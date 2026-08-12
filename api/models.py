"""Shared Phase 4 API constants and envelope helpers."""

from __future__ import annotations

from typing import Any


API_VERSION = "phase4-api-v1"


def success_envelope(*, mode: str, scientific_authority: str, data: Any) -> dict[str, Any]:
    """Build the approved success envelope for API responses."""

    return {
        "api_version": API_VERSION,
        "mode": mode,
        "scientific_authority": scientific_authority,
        "data": data,
        "schema": {"name": "ApiSuccessEnvelope", "version": API_VERSION},
    }


def error_envelope(*, code: str, message: str, status_code: int) -> dict[str, Any]:
    """Build the approved error envelope for API responses."""

    return {
        "api_version": API_VERSION,
        "mode": "error",
        "scientific_authority": "none",
        "errors": [
            {
                "code": code,
                "message": message,
                "status_code": status_code,
            }
        ],
        "schema": {"name": "ApiErrorEnvelope", "version": API_VERSION},
    }
