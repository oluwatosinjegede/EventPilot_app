# Generated manually for invitation/RSVP refactor.
import secrets
import uuid
import guests.models
from django.db import migrations, models
from django.db.models import Q


def generate_invitation_token():
    return secrets.token_urlsafe(32)


def populate_guest_tokens(apps, schema_editor):
    Guest = apps.get_model('guests', 'Guest')
    for guest in Guest.objects.all():
        guest.public_id = uuid.uuid4()
        guest.invitation_token = secrets.token_urlsafe(32)
        guest.save(update_fields=['public_id', 'invitation_token'])


class Migration(migrations.Migration):
    dependencies = [('events', '0006_event_guest_flow_configuration'), ('guests', '0001_initial')]
    operations = [
        migrations.AlterField('guest', 'phone', models.CharField(blank=True, help_text='WhatsApp-capable phone number', max_length=40)),
        migrations.AddField('guest', 'public_id', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
        migrations.AddField('guest', 'whatsapp_phone', models.CharField(blank=True, help_text='Optional WhatsApp number if different from phone', max_length=40)),
        migrations.AddField('guest', 'invitation_token', models.CharField(default=guests.models.generate_invitation_token, editable=False, max_length=96, null=True)),
        migrations.AddField('guest', 'email_invite_status', models.CharField(choices=[('pending','Pending'),('queued','Queued'),('sent','Sent'),('failed','Failed'),('delivered','Delivered')], default='pending', max_length=30)),
        migrations.AddField('guest', 'whatsapp_invite_status', models.CharField(choices=[('pending','Pending'),('queued','Queued'),('sent','Sent'),('failed','Failed'),('delivered','Delivered')], default='pending', max_length=30)),
        migrations.AddField('guest', 'rsvp_submitted_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('guest', 'selected_menu_choice', models.CharField(blank=True, max_length=120)),
        migrations.AddField('guest', 'seat_assignment', models.CharField(blank=True, max_length=80)),
        migrations.AddField('guest', 'invitation_sent_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('guest', 'invitation_opened_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('guest', 'rsvp_updated_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('guest', 'pass_delivery_email_status', models.CharField(choices=[('pending','Pending'),('sent','Sent'),('failed','Failed')], default='pending', max_length=30)),
        migrations.AddField('guest', 'pass_delivery_whatsapp_status', models.CharField(choices=[('pending','Pending'),('sent','Sent'),('failed','Failed')], default='pending', max_length=30)),
        migrations.AddField('guest', 'updated_at', models.DateTimeField(auto_now=True)),
        migrations.RunPython(populate_guest_tokens, migrations.RunPython.noop),
        migrations.AlterField('guest', 'public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
        migrations.AlterField('guest', 'invitation_token', models.CharField(default=guests.models.generate_invitation_token, editable=False, max_length=96, unique=True)),
        migrations.AddConstraint('guest', models.UniqueConstraint(fields=('event','seat_assignment'), condition=~Q(seat_assignment=''), name='unique_assigned_seat_per_event')),
    ]
