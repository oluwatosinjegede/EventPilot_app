from django.db import models

class GuestPreference(models.Model):
    guest = models.OneToOneField('guests.Guest', on_delete=models.CASCADE, related_name='preference')
    menu_choice = models.CharField(max_length=120, blank=True)
    side_choice = models.CharField(max_length=120, blank=True)
    dessert_choice = models.CharField(max_length=120, blank=True)
    dietary_restrictions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    seat_choice = models.CharField(max_length=80, blank=True)
    table_number = models.CharField(max_length=40, blank=True)
    seat_me_with = models.CharField(max_length=200, blank=True)
    accessibility_needs = models.TextField(blank=True)
    drink_choice = models.CharField(max_length=120, blank=True)
    gift_status = models.CharField(max_length=120, blank=True)
    gift_note = models.TextField(blank=True)
    custom_answers = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
