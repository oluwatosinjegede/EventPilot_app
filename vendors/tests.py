from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from django.urls import reverse
from django.utils import timezone

from events.models import Event
from events.views import notify_vendors
from guests.models import Guest
from notifications.models import NotificationLog, VendorNotificationRule
from organizations.models import Membership, Organization
from vendors.models import Vendor, VendorProfile


class VendorSelfRegistrationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='StrongPass123')
        self.organization = Organization.objects.create(name='Acme Events', slug='acme', created_by=self.owner)
        Membership.objects.create(organization=self.organization, user=self.owner, role=Membership.OWNER)
        self.event = Event.objects.create(
            organization=self.organization,
            title='Spring Gala',
            start_at=timezone.now(),
            end_at=timezone.now() + timedelta(hours=4),
        )

    def vendor_payload(self, **overrides):
        data = {
            'full_name': 'Vendor Person',
            'email': 'vendor@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
            'company_name': 'Premier AV',
            'service_type': 'Audio visual',
            'phone': '555-0100',
            'website': 'https://vendor.example.com',
            'organization_code': self.organization.organization_code,
            'event_code': self.event.event_code,
        }
        data.update(overrides)
        return data

    def test_codes_are_generated(self):
        self.assertRegex(self.organization.organization_code, r'^ORG-[A-Z2-9]{6}$')
        self.assertRegex(self.event.event_code, r'^EVT-[A-Z2-9]{6}$')

    def test_vendor_can_register_with_matching_codes(self):
        response = self.client.post(reverse('vendor_register'), self.vendor_payload())
        self.assertRedirects(response, reverse('vendor_dashboard'))
        user = User.objects.get(email='vendor@example.com')
        vendor = Vendor.objects.get(event=self.event, email='vendor@example.com')
        profile = VendorProfile.objects.get(user=user, event=self.event)
        self.assertEqual(vendor.user, user)
        self.assertEqual(profile.organization, self.organization)
        self.assertTrue(profile.approved)
        self.assertEqual(Membership.objects.get(user=user, organization=self.organization).role, Membership.VENDOR)

    def test_vendor_registration_rejects_invalid_event_code(self):
        response = self.client.post(reverse('vendor_register'), self.vendor_payload(event_code='EVT-XXXXXX'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No event found for this code')
        self.assertFalse(User.objects.filter(email='vendor@example.com').exists())

    def test_vendor_registration_rejects_mismatched_organization(self):
        other = Organization.objects.create(name='Other Org', slug='other', created_by=self.owner)
        response = self.client.post(reverse('vendor_register'), self.vendor_payload(organization_code=other.organization_code))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'does not belong')
        self.assertFalse(User.objects.filter(email='vendor@example.com').exists())

    def test_vendor_dashboard_is_limited_and_organizer_pages_are_forbidden_by_lookup(self):
        self.client.post(reverse('vendor_register'), self.vendor_payload())
        response = self.client.get(reverse('vendor_dashboard'))
        self.assertContains(response, 'Spring Gala')
        self.assertContains(response, 'Premier AV')
        self.assertEqual(self.client.get(reverse('event_detail', args=[self.event.pk])).status_code, 404)

    def test_vendor_dashboard_shows_allowed_guest_notifications(self):
        self.client.post(reverse('vendor_register'), self.vendor_payload())
        vendor = Vendor.objects.get(event=self.event, email='vendor@example.com')
        guest = Guest.objects.create(event=self.event, full_name='Guest One', rsvp_status='attending')
        VendorNotificationRule.objects.create(event=self.event, vendor=vendor, notify_on_guest_confirmed=True)
        notify_vendors(self.event, guest, 'confirmed')
        self.assertEqual(NotificationLog.objects.filter(vendor=vendor, guest=guest).count(), 1)
        response = self.client.get(reverse('vendor_dashboard'))
        self.assertContains(response, 'Guest One confirmed')
