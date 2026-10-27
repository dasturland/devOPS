"""Template helpers for the dashboard (FR-22)."""

from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def percentage(value: float) -> str:
    """Format a number as a percentage string."""
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "0.0%"


@register.filter
def get_item(mapping: dict, key: str):  # noqa: ANN201
    """Return ``mapping[key]`` or 0; useful for status dictionaries in templates."""
    if isinstance(mapping, dict):
        return mapping.get(key, 0)
    return 0
