# Generated to repair deployments where events.0002 was recorded without adding the column.

import secrets

from django.db import migrations, models

ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def code(prefix):
    return f"{prefix}-" + ''.join(secrets.choice(ALPHABET) for _ in range(6))


def column_exists(connection, table_name, column_name):
    with connection.cursor() as cursor:
        columns = connection.introspection.get_table_description(cursor, table_name)
    names = set()
    for column in columns:
        name = getattr(column, 'name', None)
        if name is None:
            name = column[0]
        names.add(name)
    return column_name in names


def ensure_event_code_column(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    table_name = Event._meta.db_table
    column_name = 'event_code'
    connection = schema_editor.connection

    if not column_exists(connection, table_name, column_name):
        quote_name = schema_editor.quote_name
        field = models.CharField(max_length=10, db_index=True, editable=False, blank=True, null=True)
        column_type = field.db_type(connection)
        schema_editor.execute(
            f'ALTER TABLE {quote_name(table_name)} ADD COLUMN {quote_name(column_name)} {column_type} NULL'
        )
        schema_editor.execute(
            f'CREATE INDEX IF NOT EXISTS {quote_name("events_event_event_code_repair_idx")} '
            f'ON {quote_name(table_name)} ({quote_name(column_name)})'
        )

    used = set(
        Event.objects.exclude(event_code__isnull=True)
        .exclude(event_code='')
        .values_list('event_code', flat=True)
    )
    for event in Event.objects.filter(models.Q(event_code__isnull=True) | models.Q(event_code='')):
        value = code('EVT')
        while value in used:
            value = code('EVT')
        used.add(value)
        event.event_code = value
        event.save(update_fields=['event_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_event_event_code'),
    ]

    operations = [
        migrations.RunPython(ensure_event_code_column, migrations.RunPython.noop),
    ]
