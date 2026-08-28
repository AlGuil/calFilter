#!/usr/bin/env python3
"""Compte l'usage anonyme du proxy Cloudflare (option « Expérimental »).

Le worker écrit, à chaque appel, un point dans Analytics Engine :
  blob1 = hash SHA-256 des ressources (clé anonyme, aucune IP ni cookie)
  blob2 = ressources brutes (IDs de groupes, non personnels)
  blob3 = nbWeeks

Ce script interroge le dataset via l'API SQL d'Analytics Engine et affiche :
  - le nombre de **sélections distinctes actives** (≈ plancher du nombre de
    personnes : deux personnes du même groupe partagent la même sélection) ;
  - une estimation du nombre total d'appels (pondérée par l'échantillonnage) ;
  - les combinaisons de groupes les plus fréquentes.

⚠️ Ne voit QUE les utilisateurs ayant activé l'option « Expérimental » (qui passe
par le worker). Les abonnements ADE directs ne touchent aucun serveur à toi et
restent invisibles (cf. docs).

Prérequis :
  - CF_ACCOUNT_ID : l'ID de compte Cloudflare (dash → Workers & Pages → à droite).
  - CF_API_TOKEN  : un jeton API avec la permission « Account Analytics : Read »
    (dash → My Profile → API Tokens → Create Token → Custom).

Usage :
  export CF_ACCOUNT_ID=xxxx
  export CF_API_TOKEN=yyyy
  python scripts/usage_stats.py                 # 7 derniers jours
  python scripts/usage_stats.py --days 30
  python scripts/usage_stats.py --dataset calfilter_usage --top 20
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.cloudflare.com/client/v4/accounts/{acct}/analytics_engine/sql"


def local_creds() -> dict[str, str]:
    """Lit les identifiants depuis un fichier local `.cf_usage.env` (ignoré par
    git), au format KEY=VALUE. Cherché à côté du script puis à la racine du dépôt.
    Permet de lancer `python scripts/usage_stats.py` sans exporter de variables."""
    here = Path(__file__).resolve().parent
    out: dict[str, str] = {}
    for path in (here / ".cf_usage.env", here.parent / ".cf_usage.env"):
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
            break
    return out


def run_sql(acct: str, token: str, sql: str) -> list[dict]:
    req = urllib.request.Request(
        API.format(acct=acct),
        data=sql.encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "text/plain"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.loads(r.read().decode("utf-8", "replace"))
    return payload.get("data", [])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=7, help="Fenêtre en jours (défaut 7)")
    ap.add_argument("--dataset", default="calfilter_usage", help="Nom du dataset AE")
    ap.add_argument("--top", type=int, default=10, help="Nb de combinaisons à lister")
    ap.add_argument("--account")
    ap.add_argument("--token")
    args = ap.parse_args(argv)

    # Priorité : --account/--token > variables d'env > fichier local .cf_usage.env
    creds = local_creds()
    account = args.account or os.environ.get("CF_ACCOUNT_ID") or creds.get("CF_ACCOUNT_ID")
    token = args.token or os.environ.get("CF_API_TOKEN") or creds.get("CF_API_TOKEN")

    if not account or not token:
        print("Identifiants manquants. Renseigne-les via --account/--token, les",
              "variables CF_ACCOUNT_ID / CF_API_TOKEN, ou le fichier local",
              "scripts/.cf_usage.env (KEY=VALUE, ignoré par git).", file=sys.stderr)
        return 2

    # Une ligne par sélection distincte (blob1=hash, blob2=ressources), pondérée
    # par l'échantillonnage. Le nombre de lignes = sélections distinctes actives.
    where = f"timestamp > NOW() - INTERVAL '{args.days}' DAY"
    sql = (
        "SELECT blob2 AS resources, "
        "sum(_sample_interval) AS hits, count() AS raw "
        f"FROM {args.dataset} "
        f"WHERE {where} "
        "GROUP BY blob1, blob2 "
        "ORDER BY hits DESC "
        "LIMIT 10000"
    )
    try:
        rows = run_sql(account, token, sql)
    except urllib.error.HTTPError as e:
        print(f"Erreur API ({e.code}) : {e.read().decode('utf-8','replace')[:300]}",
              file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

    distinct = len(rows)
    total = int(sum(float(r.get("hits", 0)) for r in rows))
    print(f"== Usage du proxy calFilter — {args.days} derniers jours ==\n")
    print(f"Sélections distinctes actives : {distinct}")
    print(f"   (≈ plancher du nombre de personnes ; même groupe = même sélection)")
    print(f"Appels estimés (total)        : {total}")
    print(f"Moyenne d'appels / jour       : {total / max(args.days,1):.0f}\n")
    if not rows:
        print("Aucune donnée. Le binding USAGE est-il déployé, et quelqu'un a-t-il")
        print("utilisé l'option « Expérimental » sur cette fenêtre ?")
        return 0
    print(f"Top {min(args.top, distinct)} combinaisons de groupes (ressources -> appels estimés) :")
    for r in rows[:args.top]:
        print(f"  {int(float(r['hits'])):>6}  resources={r['resources']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
