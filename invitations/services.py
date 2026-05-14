import logging
import signal
from contextlib import contextmanager

from django.conf import settings

from django.core.mail import EmailMessage, send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from access.models import DigitalAccessCard
from checkins.models import CheckInLog
from guests.models import Guest
from .models import GuestInvitation

VALID_RSVP_STATUSES = {'attending', 'declining', 'maybe'}
QR_MAX_AGE_SECONDS = 60 * 60 * 24 * 370
logger = logging.getLogger(__name__)

@contextmanager
def email_send_timeout():
    """Raise TimeoutError if a mail backend blocks longer than configured."""
    timeout = getattr(settings, 'INVITATION_EMAIL_SEND_TIMEOUT', None)
    if timeout is None:
        timeout = getattr(settings, 'EMAIL_TIMEOUT', 5)
    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        timeout = 5.0
    if timeout <= 0 or not hasattr(signal, 'SIGALRM'):
        yield
        return

    def _handle_timeout(signum, frame):
        raise TimeoutError('Invitation email send timed out')

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)


class InvitationFlowError(ValueError):
    pass


def invite_url_for_guest(request, invitation):
    path = reverse('invite_rsvp', args=[invitation.token])
    return request.build_absolute_uri(path) if request else path


def send_whatsapp_message(phone_number, body):
    """Placeholder integration point for a WhatsApp provider."""
    return bool(phone_number and body)

def _send_mail(subject, body, recipient):
    try:
        with email_send_timeout():
            return send_mail(subject, body, None, [recipient], fail_silently=True) > 0
    except Exception as exc:
        logger.warning(
            'Failed to send invitation email to guest recipient: %s',
            exc,
        )
        return False


def _send_email_message(message):
    try:
        with email_send_timeout():
            return message.send(fail_silently=True) > 0
    except Exception as exc:
        logger.warning(
            'Failed to send access card email to guest recipient: %s',
            exc,
        )
        return False

def send_guest_invitation(guest, request=None):
    invitation, _ = GuestInvitation.objects.get_or_create(guest=guest)
    if invitation.token != guest.invitation_token:
        invitation.token = guest.invitation_token
    url = invite_url_for_guest(request, invitation)
    now = timezone.now()
    subject = f'Invitation to {guest.event.title}'
    body = f'Hello {guest.full_name}, RSVP here: {url}'

    if guest.email and _send_mail(subject, body, guest.email):
        guest.email_invite_status = 'sent'
        invitation.email_sent_at = now
    else:
        guest.email_invite_status = 'failed'

    if send_whatsapp_message(guest.whatsapp_number, body):
        guest.whatsapp_invite_status = 'sent'
        invitation.whatsapp_sent_at = now
    else:
        guest.whatsapp_invite_status = 'failed'

    invitation.sent_at = now
    invitation.resend_count += 1
    invitation.save(update_fields=['token','sent_at','email_sent_at','whatsapp_sent_at','resend_count','expires_at'])
    guest.invite_status = 'sent'
    guest.invitation_sent_at = now
    guest.save(update_fields=['email_invite_status','whatsapp_invite_status','invite_status','invitation_sent_at','updated_at'])
    return invitation


def validate_menu_choice(event, menu_choice):
    choices = event.menu_choices()
    if not choices:
        raise InvitationFlowError('This event does not have menu options configured.')
    if menu_choice not in choices:
        raise InvitationFlowError('Invalid menu choice.')


def validate_seat_choice(event, seat_assignment):
    seats = event.seat_choices()
    if not seats:
        raise InvitationFlowError('This event does not have seats configured.')
    if seat_assignment not in seats:
        raise InvitationFlowError('Invalid seat selection.')


def assign_rsvp_details(guest, rsvp_status, menu_choice='', seat_assignment=''):
    if rsvp_status not in VALID_RSVP_STATUSES:
        raise InvitationFlowError('Invalid RSVP status.')
    with transaction.atomic():
        locked_guest = Guest.objects.select_for_update().select_related('event').get(pk=guest.pk)
        event = locked_guest.event
        locked_guest.mark_rsvp(rsvp_status)
        if rsvp_status == 'attending':
            validate_menu_choice(event, menu_choice)
            validate_seat_choice(event, seat_assignment)
            conflict = Guest.objects.select_for_update().filter(
                event=event, seat_assignment=seat_assignment
            ).exclude(pk=locked_guest.pk).exists()
            if conflict:
                raise InvitationFlowError('That seat is no longer available. Please choose another seat.')
            locked_guest.selected_menu_choice = menu_choice
            locked_guest.seat_assignment = seat_assignment
            locked_guest.invite_status = 'confirmed'
        elif rsvp_status == 'declining':
            locked_guest.selected_menu_choice = ''
            locked_guest.seat_assignment = ''
            locked_guest.invite_status = 'declined'
        else:
            locked_guest.selected_menu_choice = menu_choice if menu_choice in event.menu_choices() else ''
            locked_guest.seat_assignment = ''
            locked_guest.invite_status = 'opened'
        try:
            locked_guest.save(update_fields=[
                'rsvp_status','rsvp_submitted_at','rsvp_updated_at','selected_menu_choice',
                'seat_assignment','invite_status','updated_at'
            ])
        except IntegrityError as exc:
            raise InvitationFlowError('That seat is no longer available. Please choose another seat.') from exc
        return locked_guest


