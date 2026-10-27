"""Forms for leaving reviews (FR-21)."""

from __future__ import annotations

from django import forms

from apps.reviews.models import Review


class ReviewForm(forms.ModelForm):
    """Create a review for a completed reservation."""

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
        }

    def clean_rating(self) -> int:
        rating = self.cleaned_data["rating"]
        if not 1 <= rating <= 5:
            raise forms.ValidationError("Baho 1 dan 5 gacha bo'lishi kerak.")
        return rating
