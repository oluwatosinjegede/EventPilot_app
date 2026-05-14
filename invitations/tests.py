import json
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from events.models import Event
from guests.models import Guest
from invitations.models import GuestInvitation
from invitations.services import InvitationFlowError, assign_rsvp_details, send_guest_invitation
from organizations.models import Organization


class TimeoutEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise TimeoutError('SMTP server did not respond')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class InvitationFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('owner@example.com', password='pw')
        self.org = Organization.objects.create(name='Org', slug='org', created_by=self.user)
        self.event = Event.objects.create(
            organization=self.org,
            title='Gala',
            start_at=timezone.now(),
            end_at=timezone.now(),
            venue_name='Main Hall',
            venue_address='1 Event Way',
            menu_options=['Chicken', 'Vegan'],
            seat_options=['A1', 'A2'],
        )
        self.guest = Guest.objects.create(event=self.event, full_name='Ada Lovelace', email='ada@example.com', whatsapp_phone='+15555550100')

    def test_email_and_whatsapp_invites_have_unique_token_and_status(self):
        invitation = send_guest_invitation(self.guest)
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.email_invite_status, 'sent')
        self.assertEqual(self.guest.whatsapp_invite_status, 'sent')
        self.assertEqual(invitation.token, self.guest.invitation_token)
        self.assertIn(self.guest.invitation_token, mail.outbox[0].body)

    @override_settings(EMAIL_BACKEND='invitations.tests.TimeoutEmailBackend')
    def test_invitation_email_timeout_marks_email_failed(self):
        invitation = send_guest_invitation(self.guest)
        self.guest.refresh_from_db()
        invitation.refresh_from_db()
        self.assertEqual(self.guest.email_invite_status, 'failed')
        self.assertEqual(self.guest.whatsapp_invite_status, 'sent')
        self.assertIsNone(invitation.email_sent_at)


    def test_invite_details_invalid_token_returns_404(self):
        response = self.client.get(reverse('api_invite_details', args=['not-a-token']))
        self.assertEqual(response.status_code, 404)

    def test_rsvp_submission_generates_card_and_delivers_it(self):
        invitation = GuestInvitation.objects.create(guest=self.guest)
        response = self.client.post(reverse('api_submit_rsvp', args=[invitation.token]), data=json.dumps({
            'rsvp_status': 'attending',
            'menu_choice': 'Vegan',
            'seat_assignment': 'A1',
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.rsvp_status, 'attending')
        self.assertEqual(self.guest.selected_menu_choice, 'Vegan')
        self.assertEqual(self.guest.seat_assignment, 'A1')
        self.assertTrue(hasattr(self.guest, 'access_card'))
        self.assertEqual(self.guest.pass_delivery_email_status, 'sent')
        self.assertEqual(self.guest.pass_delivery_whatsapp_status, 'sent')
        self.assertTrue(self.guest.access_card.qr_token)
        self.assertTrue(self.guest.access_card.qr_code.name)
        self.assertTrue(self.guest.access_card.card_file.name)

    def test_invalid_menu_choice_is_rejected(self):
        with self.assertRaisesMessage(InvitationFlowError, 'Invalid menu choice'):
            assign_rsvp_details(self.guest, 'attending', 'Fish', 'A1')

    def test_duplicate_submission_same_guest_can_update_seat(self):
        first = assign_rsvp_details(self.guest, 'attending', 'Chicken', 'A1')
        second = assign_rsvp_details(first, 'attending', 'Chicken', 'A2')
        self.assertEqual(second.seat_assignment, 'A2')

    def test_seat_conflict_prevention(self):
        assign_rsvp_details(self.guest, 'attending', 'Chicken', 'A1')
        other = Guest.objects.create(event=self.event, full_name='Grace Hopper', email='grace@example.com')
        with self.assertRaisesMessage(InvitationFlowError, 'seat is no longer available'):
            assign_rsvp_details(other, 'attending', 'Vegan', 'A1')

    def test_seat_endpoint_reports_unavailable_seat(self):
        assign_rsvp_details(self.guest, 'attending', 'Chicken', 'A1')
        other = Guest.objects.create(event=self.event, full_name='Grace Hopper', email='grace@example.com', selected_menu_choice='Vegan')
        invitation = GuestInvitation.objects.create(guest=other)
        response = self.client.post(reverse('api_seat_selection', args=[invitation.token]), data=json.dumps({'seat_assignment': 'A1'}), content_type='application/json')
        self.assertEqual(response.status_code, 409)
        self.assertIn('seat', response.json()['error'].lower())