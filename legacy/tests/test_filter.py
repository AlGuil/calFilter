"""Tests de non-régression du moteur hybride."""

from datetime import date
from pathlib import Path

from calfilter.config import Config, Profile, Rule
from calfilter.filter import course_type, filter_calendar

ROOT = Path(__file__).resolve().parent.parent

# Mini flux : ce que renverraient les ressources (avec dates).
SAMPLE = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//test//test
BEGIN:VEVENT
UID:1
DTSTART:20261006T060000Z
SUMMARY:CM - UE 3 Dysfonctionnement cellulaire
DESCRIPTION:\\n\\nPHI 2 DFGSP 2\\nPROF X\\n
END:VEVENT
BEGIN:VEVENT
UID:2
DTSTART:20261007T060000Z
SUMMARY:TP2/3 UE 1
DESCRIPTION:\\n\\nAUZELOUX PHILIPPE\\nGroupe 3\\n
END:VEVENT
BEGIN:VEVENT
UID:3
DTSTART:20261104T060000Z
SUMMARY:ED1 - UE 4 Voies
DESCRIPTION:\\n\\nGroupe B\\n
END:VEVENT
BEGIN:VEVENT
UID:4
DTSTART:20261105T060000Z
SUMMARY:TP4 - UE HERBIER
DESCRIPTION:\\n\\nHerbier\\n
END:VEVENT
END:VCALENDAR
"""


def test_course_type():
    assert course_type("TP2/3 UE 1") == "tp"
    assert course_type("ED1 - UE 4") == "ed"
    assert course_type("CM - UE 3") == "cm"


def test_no_refinement_keeps_all():
    prof = Profile(name="p", description="", resources=["1"])
    res = filter_calendar(SAMPLE, prof, "test")
    assert res.kept == 4


def test_exclude_by_content():
    prof = Profile(name="p", description="", resources=["1"],
                   exclude=[Rule.from_dict({"name": "no herbier", "summary_contains": "HERBIER"})])
    res = filter_calendar(SAMPLE, prof, "test")
    uids = {str(e["UID"]) for e in res.calendar.walk("VEVENT")}
    assert uids == {"1", "2", "3"}


def test_exclude_by_date_range():
    prof = Profile(name="p", description="", resources=["1"],
                   exclude=[Rule.from_dict({"name": "semaine off",
                                            "date_from": "2026-11-02", "date_to": "2026-11-08"})])
    res = filter_calendar(SAMPLE, prof, "test")
    uids = {str(e["UID"]) for e in res.calendar.walk("VEVENT")}
    # Les cours du 4 et 5 nov tombent dans la plage -> retirés.
    assert uids == {"1", "2"}


def test_keep_only_restricts():
    prof = Profile(name="p", description="", resources=["1"],
                   keep_only=[Rule.from_dict({"name": "cm promo", "group_contains": "PHI 2 DFGSP 2"})])
    res = filter_calendar(SAMPLE, prof, "test")
    uids = {str(e["UID"]) for e in res.calendar.walk("VEVENT")}
    assert uids == {"1"}


def test_config_loads_and_builds_url():
    cfg = Config.load(ROOT / "filters.yaml")
    assert cfg.default_profile in cfg.profiles
    prof = cfg.profile("alban")
    assert prof.resources  # non vide
    url = cfg.build_url(prof)
    assert "{resources}" not in url and "{weeks}" not in url  # placeholders remplis
    assert "resources=" + ",".join(prof.resources) in url
    assert f"nbWeeks={cfg.weeks}" in url
