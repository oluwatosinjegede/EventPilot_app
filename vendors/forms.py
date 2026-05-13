from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from events.models import Event
from organizations.models import Organization
from .models import VendorProfile


class TailwindMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500')


class VendorRegistrationForm(TailwindMixin, UserCreationForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    company_name = forms.CharField(max_length=200, label='Company / vendor name')
    service_type = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=40, required=False)
    website = forms.URLField(required=False)
    organization_code = forms.CharField(max_length=10)
    event_code = forms.CharField(max_length=10)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('full_name', 'email', 'password1', 'password2', 'company_name', 'service_type', 'phone', 'website', 'organization_code', 'event_code')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists. Please log in instead.')
        return email

    def clean_organization_code(self):
        return self.cleaned_data['organization_code'].strip().upper()

    def clean_event_code(self):
        return self.cleaned_data['event_code'].strip().upper()

    def clean(self):
        cleaned = super().clean()
        org_code = cleaned.get('organization_code')
        event_code = cleaned.get('event_code')
        if not org_code or not event_code:
            return cleaned
        organization = Organization.objects.filter(organization_code=org_code).first()
        if not organization:
            self.add_error('organization_code', 'No organization found for this code.')
            return cleaned
        event = Event.objects.filter(event_code=event_code).select_related('organization').first()
        if not event:
            self.add_error('event_code', 'No event found for this code.')
            return cleaned
        if event.organization_id != organization.id:
            self.add_error('event_code', 'This event code does not belong to the organization code provided.')
            return cleaned
        cleaned['organization'] = organization
        cleaned['event'] = event
        return cleaned


class VendorProfileForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['company_name', 'service_type', 'phone', 'website']
