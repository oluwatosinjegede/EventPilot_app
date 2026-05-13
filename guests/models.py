import secrets
import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone


def generate_invitation_token():
    return secrets.token_urlsafe(32)


class Guest(models.Model):
    INVITE_CHOICES=[('draft','Draft'),('queued','Queued'),('sent','Sent'),('opened','Opened'),('confirmed','Confirmed'),('declined','Declined'),('expired','Expired'),('checked_in','Checked in')]
    DELIVERY_CHOICES=[('pending','Pending'),('queued','Queued'),('sent','Sent'),('failed','Failed'),('delivered','Delivered')]
    RSVP_CHOICES=[('pending','Pending'),('attending','Attending'),('declining','Declining'),('maybe','Maybe')]
    PASS_DELIVERY_CHOICES=[('pending','Pending'),('sent','Sent'),('failed','Failed')]

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='guests')
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True, help_text='WhatsApp-capable phone number')
    whatsapp_phone = models.CharField(max_length=40, blank=True, help_text='Optional WhatsApp number if different from phone')
    group_name = models.CharField(max_length=120, blank=True)
    access_type = models.CharField(max_length=80, default='General')
    invitation_token = models.CharField(max_length=96, unique=True, default=generate_invitation_token, editable=False)
    invite_status = models.CharField(max_length=30, choices=INVITE_CHOICES, default='draft')
    email_invite_status = models.CharField(max_length=30, choices=DELIVERY_CHOICES, default='pending')
    whatsapp_invite_status = models.CharField(max_length=30, choices=DELIVERY_CHOICES, default='pending')
    rsvp_status = models.CharField(max_length=30, choices=RSVP_CHOICES, default='pending')
    rsvp_submitted_at = models.DateTimeField(null=True, blank=True)
    selected_menu_choice = models.CharField(max_length=120, blank=True)
    seat_assignment = models.CharField(max_length=80, blank=True)
    invitation_sent_at = models.DateTimeField(null=True, blank=True)
    invitation_opened_at = models.DateTimeField(null=True, blank=True)
    rsvp_updated_at = models.DateTimeField(null=True, blank=True)
    pass_delivery_email_status = models.CharField(max_length=30, choices=PASS_DELIVERY_CHOICES, default='pending')
    pass_delivery_whatsapp_status = models.CharField(max_length=30, choices=PASS_DELIVERY_CHOICES, default='pending')
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=['full_name']
        constraints=[
            models.UniqueConstraint(
                fields=['event','seat_assignment'],
                condition=~Q(seat_assignment=''),
                name='unique_assigned_seat_per_event',
            )
        ]

    @property
    def whatsapp_number(self):
        return self.whatsapp_phone or self.phone

    def mark_rsvp(self, status):
        self.rsvp_status = status
        self.rsvp_submitted_at = timezone.now()
        self.rsvp_updated_at = self.rsvp_submitted_at

    def __str__(self): return self.full_name
