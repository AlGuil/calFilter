"""Point d'entrée CLI : python -m calfilter --profile alban --out calendar.ics"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .config import Config
from .filter import run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="calfilter",
        description="Compose le flux iCal par ressources puis l'affine selon un profil de filters.yaml.",
    )
    parser.add_argument("-c", "--config", default="filters.yaml",
                        help="Chemin du fichier de config (défaut: filters.yaml)")
    parser.add_argument("-p", "--profile", default=os.environ.get("CALFILTER_PROFILE"),
                        help="Profil à utiliser (défaut: CALFILTER_PROFILE, sinon default_profile)")
    parser.add_argument("-o", "--out", default="-", help="Fichier ICS de sortie (défaut: stdout)")
    parser.add_argument("--input", help="Lire l'ICS depuis un fichier local au lieu de télécharger (tests)")
    parser.add_argument("--print-url", action="store_true", help="Afficher l'URL composée et quitter")
    args = parser.parse_args(argv)

    config = Config.load(args.config)

    if args.print_url:
        profile = config.profile(args.profile)
        print(config.build_url(profile))
        return 0

    ics_bytes = Path(args.input).read_bytes() if args.input else None

    try:
        output, result = run(config, args.profile, ics_bytes=ics_bytes)
    except Exception as exc:  # remonte proprement pour que le workflow échoue
        print(f"[calfilter] ÉCHEC : {exc}", file=sys.stderr)
        return 2

    profile_name = args.profile or config.default_profile
    print(f"[calfilter] profil '{profile_name}' : {result.kept}/{result.total} cours gardés",
          file=sys.stderr)
    for reason, count in result.excluded.items():
        print(f"[calfilter]   retirés ({reason}): {count}", file=sys.stderr)

    if result.kept < config.min_events:
        print(
            f"[calfilter] ÉCHEC : seulement {result.kept} cours gardés "
            f"(seuil min_events={config.min_events}). Le flux ou les ressources ont peut-être changé.",
            file=sys.stderr,
        )
        return 3

    if args.out == "-":
        sys.stdout.buffer.write(output)
    else:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_bytes(output)
        print(f"[calfilter] écrit -> {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
