"""Shared validators for request schemas."""
import re
from typing import Optional

# E.164 format: +[country code][subscriber number], 1-15 digits total
# e.g. +1234567890, +919876543210
E164_PATTERN = re.compile(r"^\+[1-9]\d{6,14}$")


def validate_phone_e164(phone: str) -> str:
    """Validate phone number is in E.164 format (e.g. +1234567890)."""
    phone = phone.strip()
    if not E164_PATTERN.match(phone):
        raise ValueError(
            "Phone number must be in E.164 format (e.g. +1234567890, +919876543210)"
        )
    return phone
