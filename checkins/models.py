from django.conf import settings
from django.db import models

class CheckInLog(models.Model):
    RESULT_CHOICES=[('valid','Valid — checked in successfully'),('already_checked_in','Already checked in'),('invalid_code','Invalid code'),('wrong_event','Wrong event'),('guest_not_confirmed','Guest not confirmed'),('access_revoked','Access revoked')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='checkin_logs')
    guest = models.ForeignKey('guests.Guest', null=True, blank=True, on_delete=models.SET_NULL)
    access_card = models.ForeignKey('access.DigitalAccessCard', null=True, blank=True, on_delete=models.SET_NULL)
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    code_entered = models.CharField(max_length=120)
    result = models.CharField(max_length=40, choices=RESULT_CHOICES)
    message = models.CharField(max_length=240)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']