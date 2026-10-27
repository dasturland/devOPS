"""Initial migration for reviews (Review)."""

from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cafes", "0001_initial"),
        ("reservations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="yaratilgan vaqt")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="yangilangan vaqt")),
                ("rating", models.PositiveSmallIntegerField(verbose_name="baho")),
                ("comment", models.TextField(blank=True, verbose_name="izoh")),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="muallif",
                    ),
                ),
                (
                    "cafe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="cafes.cafe",
                        verbose_name="kafe",
                    ),
                ),
                (
                    "reservation",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review",
                        to="reservations.reservation",
                        verbose_name="bron",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sharh",
                "verbose_name_plural": "Sharhlar",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="review_rating_1_5",
            ),
        ),
        migrations.AddIndex(
            model_name="review",
            index=models.Index(fields=["cafe", "rating"], name="review_cafe_rating_idx"),
        ),
    ]
