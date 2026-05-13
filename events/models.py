import uuid
from django.db import models
from django.urls import reverse
from event_codes import generate_unique_code

class Event(models.Model):
    PLANNING='planning'; ACTIVE='active'; COMPLETED='completed'; CANCELLED='cancelled'
    STATUS_CHOICES=[(PLANNING,'Planning'),(ACTIVE,'Active'),(COMPLETED,'Completed'),(CANCELLED,'Cancelled')]
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='events')
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    event_code = models.CharField(max_length=10, unique=True, db_index=True, editable=False, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=100, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    venue_name = models.CharField(max_length=200, blank=True)
    venue_address = models.TextField(blank=True)
    online_url = models.URLField(blank=True)
    menu_options = models.JSONField(default=list, blank=True, help_text='Configured menu choices shown to guests')
    seat_options = models.JSONField(default=list, blank=True, help_text='Configured seat labels shown to guests')
    expected_guest_count = models.PositiveIntegerField(default=0)
    budget_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PLANNING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_at']

    def save(self, *args, **kwargs):
        if not self.event_code:
            self.event_code = generate_unique_code(Event, 'event_code', 'EVT')
        super().save(*args, **kwargs)

    def menu_choices(self):
        return [str(option).strip() for option in (self.menu_options or []) if str(option).strip()]

    def seat_choices(self):
        return [str(seat).strip() for seat in (self.seat_options or []) if str(seat).strip()]

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('event_detail', args=[self.pk])
