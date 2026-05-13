from django.db import models

class Guest(models.Model):
    INVITE_CHOICES=[('draft','Draft'),('queued','Queued'),('sent','Sent'),('opened','Opened'),('confirmed','Confirmed'),('declined','Declined'),('expired','Expired'),('checked_in','Checked in')]
    RSVP_CHOICES=[('pending','Pending'),('attending','Attending'),('declining','Declining'),('maybe','Maybe')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='guests')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    group_name = models.CharField(max_length=120, blank=True)
    access_type = models.CharField(max_length=80, default='General')
    invite_status = models.CharField(max_length=30, choices=INVITE_CHOICES, default='draft')
    rsvp_status = models.CharField(max_length=30, choices=RSVP_CHOICES, default='pending')
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['full_name']
    def __str__(self): return self.full_name
