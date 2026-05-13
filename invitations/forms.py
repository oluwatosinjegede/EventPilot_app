from django import forms
from preferences.models import GuestPreference
class RSVPForm(forms.ModelForm):
    rsvp_status=forms.ChoiceField(choices=[('attending','Attending'),('declining','Declining'),('maybe','Maybe')], widget=forms.RadioSelect)
    class Meta:
        model=GuestPreference
        fields=['menu_choice','side_choice','dessert_choice','dietary_restrictions','allergies','seat_choice','table_number','seat_me_with','accessibility_needs','drink_choice','gift_status','gift_note']