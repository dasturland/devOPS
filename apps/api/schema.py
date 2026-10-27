"""OpenAPI schema customisation hooks for drf-spectacular (§8.3).

The bulk of the schema is generated automatically from the serializers and
``@extend_schema`` annotations on the viewsets. This module centralises any
shared schema metadata so it can be referenced from the settings if needed.
"""

from __future__ import annotations

API_TAGS = [
    {"name": "cafes", "description": "Kafelar va zonalar."},
    {"name": "tables", "description": "Stollar va bo'sh stol qidirish."},
    {"name": "reservations", "description": "Bronlar va holat o'tishlari."},
    {"name": "reviews", "description": "Sharhlar va baholar."},
]
