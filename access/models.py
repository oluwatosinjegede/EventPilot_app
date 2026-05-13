import secrets
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.signing import TimestampSigner
from django.db import models
from django.urls import reverse
from django.utils import timezone


def generate_access_code():
    return secrets.token_urlsafe(18)


def generate_pass_id():
    return f'PASS-{secrets.token_hex(8).upper()}'


class DigitalAccessCard(models.Model):
    guest = models.OneToOneField('guests.Guest', on_delete=models.CASCADE, related_name='access_card')
    access_code = models.CharField(max_length=48, unique=True, default=generate_access_code)
    access_pass_id = models.CharField(max_length=40, unique=True, default=generate_pass_id)
    qr_token = models.TextField(blank=True, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    card_file = models.FileField(upload_to='access_cards/', blank=True)
    active = models.BooleanField(default=True)
    confirmation_status = models.CharField(max_length=40, default='confirmed')
    revoked_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def signed_payload(self):
        guest = self.guest
        event = guest.event
        value = f'{event.public_id}:{guest.public_id}:{self.access_pass_id}:{self.access_code}'
        return TimestampSigner(salt='event-access-card').sign(value)

    def build_absolute_card_url(self, request=None):
        path = reverse('access_card', args=[self.access_code])
        return request.build_absolute_uri(path) if request else path

    def render_card_document(self):
        guest = self.guest
        event = guest.event
        return (
            f'EventPilot Access Card\n\n'
            f'Pass ID: {self.access_pass_id}\n'
            f'Guest: {guest.full_name}\n'
            f'Event: {event.title}\n'
            f'Date/time: {event.start_at}\n'
            f'Venue: {event.venue_name or "Venue TBD"}\n'
            f'Location: {event.venue_address}\n'
            f'Seat: {guest.seat_assignment or "TBD"}\n'
            f'Menu: {guest.selected_menu_choice or "TBD"}\n'
            f'QR token: {self.qr_token}\n'
        )

    def save(self,*args,**kwargs):
        if not self.qr_token:
            self.qr_token = self.signed_payload()
        if not self.generated_at:
            self.generated_at = timezone.now()
        super().save(*args,**kwargs)
        updates=[]
        if not self.qr_code:
            import qrcode
            img = qrcode.make(self.qr_token)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            self.qr_code.save(f'{self.access_pass_id}.png', ContentFile(buffer.getvalue()), save=False)
            updates.append('qr_code')
        if not self.card_file:
            self.card_file.save(f'{self.access_pass_id}.txt', ContentFile(self.render_card_document().encode('utf-8')), save=False)
            updates.append('card_file')
        if updates:
            super().save(update_fields=updates)

    def __str__(self): return self.access_pass_id
