from django.db import models
class LogisticsPlan(models.Model):
    event = models.OneToOneField('events.Event', on_delete=models.CASCADE, related_name='logistics_plan')
    venue_layout_notes = models.TextField(blank=True)
    equipment_checklist = models.TextField(blank=True)
    supply_inventory = models.TextField(blank=True)
    transportation_plan = models.TextField(blank=True)
    parking_notes = models.TextField(blank=True)
    setup_schedule = models.TextField(blank=True)
    cleanup_schedule = models.TextField(blank=True)
    room_assignments = models.TextField(blank=True)
    staff_assignments = models.TextField(blank=True)
    accessibility_notes = models.TextField(blank=True)