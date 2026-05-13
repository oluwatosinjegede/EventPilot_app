from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event
from guests.models import Guest
from organizations.models import Membership, Organization
from vendors.models import Vendor, VendorProfile

class HomeRegistrationLinkTests(TestCase):
    def test_home_links_registration_buttons_to_correct_flows(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Event planner registration')
        self.assertContains(response, 'href="/accounts/register/"')
        self.assertContains(response, 'Vendor registration')
        self.assertContains(response, 'href="/vendors/register/"')
        self.assertContains(response, 'Join event')


class EventWorkspaceEndpointTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='planner', password='StrongPass123')
        self.client.force_login(self.user)

    def create_event(self, role=Membership.OWNER, title='Spring Gala'):
        organization = Organization.objects.create(
            name=f'{title} Org',
            slug=title.lower().replace(' ', '-'),
            created_by=self.user,
        )
        Membership.objects.create(organization=organization, user=self.user, role=role)
        return Event.objects.create(
            organization=organization,
            title=title,
            start_at=timezone.now(),
            end_at=timezone.now() + timedelta(hours=4),
        )

    def test_dashboard_and_event_list_render_for_empty_planner_account(self):
        for route_name in ('dashboard', 'event_list'):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'No events')

    def test_dashboard_and_event_list_render_events_with_guest_counts(self):
        event = self.create_event()
        Guest.objects.create(event=event, full_name='Guest One')
        Guest.objects.create(event=event, full_name='Guest Two')

        for route_name in ('dashboard', 'event_list'):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, event.title)

        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertContains(dashboard_response, '>2</p>')

    def test_vendor_only_membership_is_excluded_from_event_list(self):
        event = self.create_event(role=Membership.VENDOR, title='Vendor Event')

        response = self.client.get(reverse('event_list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, event.title)
        self.assertContains(response, 'No events found')

    def test_vendor_only_dashboard_redirects_to_vendor_dashboard(self):
        event = self.create_event(role=Membership.VENDOR, title='Vendor Event')
        vendor = Vendor.objects.create(
            event=event,
            user=self.user,
            vendor_name='Premier AV',
            service_type='Audio visual',
        )
        VendorProfile.objects.create(
            user=self.user,
            vendor=vendor,
            organization=event.organization,
            event=event,
            company_name='Premier AV',
            service_type='Audio visual',
            approved=True,
        )

        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(response, reverse('vendor_dashboard'))