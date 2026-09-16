#!/usr/bin/env python3
"""Sonde chaque ressource de l'emploi du temps ADE isolément.

But : découvrir à quel groupe/UE correspond chaque identifiant `resources=<id>`
de l'URL, afin de pouvoir trier par ressources (voir docs/RESSOURCES.md).

Usage :
    python scripts/probe_resources.py                # nbWeeks=26, sortie texte
    python scripts/probe_resources.py --weeks 40     # horizon plus large
    python scripts/probe_resources.py --json map.json # dump JSON détaillé

La liste complète des ressources de la promo est la constante RESOURCES ci-dessous
(relevée depuis l'URL fournie par la fac). Mets-la à jour si la fac renumérote.
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


# Liste complète des ressources de la promo DFGSP2 (toutes celles de l'URL fournie
# par la fac). Sonder chacune isolément révèle à quel groupe/UE elle correspond.
RESOURCES = (
    "51303,51302,51300,51299,51298,51297,51296,51295,51294,51293,51292,51291,"
    "51290,51289,51288,50942,50941,48538,64001,64000,63999,63998,63997,9079,9078,"
    "9077,61319,61318,60863,60862,60530,60529,60528,60527,60526,60525,60524,6139,"
    "6130,6127,6126,6125,5644,4388,4387,4386,4385,4382,4321,4127,4125,4116,4114,"
    "4110,4109,4029,38837,54153,34457"
)


# Liste complète des ressources de la promo DFGSP3 (relevée depuis l'URL fournie
# par la fac, dédoublonnée). Voir la cartographie dans docs/RESSOURCES.md.
# Utilisation : --promo 3
RESOURCES_DFGSP3 = (
    "48569,48568,48567,48566,48565,48564,48563,48562,48561,48560,30002,29127,"
    "29009,10662,46006,46005,46004,46003,46002,46001,46000,45999,63702,45469,"
    "9598,9596,9086,9085,9084,9083,62663,62662,62655,8197,8172,8171,8169,7847,"
    "61269,61268,61144,7139,7138,7137,7136,6678,6660,6415,6414,6413,4658,4135,"
    "4133,4130,4030,3916,3910,3909,3908,3877,3875,3874,3873,3872,57314,57313,"
    "57312,57311,57310,3375,3324,3302,3301,55915,2106,55373,55372,55371,36959,"
    "62,59,44,42,40,32,20,19,14"
)


# Liste complète des ressources de la promo DFASP1 (4e année ; relevée depuis
# l'URL fournie par la fac, dédoublonnée). Voir la cartographie dans
# docs/RESSOURCES.md. Utilisation : --promo 4
RESOURCES_DFASP1 = (
    "51137,51135,51134,48353,48351,65022,64209,64208,64207,63984,63538,63537,"
    "63536,63535,63534,9521,9520,9075,8952,8951,8883,8824,62060,61856,61855,"
    "7903,7902,7900,7899,7895,7894,7893,7891,7889,7888,7887,7886,7884,7883,"
    "7491,7490,7489,7488,7487,7486,7485,7484,7483,7481,7480,5377,5376,5375,"
    "5374,5373,5372,5371,5370,5369,5309,5056,5055,5054,5053,4142,4141,4140,"
    "4139,39870,39847,3824,51136,49424,65868,47812,47802,47801,47800,47799,"
    "47798,47797,47796,63533,62653,62652,62651,62650,62649,62648,62647,62646,"
    "62645,62644,7892,7890,7885,7882,7482,5368,4208,4138,4137,4055,3705,34125"
)


# Ressources de la promo DFASP2 (5e année ; URL fournie par la fac). La 5e année
# est organisée par parcours, pas par groupes de TP : 4096 = tous les parcours,
# 4098 = Officine, 4099 = Internat, 4097 = Industrie (aucun cours publié pour
# l'instant), 32783 = nœud vide non identifié. Voir docs/RESSOURCES.md.
# Utilisation : --promo 5
RESOURCES_DFASP2 = "4099,4098,4097,4096,32783"


def resources_from_config(promo: str = "2") -> list[str]:
    raw = {"3": RESOURCES_DFGSP3, "4": RESOURCES_DFASP1,
           "5": RESOURCES_DFASP2}.get(str(promo), RESOURCES)
    return list(dict.fromkeys(raw.split(",")))


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
    ap.add_argument("--promo", default="2", choices=["2", "3", "4", "5"],
                    help="Promo à sonder : 2 (DFGSP2, défaut), 3 (DFGSP3), "
                         "4 (DFASP1) ou 5 (DFASP2)")
    ap.add_argument("--json", help="Écrire le détail JSON dans ce fichier")
    ap.add_argument("--sleep", type=float, default=0.25, help="Pause entre requêtes (s)")
    args = ap.parse_args(argv)

    ids = resources_from_config(args.promo)
    if not ids:
        print("Aucune ressource à sonder", file=sys.stderr)
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
