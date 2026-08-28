"""Chargement et modélisation de filters.yaml (architecture hybride).

Un profil = une sélection de RESSOURCES (tri grossier fait par la fac) + un
affinage optionnel :
  - keep_only : si non vide, on ne garde QUE les cours correspondant à une règle
  - exclude   : on retire les cours correspondant à une règle (contenu ou dates)
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml


def normalize(text: str) -> str:
    """Minuscule + suppression des accents, pour des comparaisons tolérantes."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().strip()


def _as_list(value) -> list[str]:
    """Accepte une chaîne unique ou une liste ; renvoie toujours une liste."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value]


def _as_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


@dataclass
class Rule:
    """Condition de correspondance d'un cours (toutes les clauses en ET)."""

    name: str
    types: list[str] = field(default_factory=list)  # normalisés (minuscule)
    summary_contains: list[str] = field(default_factory=list)
    summary_not_contains: list[str] = field(default_factory=list)
    group_contains: list[str] = field(default_factory=list)
    group_not_contains: list[str] = field(default_factory=list)
    date_from: date | None = None
    date_to: date | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Rule":
        return cls(
            name=str(data.get("name", "(sans nom)")),
            types=[normalize(t) for t in _as_list(data.get("type"))],
            summary_contains=[normalize(t) for t in _as_list(data.get("summary_contains"))],
            summary_not_contains=[normalize(t) for t in _as_list(data.get("summary_not_contains"))],
            group_contains=[normalize(t) for t in _as_list(data.get("group_contains"))],
            group_not_contains=[normalize(t) for t in _as_list(data.get("group_not_contains"))],
            date_from=_as_date(data.get("date_from")),
            date_to=_as_date(data.get("date_to")),
        )

    def matches(self, course_type: str, summary: str, description: str, start: date | None) -> bool:
        """True si TOUTES les conditions présentes sont satisfaites (ET)."""
        s, d = normalize(summary), normalize(description)

        if self.types and course_type not in self.types:
            return False
        if self.summary_contains and not any(n in s for n in self.summary_contains):
            return False
        if any(n in s for n in self.summary_not_contains):
            return False
        if self.group_contains and not any(n in d for n in self.group_contains):
            return False
        if any(n in d for n in self.group_not_contains):
            return False
        if self.date_from is not None and (start is None or start < self.date_from):
            return False
        if self.date_to is not None and (start is None or start > self.date_to):
            return False
        return True


@dataclass
class Profile:
    name: str
    description: str
    resources: list[str]
    keep_only: list[Rule] = field(default_factory=list)
    exclude: list[Rule] = field(default_factory=list)

    def is_kept(self, course_type: str, summary: str, description: str, start: date | None):
        """Décide du sort d'un cours issu des ressources.

        Renvoie (gardé: bool, raison: str).
        """
        if self.keep_only:
            hit = next((r for r in self.keep_only
                        if r.matches(course_type, summary, description, start)), None)
            if hit is None:
                return False, "hors keep_only"
        excl = next((r for r in self.exclude
                     if r.matches(course_type, summary, description, start)), None)
        if excl is not None:
            return False, f"exclu par '{excl.name}'"
        return True, "gardé"


@dataclass
class Config:
    source_url_template: str
    weeks: int
    calendar_name: str
    default_profile: str
    min_events: int
    profiles: dict[str, Profile]

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        profiles: dict[str, Profile] = {}
        for name, pdata in (raw.get("profiles") or {}).items():
            profiles[name] = Profile(
                name=name,
                description=str(pdata.get("description", "")),
                resources=[str(r) for r in _as_list(pdata.get("resources"))],
                keep_only=[Rule.from_dict(r) for r in (pdata.get("keep_only") or [])],
                exclude=[Rule.from_dict(r) for r in (pdata.get("exclude") or [])],
            )
        return cls(
            source_url_template=raw["source_url_template"],
            weeks=int(raw.get("weeks", 8)),
            calendar_name=str(raw.get("calendar_name", "Calendrier filtré")),
            default_profile=str(raw.get("default_profile", next(iter(profiles), ""))),
            min_events=int(raw.get("min_events", 1)),
            profiles=profiles,
        )

    def profile(self, name: str | None) -> Profile:
        key = name or self.default_profile
        if key not in self.profiles:
            available = ", ".join(self.profiles) or "(aucun)"
            raise KeyError(f"Profil '{key}' introuvable. Profils disponibles : {available}")
        return self.profiles[key]

    def build_url(self, profile: Profile) -> str:
        if not profile.resources:
            raise ValueError(f"Le profil '{profile.name}' ne définit aucune ressource.")
        return self.source_url_template.format(
            resources=",".join(profile.resources),
            weeks=self.weeks,
        )
