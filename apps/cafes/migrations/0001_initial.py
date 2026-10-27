"""Initial migration for cafes (Cafe, Zone)."""

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
            name="Cafe",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="yaratilgan vaqt")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="yangilangan vaqt")),
                ("name", models.CharField(max_length=160, verbose_name="nom")),
                ("slug", models.SlugField(unique=True, verbose_name="slug")),
                ("address", models.CharField(max_length=255, verbose_name="manzil")),
                ("phone", models.CharField(max_length=32, verbose_name="telefon")),
                ("description", models.TextField(blank=True, verbose_name="tavsif")),
                ("opening_time", models.TimeField(verbose_name="ochilish vaqti")),
                ("closing_time", models.TimeField(verbose_name="yopilish vaqti")),
                ("image", models.ImageField(blank=True, upload_to="cafes/", verbose_name="rasm")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="faol")),
                (
                    "manager",
                    models.ForeignKey(
                        limit_choices_to={"role": "MANAGER"},
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="managed_cafes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="menejer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kafe",
                "verbose_name_plural": "Kafelar",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Zone",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="yaratilgan vaqt")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="yangilangan vaqt")),
                ("name", models.CharField(max_length=80, verbose_name="nom")),
                (
                    "zone_type",
                    models.CharField(
                        choices=[("HALL", "Zal"), ("TERRACE", "Terrasa"), ("VIP", "VIP")],
                        default="HALL",
                        max_length=12,
                        verbose_name="zona turi",
                    ),
                ),
                (
                    "cafe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="zones",
                        to="cafes.cafe",
                        verbose_name="kafe",
                    ),
                ),
            ],
            options={
                "verbose_name": "Zona",
                "verbose_name_plural": "Zonalar",
                "ordering": ["cafe", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="cafe",
            index=models.Index(fields=["name"], name="cafe_name_idx"),
        ),
        migrations.AddIndex(
            model_name="cafe",
            index=models.Index(fields=["is_active"], name="cafe_is_active_idx"),
        ),
        migrations.AddConstraint(
            model_name="zone",
            constraint=models.UniqueConstraint(fields=("cafe", "name"), name="uniq_zone_name_per_cafe"),
        ),
    ]
