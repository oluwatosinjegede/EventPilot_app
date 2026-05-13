from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from access.models import DigitalAccessCard
from events.views import notify_vendors
from guests.models import Guest
from preferences.models import GuestPreference
from .forms import RSVPForm
from .models import GuestInvitation

def invite_rsvp(request, token):
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = f'invite-rate:{ip}'
    attempts = cache.get(key, 0)
    if attempts > 120:
        return HttpResponse('Too many requests. Please wait and try again.', status=429)
    cache.set(key, attempts + 1, 60)
    invitation=get_object_or_404(GuestInvitation.objects.select_related('guest__event'), token=token)
    guest=invitation.guest
    if invitation.is_expired:
        guest.invite_status='expired'; guest.save(update_fields=['invite_status'])
        return render(request,'invitations/expired.html', {'guest':guest})
    if not invitation.opened_at:
        invitation.opened_at=timezone.now(); invitation.save(update_fields=['opened_at'])
        if guest.invite_status == 'sent': guest.invite_status='opened'; guest.save(update_fields=['invite_status'])
    pref,_=GuestPreference.objects.get_or_create(guest=guest)
    form=RSVPForm(request.POST or None, instance=pref)
    if request.method=='POST' and form.is_valid():
        pref=form.save(); guest.rsvp_status=form.cleaned_data['rsvp_status']
        if guest.rsvp_status=='attending':
            guest.invite_status='confirmed'; guest.save(update_fields=['rsvp_status','invite_status'])
            card,_=DigitalAccessCard.objects.get_or_create(guest=guest)
            url=request.build_absolute_uri(reverse('access_card', args=[card.access_code]))
            if guest.email: send_mail(f'Your access card for {guest.event.title}', f'Your digital access card: {url}', None, [guest.email])
            notify_vendors(guest.event, guest, 'confirmed')
            messages.success(request,'RSVP confirmed. Your access card is ready.')
            return redirect('access_card', card.access_code)
        elif guest.rsvp_status=='declining': guest.invite_status='declined'
        else: guest.invite_status='opened'
        guest.save(update_fields=['rsvp_status','invite_status'])
        messages.success(request,'Thank you. Your RSVP has been recorded.')
        return render(request,'invitations/thanks.html', {'guest':guest})
    return render(request,'invitations/rsvp.html', {'invitation':invitation,'guest':guest,'form':form})
