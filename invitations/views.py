import json
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from access.models import DigitalAccessCard
from events.views import notify_vendors
from guests.models import Guest
from preferences.models import GuestPreference
from .forms import RSVPForm
from .models import GuestInvitation
from .services import InvitationFlowError, confirm_guest_flow, send_guest_invitation


def _json_body(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return {}
    return request.POST


def invite_rsvp(request, token):
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = f'invite-rate:{ip}'
    attempts = cache.get(key, 0)
    if attempts > 120:
        return HttpResponse('Too many requests. Please wait and try again.', status=429)
    cache.set(key, attempts + 1, 60)
    invitation=get_object_or_404(GuestInvitation.objects.select_related('guest__event'), token=token)
    guest=invitation.guest
    event=guest.event
    if invitation.is_expired:
        guest.invite_status='expired'; guest.save(update_fields=['invite_status'])
        return render(request,'invitations/expired.html', {'guest':guest})
    if not invitation.opened_at:
        now=timezone.now()
        invitation.opened_at=now; invitation.save(update_fields=['opened_at'])
        guest.invitation_opened_at=now
        if guest.invite_status == 'sent': guest.invite_status='opened'
        guest.save(update_fields=['invite_status','invitation_opened_at'])
    form=RSVPForm(request.POST or None, event=event, guest=guest)
    available_seats=[seat for seat in event.seat_choices() if seat == guest.seat_assignment or not event.guests.filter(seat_assignment=seat).exclude(pk=guest.pk).exists()]
    if request.method=='POST' and form.is_valid():
        try:
            guest, card = confirm_guest_flow(
                guest,
                form.cleaned_data['rsvp_status'],
                form.cleaned_data.get('menu_choice',''),
                form.cleaned_data.get('seat_assignment',''),
                request,
            )
        except InvitationFlowError as exc:
            form.add_error(None, str(exc))
        else:
            pref,_=GuestPreference.objects.get_or_create(guest=guest)
            pref.menu_choice=guest.selected_menu_choice
            pref.seat_choice=guest.seat_assignment
            pref.dietary_restrictions=form.cleaned_data.get('dietary_restrictions','')
            pref.save(update_fields=['menu_choice','seat_choice','dietary_restrictions','updated_at'])
            if guest.rsvp_status=='attending':
                notify_vendors(guest.event, guest, 'confirmed')
                messages.success(request,'RSVP confirmed. Your access card has been sent by email and WhatsApp.')
                return redirect('access_card', card.access_code)
            messages.success(request,'Thank you. Your RSVP has been recorded.')
            return render(request,'invitations/thanks.html', {'guest':guest})
    return render(request,'invitations/rsvp.html', {'invitation':invitation,'guest':guest,'event':event,'form':form,'available_seats':available_seats})


def api_invite_details(request, token):
    invitation=get_object_or_404(GuestInvitation.objects.select_related('guest__event'), token=token)
    guest=invitation.guest; event=guest.event
    return JsonResponse({
        'guest': {'name': guest.full_name, 'rsvp_status': guest.rsvp_status, 'menu_choice': guest.selected_menu_choice, 'seat_assignment': guest.seat_assignment},
        'event': {'name': event.title, 'starts_at': event.start_at.isoformat(), 'venue': event.venue_name, 'location': event.venue_address, 'menu_options': event.menu_choices(), 'seat_options': event.seat_choices()},
    })


def api_submit_rsvp(request, token):
    invitation=get_object_or_404(GuestInvitation.objects.select_related('guest__event'), token=token)
    data=_json_body(request)
    try:
        guest, card=confirm_guest_flow(invitation.guest, data.get('rsvp_status'), data.get('menu_choice',''), data.get('seat_assignment',''), request)
    except InvitationFlowError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return JsonResponse({'rsvp_status': guest.rsvp_status, 'menu_choice': guest.selected_menu_choice, 'seat_assignment': guest.seat_assignment, 'access_card_url': request.build_absolute_uri(reverse('access_card', args=[card.access_code])) if card else ''})


def api_menu_selection(request, token):
    invitation=get_object_or_404(GuestInvitation.objects.select_related('guest__event'), token=token)
    data=_json_body(request)
    try:
        guest, card=confirm_guest_flow(invitation.guest, 'attending', data.get('menu_choice',''), invitation.guest.seat_assignment, request)
    except InvitationFlowError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return JsonResponse({'menu_choice': guest.selected_menu_choice, 'access_card_generated': bool(card)})


def api_seat_selection(request, token):
    invitation=get_object_or_404(GuestInvitation.objects.select_related('guest__event'), token=token)
    data=_json_body(request)
    try:
        guest, card=confirm_guest_flow(invitation.guest, 'attending', invitation.guest.selected_menu_choice, data.get('seat_assignment',''), request)
    except InvitationFlowError as exc:
        return JsonResponse({'error': str(exc)}, status=409 if 'seat' in str(exc).lower() else 400)
    return JsonResponse({'seat_assignment': guest.seat_assignment, 'access_card_generated': bool(card)})


def api_send_invites(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    guests=Guest.objects.filter(event_id=event_id)
    sent=[send_guest_invitation(guest, request).guest_id for guest in guests]
    return JsonResponse({'sent_count': len(sent), 'guest_ids': sent})


def api_resend_access_card(request, guest_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    guest=get_object_or_404(Guest.objects.select_related('event'), pk=guest_id)
    card=get_object_or_404(DigitalAccessCard, guest=guest)
    from .services import deliver_access_card
    deliver_access_card(guest, card, request)
    return JsonResponse({'email_status': guest.pass_delivery_email_status, 'whatsapp_status': guest.pass_delivery_whatsapp_status})
