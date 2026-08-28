"""Récupération, filtrage et réémission du flux iCal (architecture hybride)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime

import requests
from icalendar import Calendar

from .config import Config, Profile, normalize

_TYPE_RE = re.compile(r"^\s*([A-Za-zÀ-ÿ]+)")


def course_type(summary: str) -> str:
    """Type de cours = premières lettres du titre (CM, TD, TP, ED, CC...)."""
    m = _TYPE_RE.match(summary or "")
    return normalize(m.group(1)) if m else ""


def event_date(component) -> date | None:
    """Date de début du cours (à partir de DTSTART), ou None si absent."""
    dt = component.get("DTSTART")
    if dt is None:
        return None
    value = dt.dt
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def fetch_ics(url: str, timeout: int = 60) -> bytes:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


@dataclass
class FilterResult:
    calendar: Calendar
    kept: int
    total: int
    excluded: dict[str, int] = field(default_factory=dict)


def filter_calendar(ics_bytes: bytes, profile: Profile, calendar_name: str) -> FilterResult:
    src = Calendar.from_ical(ics_bytes)

    out = Calendar()
    for key, value in src.items():  # VERSION, PRODID, CALSCALE...
        out.add(key, value)
    out["X-WR-CALNAME"] = calendar_name

    total = kept = 0
    excluded: dict[str, int] = {}

    for component in src.walk("VEVENT"):
        total += 1
        summary = str(component.get("SUMMARY", ""))
        description = str(component.get("DESCRIPTION", ""))
        keep, reason = profile.is_kept(
            course_type(summary), summary, description, event_date(component)
        )
        if keep:
            out.add_component(component)
            kept += 1
        else:
            excluded[reason] = excluded.get(reason, 0) + 1

    return FilterResult(calendar=out, kept=kept, total=total, excluded=excluded)


def run(config: Config, profile_name: str | None,
        ics_bytes: bytes | None = None) -> tuple[bytes, FilterResult]:
    """Pipeline : compose l'URL des ressources -> (télécharge) -> affine."""
    profile = config.profile(profile_name)
    if ics_bytes is None:
        ics_bytes = fetch_ics(config.build_url(profile))
    result = filter_calendar(ics_bytes, profile, config.calendar_name)
    return result.calendar.to_ical(), result
