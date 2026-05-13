# Generated manually for invitation/RSVP refactor.
import uuid
from django.db import migrations, models


def populate_event_public_ids(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    for event in Event.objects.all():
        event.public_id = uuid.uuid4()
        event.save(update_fields=['public_id'])


class Migration(migrations.Migration):
    dependencies = [('events', '0005_alter_event_event_code')]
    operations = [
        migrations.AddField('event', 'public_id', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
        migrations.AddField('event', 'menu_options', models.JSONField(blank=True, default=list, help_text='Configured menu choices shown to guests')),
        migrations.AddField('event', 'seat_options', models.JSONField(blank=True, default=list, help_text='Configured seat labels shown to guests')),
        migrations.RunPython(populate_event_public_ids, migrations.RunPython.noop),
        migrations.AlterField('event', 'public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
    ]
