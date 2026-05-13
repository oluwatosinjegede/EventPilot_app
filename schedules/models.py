from django.conf import settings
from django.db import models
class ScheduleItem(models.Model):
    AUDIENCE_CHOICES=[('internal','Internal organizer'),('public','Public guest'),('staff','Staff only')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='schedule_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=160, blank=True)
    audience_visibility = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='internal')
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: ordering=['start_time']