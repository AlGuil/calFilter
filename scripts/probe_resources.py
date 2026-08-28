#!/usr/bin/env python3
"""Sonde chaque ressource de l'emploi du temps ADE isolément.

But : découvrir à quel groupe/UE correspond chaque identifiant `resources=<id>`
de l'URL, afin de pouvoir trier par ressources (voir docs/RESSOURCES.md).

Usage :
    python scripts/probe_resources.py                # nbWeeks=26, sortie texte
    python scripts/probe_resources.py --weeks 40     # horizon plus large
    python scripts/probe_resources.py --json map.json # dump JSON détaillé

La liste des ressources est lue depuis filters.yaml (source_url) si présente,
sinon depuis la constante RES ci-dessous.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

BASE = ("https://edt.uca.fr/jsp/custom/modules/plannings/anonymous_cal.jsp"
        "?resources={rid}&projectId=4&calType=ical&nbWeeks={nw}&displayConfigId=128")


def resources_from_config() -> list[str]:
    cfg = Path(__file__).resolve().parent.parent / "filters.yaml"
    if not cfg.exists():
        return []
    m = re.search(r"resources=([0-9,]+)", cfg.read_text(encoding="utf-8"))
    if not m:
        return []
    return list(dict.fromkeys(m.group(1).split(",")))


def unfold(txt: str) -> list[str]:
    txt = txt.replace("\r\n", "\n")
    out: list[str] = []
    for line in txt.split("\n"):
        if line[:1] == " " and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out


def parse(txt: str) -> list[dict]:
    events: list[dict] = []
    cur: dict | None = None
    for line in unfold(txt):
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT" and cur is not None:
            events.append(cur)
            cur = None
        elif cur is not None:
            if line.startswith("SUMMARY:"):
                cur["s"] = line[8:]
            elif line.startswith("DESCRIPTION:"):
                cur["d"] = line[12:]
    return events


def groups(desc: str) -> list[str]:
    parts = [p.strip() for p in (desc or "").split("\\n")
             if p.strip() and not p.strip().startswith("(Updated")]
    return [p for p in parts
            if re.search(r"Groupe|PHI|DFGSP|DFASP|POP|Herbier|Risque|Endocrino|Physiologie", p)]


def ctype(summary: str) -> str:
    m = re.match(r"\s*([A-Za-zÀ-ÿ]+)", summary or "")
    return m.group(1).upper() if m else "?"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weeks", type=int, default=26)
    ap.add_argument("--json", help="Écrire le détail JSON dans ce fichier")
    ap.add_argument("--sleep", type=float, default=0.25, help="Pause entre requêtes (s)")
    args = ap.parse_args(argv)

    ids = resources_from_config()
    if not ids:
        print("Aucune ressource trouvée dans filters.yaml", file=sys.stderr)
        return 1

    results: dict[str, dict] = {}
    for rid in ids:
        url = BASE.format(rid=urllib.parse.quote(rid), nw=args.weeks)
        try:
            txt = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            results[rid] = {"err": str(exc)}
            continue
        evs = parse(txt)
        gc: Counter = Counter()
        tc: Counter = Counter()
        for e in evs:
            for g in (groups(e.get("d", "")) or ["<aucun>"]):
                gc[g] += 1
            tc[ctype(e.get("s", ""))] += 1
        results[rid] = {"n": len(evs), "groups": gc.most_common(), "types": tc.most_common()}
        time.sleep(args.sleep)

    if args.json:
        Path(args.json).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Écrit -> {args.json}", file=sys.stderr)

    print(f"{'RID':>7} {'N':>4}  types / groupes distinctifs")
    print("-" * 78)
    for rid, info in results.items():
        if "err" in info:
            print(f"{rid:>7}   ERR {info['err'][:50]}")
            continue
        types = ",".join(f"{t}:{c}" for t, c in info["types"])
        distinct = [f"{g}({c})" for g, c in info["groups"]
                    if re.search(r"Groupe|Herbier|Risque|Endocrino|Physiologie|POP", g)]
        print(f"{rid:>7} {info['n']:>4}  {types[:30]:<30} {'; '.join(distinct[:3])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
