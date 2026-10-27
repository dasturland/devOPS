"""PostgreSQL-only exclusion constraint preventing overlapping bookings (FR-13).

On SQLite (local dev / tests) every operation here is a no-op, so ``migrate``
still succeeds; the equivalent guarantee is provided by the ``transaction.atomic``
+ ``select_for_update`` + overlap check in ``reservations.services`` (§5.1).
"""

from __future__ import annotations

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
            tstzrange(
                start_time,
                start_time + (duration_minutes || ' minutes')::interval
            ) WITH &&
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
        migrations.RunPython(enable_btree_gist, drop_btree_gist),
        migrations.RunPython(add_exclusion_constraint, drop_exclusion_constraint),
    ]
