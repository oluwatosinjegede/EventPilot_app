from django.db import migrations, models


def copy_guest_tokens(apps, schema_editor):
    GuestInvitation = apps.get_model('invitations', 'GuestInvitation')
    for invitation in GuestInvitation.objects.select_related('guest'):
        invitation.token = invitation.guest.invitation_token
        invitation.save(update_fields=['token'])


class Migration(migrations.Migration):
    dependencies = [('guests','0002_invitation_rsvp_menu_seat_pass_fields'), ('invitations','0001_initial')]
    operations = [
        migrations.AlterField('guestinvitation','token', models.CharField(blank=True, max_length=96, unique=True)),
        migrations.AddField('guestinvitation','email_sent_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('guestinvitation','whatsapp_sent_at', models.DateTimeField(blank=True, null=True)),
        migrations.RunPython(copy_guest_tokens, migrations.RunPython.noop),
    ]
