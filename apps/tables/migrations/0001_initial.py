"""Initial migration for tables (Table)."""

from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cafes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Table",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="yaratilgan vaqt")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="yangilangan vaqt")),
                ("number", models.CharField(max_length=16, verbose_name="raqam")),
                ("capacity", models.PositiveSmallIntegerField(verbose_name="sig'im")),
                (
                    "status",
                    models.CharField(
                        choices=[("AVAILABLE", "Mavjud"), ("INACTIVE", "Faol emas")],
                        default="AVAILABLE",
                        max_length=12,
                        verbose_name="holat",
                    ),
                ),
                (
                    "zone",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tables",
                        to="cafes.zone",
                        verbose_name="zona",
                    ),
                ),
            ],
            options={
                "verbose_name": "Stol",
                "verbose_name_plural": "Stollar",
                "ordering": ["zone", "number"],
            },
        ),
        migrations.AddConstraint(
            model_name="table",
            constraint=models.CheckConstraint(condition=models.Q(capacity__gte=1), name="table_capacity_gte_1"),
        ),
        migrations.AddConstraint(
            model_name="table",
            constraint=models.UniqueConstraint(fields=("zone", "number"), name="uniq_table_number_per_zone"),
        ),
        migrations.AddIndex(
            model_name="table",
            index=models.Index(fields=["zone", "status"], name="table_zone_status_idx"),
        ),
    ]
