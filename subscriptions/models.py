from django.db import models
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=80)
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_events = models.PositiveIntegerField(default=1)
    max_guests = models.PositiveIntegerField(default=100)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name