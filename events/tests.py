from django.test import TestCase
from django.urls import reverse


class HomeRegistrationLinkTests(TestCase):
    def test_home_links_registration_buttons_to_correct_flows(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Event planner registration')
        self.assertContains(response, 'href="/accounts/register/"')
        self.assertContains(response, 'Vendor registration')
        self.assertContains(response, 'href="/vendors/register/"')
        self.assertContains(response, 'Join event')