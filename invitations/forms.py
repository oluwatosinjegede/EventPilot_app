from django import forms

class RSVPForm(forms.Form):
    rsvp_status=forms.ChoiceField(choices=[('attending','Attending'),('declining','Not attending'),('maybe','Maybe / undecided')], widget=forms.RadioSelect)
    menu_choice=forms.ChoiceField(required=False)
    seat_assignment=forms.ChoiceField(required=False)
    dietary_restrictions=forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3}))

    def __init__(self, *args, event=None, guest=None, **kwargs):
        super().__init__(*args, **kwargs)
        menu_choices=[('', 'Select a menu option')] + [(choice, choice) for choice in (event.menu_choices() if event else [])]
        seat_choices=[('', 'Select an available seat')] + [(seat, seat) for seat in (event.seat_choices() if event else [])]
        self.fields['menu_choice'].choices=menu_choices
        self.fields['seat_assignment'].choices=seat_choices
        if guest:
            self.fields['rsvp_status'].initial=guest.rsvp_status if guest.rsvp_status != 'pending' else 'attending'
            self.fields['menu_choice'].initial=guest.selected_menu_choice
            self.fields['seat_assignment'].initial=guest.seat_assignment

    def clean(self):
        cleaned=super().clean()
        if cleaned.get('rsvp_status') == 'attending':
            if not cleaned.get('menu_choice'):
                self.add_error('menu_choice', 'Choose a menu option to attend.')
            if not cleaned.get('seat_assignment'):
                self.add_error('seat_assignment', 'Choose a seat to attend.')
        return cleaned