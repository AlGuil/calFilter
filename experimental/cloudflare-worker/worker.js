/**
 * calFilter — proxy expérimental d'enrichissement des salles.
 *
 * Récupère le flux iCal officiel d'ADE en direct et réécrit chaque champ
 * LOCATION pour y ajouter l'aile (R1/R2/R3) et l'étage, absents de l'export
 * ADE (ex. "Amphi 2B" -> "R1 Amphi 2B (4e)").
 *
 * Déploiement : voir README.md de ce dossier.
 * Appel : https://<ton-worker>.workers.dev/?resources=9077,4125,50942&nbWeeks=52
 *
 * ⚠️ Expérimental : les agendas abonnés dépendent alors de la disponibilité de
 * ce worker (et non plus seulement de la fac). La table des salles vient d'un
 * plan 2021 — à tenir à jour (cf. docs/SALLES.md). Doit rester synchro avec la
 * constante ROOMS de index.html.
 */

const ADE = "https://edt.uca.fr/jsp/custom/modules/plannings/anonymous_cal.jsp";

// nom exact de salle -> [aile, étage]. aile "" = inconnue (on n'ajoute que l'étage).
const ROOMS = {
  "Amphi 1": ["R1", "1er"], "Amphi 4": ["R2", "1er"], "Amphi 5": ["R3", "1er"],
  "Amphi 2A": ["R1", "3e"], "Amphi 6A": ["R3", "3e"],
  "Amphi 2B": ["R1", "4e"], "Amphi 6B": ["R3", "4e"], "Amphi 3": ["R1", "5e"],
  "Amphi Volcans (B)": ["", "RDC"], "Auditorium": ["", "RDC"],
  "Salle 002": ["R1", "RDC"], "Salle 040": ["R1", "RDC"], "Salle 042": ["R2", "RDC"],
  "Salle 126": ["R1", "1er"], "Salle 127": ["R1", "1er"],
  "Salle 203": ["", "2e"], "Salle 205": ["R1", "2e"], "Salle 223": ["R1", "2e"],
  "Salle 224": ["", "2e"], "Salle 225": ["", "2e"], "Salle 226": ["", "2e"],
  "Salle 227": ["", "2e"], "Salle 228": ["", "2e"], "Salle 234": ["", "2e"],
  "Salle 236": ["", "2e"], "Salle 237": ["", "2e"], "Salle 243": ["R2", "2e"],
  "Salle 244": ["R2", "2e"], "Salle 245": ["R2", "2e"], "Salle 246": ["R2", "2e"],
  "Salle 262": ["R3", "2e"], "Salle 305": ["", "3e"], "Salle 326": ["", "3e"],
  "Salle 330-342": ["", "3e"], "Salle 345": ["", "3e"], "Salle 431": ["", "4e"],
  "Salle 449": ["", "4e"], "Salle 501": ["", "5e"], "Salle 502": ["", "5e"],
  "Salle 505": ["", "5e"], "Salle 527": ["", "5e"], "Salle 532": ["R2", "5e"],
  "Salle 547": ["R2", "5e"],
};
// clés triées par longueur décroissante pour un match par préfixe non ambigu.
const KEYS = Object.keys(ROOMS).sort((a, b) => b.length - a.length);

function enrichName(name) {
  const t = name.trim();
  if (!t) return name;
  for (const key of KEYS) {
    if (t === key || t.startsWith(key + " ") || t.startsWith(key + "-")) {
      const [aile, etage] = ROOMS[key];
      let out = aile ? aile + " " + t : t;
      if (etage && !/\(\s*(RDC|\d)/.test(out)) out += " (" + etage + ")";
      return out;
    }
  }
  return name; // salle inconnue -> inchangée
}

// une LOCATION peut lister plusieurs salles, séparées par une virgule échappée "\,"
function transformLocation(value) {
  return value.split("\\,").map(enrichName).join("\\,");
}

// repliage RFC 5545 (lignes <= 75 octets), suffisant pour nos valeurs courtes.
function foldLine(line) {
  if (line.length <= 74) return line;
  let out = line.slice(0, 74);
  let rest = line.slice(74);
  while (rest.length) { out += "\r\n " + rest.slice(0, 73); rest = rest.slice(73); }
  return out;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const resources = url.searchParams.get("resources");
    if (!resources) {
      return new Response("Paramètre 'resources' manquant.\nEx: ?resources=9077,4125,50942&nbWeeks=52",
        { status: 400, headers: { "content-type": "text/plain; charset=utf-8" } });
    }
    const weeks = url.searchParams.get("nbWeeks") || "52";
    const ade = `${ADE}?resources=${encodeURIComponent(resources)}`
      + `&projectId=4&calType=ical&displayConfigId=128&nbWeeks=${encodeURIComponent(weeks)}`;

    let resp;
    try {
      resp = await fetch(ade, { cf: { cacheTtl: 300, cacheEverything: true } });
    } catch (e) {
      return new Response("Flux ADE injoignable.", { status: 502, headers: { "content-type": "text/plain; charset=utf-8" } });
    }
    if (!resp.ok) {
      return new Response("Flux ADE indisponible (" + resp.status + ").",
        { status: 502, headers: { "content-type": "text/plain; charset=utf-8" } });
    }

    let text = await resp.text();
    // réécrit chaque propriété LOCATION (en gérant le repliage de ligne)
    text = text.replace(/^LOCATION:((?:.*)(?:\r?\n[ \t].*)*)/gm, (_m, val) => {
      const unfolded = val.replace(/\r?\n[ \t]/g, "");
      return foldLine("LOCATION:" + transformLocation(unfolded));
    });

    return new Response(text, {
      headers: {
        "content-type": "text/calendar; charset=utf-8",
        "cache-control": "public, max-age=300",
        "content-disposition": 'inline; filename="calendar.ics"',
      },
    });
  },
};
