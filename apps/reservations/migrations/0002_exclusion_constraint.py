"""Materialised ``time_range`` column + PostgreSQL overlap exclusion (FR-13).

An inline expression such as ``tstzrange(start_time, start_time + interval)``
cannot be used in a GiST exclusion constraint: in PostgreSQL the operation
``timestamptz + interval`` is only ``STABLE`` (it depends on the session
``TimeZone``/DST), so it is rejected with *"functions in index expression must
be marked IMMUTABLE"*. The fix is a stored ``tstzrange`` column (``time_range``,
§3.6); a bare column reference is immutable and can be indexed.

On SQLite (local dev / tests) the ``AddField`` creates a plain (unused) column
while ``btree_gist`` and the exclusion constraint are skipped, so ``migrate``
still succeeds; the equivalent guarantee is provided by the
``transaction.atomic`` + ``select_for_update`` + overlap check in
``reservations.services`` (§5.1). The ``AddField`` runs on every backend so
``makemigrations --check`` stays clean.
"""

from __future__ import annotations

import django.contrib.postgres.fields
from django.db import migrations


def _is_postgres(schema_editor) -> bool:  # noqa: ANN001
    return schema_editor.connection.vendor == "postgresql"


def enable_btree_gist(apps, schema_editor):  # noqa: ANN001, ARG001
    if _is_postgres(schema_editor):
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")


def drop_btree_gist(apps, schema_editor):  # noqa: ANN001, ARG001
    # Intentionally keep the extension on reverse to avoid breaking other tables.
    return None


def add_exclusion_constraint(apps, schema_editor):  # noqa: ANN001, ARG001
    if not _is_postgres(schema_editor):
        return
    schema_editor.execute(
        """
        ALTER TABLE reservations_reservation
        ADD CONSTRAINT excl_overlapping_active_reservation
        EXCLUDE USING gist (
            table_id WITH =,
            time_range WITH &&
        )
        WHERE (status IN ('PENDING', 'CONFIRMED'))
        """
    )


def drop_exclusion_constraint(apps, schema_editor):  # noqa: ANN001, ARG001
    if not _is_postgres(schema_editor):
        return
    schema_editor.execute(
        "ALTER TABLE reservations_reservation "
        "DROP CONSTRAINT IF EXISTS excl_overlapping_active_reservation"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("reservations", "0001_initial"),
    ]

    operations = [
        # Add the materialised range column on every backend. On PostgreSQL this
        # is a real ``tstzrange`` column; on SQLite the type name is ignored
        # (dynamic typing) and the column simply stays NULL because ``save()``
        # only populates it on PostgreSQL.
        migrations.AddField(
            model_name="reservation",
            name="time_range",
            field=django.contrib.postgres.fields.DateTimeRangeField(
                blank=True, editable=False, null=True
            ),
        ),
        migrations.RunPython(enable_btree_gist, drop_btree_gist),
        migrations.RunPython(add_exclusion_constraint, drop_exclusion_constraint),
    ]
