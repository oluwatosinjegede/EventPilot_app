# Generated manually for signed QR access cards.
import secrets
import access.models
from django.db import migrations, models


def generate_pass_id():
    return f'PASS-{secrets.token_hex(8).upper()}'


def populate_cards(apps, schema_editor):
    DigitalAccessCard = apps.get_model('access', 'DigitalAccessCard')
    for card in DigitalAccessCard.objects.all():
        card.access_pass_id = generate_pass_id()
        card.qr_token = card.access_code
        card.generated_at = card.created_at
        card.save(update_fields=['access_pass_id','qr_token','generated_at'])


class Migration(migrations.Migration):
    dependencies = [('access','0001_initial'), ('guests','0002_invitation_rsvp_menu_seat_pass_fields')]
    operations = [
        migrations.AddField('digitalaccesscard', 'access_pass_id', models.CharField(default=access.models.generate_pass_id, max_length=40, null=True)),
        migrations.AddField('digitalaccesscard', 'qr_token', models.TextField(blank=True, null=True)),
        migrations.AddField('digitalaccesscard', 'card_file', models.FileField(blank=True, upload_to='access_cards/')),
        migrations.AddField('digitalaccesscard', 'revoked_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('digitalaccesscard', 'expires_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('digitalaccesscard', 'generated_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('digitalaccesscard', 'updated_at', models.DateTimeField(auto_now=True)),
        migrations.RunPython(populate_cards, migrations.RunPython.noop),
        migrations.AlterField('digitalaccesscard', 'access_pass_id', models.CharField(default=access.models.generate_pass_id, max_length=40, unique=True)),
        migrations.AlterField('digitalaccesscard', 'qr_token', models.TextField(blank=True, unique=True)),
    ]
