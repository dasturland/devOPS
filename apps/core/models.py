"""Core models: the shared timestamp mixin and the audit log (§3.2, §3.8)."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base adding ``created_at`` / ``updated_at`` audit columns.

    ``created_at`` is indexed because almost every list view orders or filters
    by creation time (NFR-03).
    """

    created_at = models.DateTimeField(
        "yaratilgan vaqt", auto_now_add=True, db_index=True
    )
    updated_at = models.DateTimeField("yangilangan vaqt", auto_now=True)

    class Meta:
        abstract = True


class AuditAction(models.TextChoices):
    """Possible audit actions (FR-26)."""

    CREATE = "CREATE", "Yaratildi"
    UPDATE = "UPDATE", "O'zgartirildi"
    DELETE = "DELETE", "O'chirildi"


class AuditLog(models.Model):
    """Immutable audit trail of significant domain actions (FR-26)."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_entries",
        verbose_name="bajaruvchi",
    )
    action = models.CharField(
        "amal", max_length=10, choices=AuditAction.choices
    )
    object_type = models.CharField("obyekt turi", max_length=64)
    object_id = models.CharField("obyekt ID", max_length=64)
    changes = models.JSONField("o'zgarishlar", default=dict, blank=True)
    created_at = models.DateTimeField("vaqt", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Audit yozuvi"
        verbose_name_plural = "Audit yozuvlari"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["object_type", "object_id"], name="audit_obj_idx"),
            models.Index(fields=["action"], name="audit_action_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.object_type}#{self.object_id}"
