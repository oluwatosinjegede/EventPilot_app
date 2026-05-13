from datetime import timedelta
from django.db import models
from django.utils import timezone

class GuestInvitation(models.Model):
    guest = models.OneToOneField('guests.Guest', on_delete=models.CASCADE, related_name='invitation')
    token = models.CharField(max_length=96, unique=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    whatsapp_sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    resend_count = models.PositiveIntegerField(default=0)
    def save(self,*args,**kwargs):
        if not self.token:
            self.token = self.guest.invitation_token
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args,**kwargs)
    @property
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at
    def __str__(self): return f'Invitation for {self.guest}'