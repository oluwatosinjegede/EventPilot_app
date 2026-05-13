from django.db import models

class VendorNotificationRule(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='notification_rules')
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='notification_rules')
    notify_on_guest_confirmed = models.BooleanField(default=False)
    notify_on_guest_arrived = models.BooleanField(default=False)
    include_menu = models.BooleanField(default=False)
    include_seat = models.BooleanField(default=False)
    include_drinks = models.BooleanField(default=False)
    include_gift = models.BooleanField(default=False)
    include_custom_answers = models.BooleanField(default=False)
    def __str__(self): return f'{self.vendor} notifications'

class NotificationLog(models.Model):
    CHANNEL_CHOICES=[('email','Email'),('dashboard','Dashboard')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='notification_logs')
    vendor = models.ForeignKey('vendors.Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    guest = models.ForeignKey('guests.Guest', null=True, blank=True, on_delete=models.SET_NULL)
    rule = models.ForeignKey(VendorNotificationRule, null=True, blank=True, on_delete=models.SET_NULL)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='email')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
