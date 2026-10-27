"""Initial migration for reservations (Reservation)."""

from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tables", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="yaratilgan vaqt")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="yangilangan vaqt")),
                ("start_time", models.DateTimeField(db_index=True, verbose_name="boshlanish vaqti")),
                ("duration_minutes", models.PositiveSmallIntegerField(default=120, verbose_name="davomiylik (daqiqa)")),
                ("guests_count", models.PositiveSmallIntegerField(verbose_name="odam soni")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Kutilmoqda"),
                            ("CONFIRMED", "Tasdiqlangan"),
                            ("COMPLETED", "Yakunlangan"),
                            ("CANCELLED", "Bekor qilingan"),
                            ("REJECTED", "Rad etilgan"),
                            ("NO_SHOW", "Kelmadi"),
                        ],
                        db_index=True,
                        default="PENDING",
                        max_length=12,
                        verbose_name="holat",
                    ),
                ),
                ("note", models.TextField(blank=True, verbose_name="izoh")),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reservations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="mijoz",
                    ),
                ),
                (
                    "table",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reservations",
                        to="tables.table",
                        verbose_name="stol",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bron",
                "verbose_name_plural": "Bronlar",
                "ordering": ["-start_time"],
            },
        ),
        migrations.AddConstraint(
            model_name="reservation",
            constraint=models.CheckConstraint(condition=models.Q(guests_count__gte=1), name="res_guests_gte_1"),
        ),
        migrations.AddConstraint(
            model_name="reservation",
            constraint=models.CheckConstraint(condition=models.Q(duration_minutes__gte=30), name="res_duration_min"),
        ),
        migrations.AddIndex(
            model_name="reservation",
            index=models.Index(fields=["table", "start_time"], name="res_table_start_idx"),
        ),
        migrations.AddIndex(
            model_name="reservation",
            index=models.Index(fields=["status"], name="res_status_idx"),
        ),
        migrations.AddIndex(
            model_name="reservation",
            index=models.Index(fields=["customer", "status"], name="res_customer_status_idx"),
        ),
    ]
