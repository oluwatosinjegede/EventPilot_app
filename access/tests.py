import json
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from events.models import Event
from guests.models import Guest
from invitations.services import confirm_guest_flow
from organizations.models import Organization


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AccessCardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('owner2@example.com', password='pw')
        self.org = Organization.objects.create(name='Org2', slug='org2', created_by=self.user)
        self.event = Event.objects.create(
            organization=self.org,
            title='Summit',
            start_at=timezone.now(),
            end_at=timezone.now(),
            venue_name='Expo',
            venue_address='2 Event Way',
            menu_options=['Beef', 'Vegetarian'],
            seat_options=['B1', 'B2'],
        )
        self.guest = Guest.objects.create(event=self.event, full_name='Lin Chen', email='lin@example.com', whatsapp_phone='+15555550101')
        self.guest, self.card = confirm_guest_flow(self.guest, 'attending', 'Beef', 'B1')

    def test_check_in_endpoint_validates_signed_qr_and_prevents_duplicate(self):
        response = self.client.post(reverse('api_validate_check_in', args=[self.event.pk]), data=json.dumps({'qr_token': self.card.qr_token}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'valid')
        duplicate = self.client.post(reverse('api_validate_check_in', args=[self.event.pk]), data=json.dumps({'qr_token': self.card.qr_token}), content_type='application/json')
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(duplicate.json()['status'], 'already_checked_in')

    def test_invalid_qr_is_rejected(self):
        response = self.client.post(reverse('api_validate_check_in', args=[self.event.pk]), data=json.dumps({'qr_token': 'invalid'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'invalid_code')

    def test_expired_or_revoked_pass_is_rejected(self):
        self.card.active = False
        self.card.save(update_fields=['active'])
        response = self.client.post(reverse('api_validate_check_in', args=[self.event.pk]), data=json.dumps({'qr_token': self.card.qr_token}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'access_revoked')