def generate_access_card_for_guest(guest):
    if guest.rsvp_status != 'attending':
        raise InvitationFlowError('Access cards can only be generated for attending guests.')
    card, _ = DigitalAccessCard.objects.get_or_create(guest=guest)
    return card


def deliver_access_card(guest, card, request=None):
    card_url = card.build_absolute_card_url(request)
    body = (
        f'Your access card for {guest.event.title} is ready.\n'
        f'Pass ID: {card.access_pass_id}\n'
        f'Seat: {guest.seat_assignment}\n'
        f'Menu: {guest.selected_menu_choice}\n'
        f'Download: {card_url}'
    )
    if guest.email:
        msg = EmailMessage(f'Your access card for {guest.event.title}', body, None, [guest.email])
        attachments = []
        if card.qr_code:
            attachments.append(card.qr_code.path)
        if card.card_file:
            attachments.append(card.card_file.path)
        for path in attachments:
            try:
                msg.attach_file(path)
            except FileNotFoundError:
                pass
        if _send_email_message(msg):
            guest.pass_delivery_email_status = 'sent'
        else:
            guest.pass_delivery_email_status = 'failed'
    else:
        guest.pass_delivery_email_status = 'failed'

    if send_whatsapp_message(guest.whatsapp_number, body):
        guest.pass_delivery_whatsapp_status = 'sent'
    else:
        guest.pass_delivery_whatsapp_status = 'failed'
    guest.save(update_fields=['pass_delivery_email_status','pass_delivery_whatsapp_status','updated_at'])


def confirm_guest_flow(guest, rsvp_status, menu_choice='', seat_assignment='', request=None):
    guest = assign_rsvp_details(guest, rsvp_status, menu_choice, seat_assignment)
    card = None
    if guest.rsvp_status == 'attending':
        card = generate_access_card_for_guest(guest)
        deliver_access_card(guest, card, request)
    return guest, card


def validate_qr_token(qr_token, event, scanned_by=None):
    signer = TimestampSigner(salt='event-access-card')
    card = None
    guest = None
    try:
        value = signer.unsign(qr_token, max_age=QR_MAX_AGE_SECONDS)
        event_public_id, guest_public_id, pass_id, access_code = value.split(':', 3)
        card = DigitalAccessCard.objects.select_related('guest__event').get(
            access_pass_id=pass_id,
            access_code=access_code,
            guest__public_id=guest_public_id,
            guest__event__public_id=event_public_id,
        )
        guest = card.guest
        if guest.event_id != event.id:
            status, message = 'wrong_event', 'Wrong event'
        elif not card.active or card.revoked_at:
            status, message = 'access_revoked', 'Invalid or expired pass'
        elif card.expires_at and timezone.now() > card.expires_at:
            status, message = 'access_revoked', 'Invalid or expired pass'
        elif guest.rsvp_status != 'attending':
            status, message = 'guest_not_confirmed', 'Guest not confirmed'
        elif guest.checked_in:
            status, message = 'already_checked_in', 'Already checked in'
        else:
            guest.checked_in = True
            guest.checked_in_at = timezone.now()
            guest.invite_status = 'checked_in'
            guest.save(update_fields=['checked_in','checked_in_at','invite_status','updated_at'])
            status, message = 'valid', 'Valid pass — checked in successfully'
    except (BadSignature, SignatureExpired, ValueError, DigitalAccessCard.DoesNotExist):
        status, message = 'invalid_code', 'Invalid or expired pass'
    CheckInLog.objects.create(
        event=event, guest=guest, access_card=card, scanned_by=scanned_by,
        code_entered=qr_token[:120], result=status, message=message,
    )
    return {'status': status, 'message': message, 'guest': guest, 'access_card': card}
