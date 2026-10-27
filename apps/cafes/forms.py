"""Forms for cafe and zone management (FR-08, FR-09)."""

from __future__ import annotations

from django import forms

from apps.cafes.models import Cafe, Zone


class CafeForm(forms.ModelForm):
    """Create / edit a cafe."""

    class Meta:
        model = Cafe
        fields = [
            "manager",
            "name",
            "address",
            "phone",
            "description",
            "opening_time",
            "closing_time",
            "image",
            "is_active",
        ]
        widgets = {
            "opening_time": forms.TimeInput(attrs={"type": "time"}),
            "closing_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self) -> dict:
        cleaned = super().clean() or {}
        opening = cleaned.get("opening_time")
        closing = cleaned.get("closing_time")
        if opening and closing and opening >= closing:
            self.add_error("closing_time", "Yopilish vaqti ochilish vaqtidan keyin bo'lishi kerak.")
        return cleaned


class ZoneForm(forms.ModelForm):
    """Create / edit a zone."""

    class Meta:
        model = Zone
        fields = ["name", "zone_type"]
