from django.db import models
from django.conf import settings


class ContingencyPlan(models.Model):
    CATEGORIES=[('weather','Weather'),('vendor_cancellation','Vendor cancellation'),('low_attendance','Low attendance'),('budget_overrun','Budget overrun'),('equipment_failure','Equipment failure'),('transportation_delay','Transportation delay'),('staff_shortage','Staff shortage'),('technical_issue','Technical issue'),('venue_problem','Venue problem')]
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='contingency_plans')
    risk_name = models.CharField(max_length=200)
    category = models.CharField(max_length=40, choices=CATEGORIES)
    probability = models.PositiveSmallIntegerField(default=1)
    impact = models.PositiveSmallIntegerField(default=1)
    backup_plan = models.TextField()
    trigger_point = models.CharField(max_length=200, blank=True)
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=40, default='open')