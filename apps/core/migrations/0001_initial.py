"""Initial migration for core models (AuditLog)."""

from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("CREATE", "Yaratildi"),
                            ("UPDATE", "O'zgartirildi"),
                            ("DELETE", "O'chirildi"),
                        ],
                        max_length=10,
                        verbose_name="amal",
                    ),
                ),
                ("object_type", models.CharField(max_length=64, verbose_name="obyekt turi")),
                ("object_id", models.CharField(max_length=64, verbose_name="obyekt ID")),
                ("changes", models.JSONField(blank=True, default=dict, verbose_name="o'zgarishlar")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="vaqt")),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_entries",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="bajaruvchi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Audit yozuvi",
                "verbose_name_plural": "Audit yozuvlari",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["object_type", "object_id"], name="audit_obj_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["action"], name="audit_action_idx"),
        ),
    ]
