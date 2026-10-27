"""Forms for availability search and the booking wizard (FR-11, FR-12)."""

from __future__ import annotations

from django import forms

from apps.cafes.models import ZoneType

DURATION_CHOICES = [
    (60, "1 soat"),
    (90, "1.5 soat"),
    (120, "2 soat"),
    (180, "3 soat"),
]


class AvailabilitySearchForm(forms.Form):
    """Step 1 of the wizard: choose when and for how many (FR-11)."""

    date = forms.DateField(label="Sana", widget=forms.DateInput(attrs={"type": "date"}))
    start_time = forms.TimeField(
        label="Boshlanish vaqti", widget=forms.TimeInput(attrs={"type": "time"})
    )
    duration_minutes = forms.TypedChoiceField(
        label="Davomiylik", choices=DURATION_CHOICES, coerce=int, initial=120
    )
    guests_count = forms.IntegerField(label="Odam soni", min_value=1)
    zone_type = forms.ChoiceField(
        label="Zona turi",
        required=False,
        choices=[("", "Barchasi"), *ZoneType.choices],
    )


class ReservationConfirmForm(forms.Form):
    """Step 3 of the wizard: confirm the selected table (FR-12)."""

    table = forms.IntegerField(widget=forms.HiddenInput)
    date = forms.DateField(widget=forms.HiddenInput)
    start_time = forms.TimeField(widget=forms.HiddenInput)
    duration_minutes = forms.IntegerField(widget=forms.HiddenInput)
    guests_count = forms.IntegerField(widget=forms.HiddenInput)
    note = forms.CharField(label="Izoh", required=False, widget=forms.Textarea)
