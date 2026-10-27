"""Forms for table management (FR-10)."""

from __future__ import annotations

from django import forms

from apps.tables.models import Table


class TableForm(forms.ModelForm):
    """Create / edit a table."""

    class Meta:
        model = Table
        fields = ["number", "capacity", "status"]

    def clean_capacity(self) -> int:
        capacity = self.cleaned_data["capacity"]
        if capacity < 1:
            raise forms.ValidationError("Sig'im kamida 1 bo'lishi kerak.")
        return capacity
