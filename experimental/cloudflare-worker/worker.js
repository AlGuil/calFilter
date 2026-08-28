/**
 * calFilter — proxy expérimental d'enrichissement des salles.
 *
 * Récupère le flux iCal officiel d'ADE en direct et réécrit chaque champ
 * LOCATION pour y ajouter l'aile (R1/R2/R3) et l'étage, absents de l'export
 * ADE (ex. "Amphi 2B" -> "R1 Amphi 2B (4e)").
 *
 * La table des salles est lue depuis rooms.json dans le dépôt (source unique) :
 * édite rooms.json + push, et cette table se met à jour toute seule ici (cache
 * ~1h). Plus besoin de re-coller ce worker.
 *
 * Déploiement : voir README.md de ce dossier.
 * Appel : https://<ton-worker>.workers.dev/?resources=9077,4125,50942&nbWeeks=52
 *
 * ⚠️ Expérimental : les agendas abonnés dépendent alors de la disponibilité de
 * ce worker (et non plus seulement de la fac).
 */

const ADE = "https://edt.uca.fr/jsp/custom/modules/plannings/anonymous_cal.jsp";
const ROOMS_URL = "https://raw.githubusercontent.com/AlGuil/calFilter/main/rooms.json";
const CACHE_TTL = 3600; // 1 h — flux ADE et rooms.json ne sont retéléchargés qu'~1x/h (mutualisé).

// Charge la table des salles depuis rooms.json (mise en cache 1h au bord Cloudflare).
// Renvoie { map: {nom: [aile, etage]}, keys: [...] }. En cas d'échec : table vide
// (le flux est alors renvoyé sans enrichissement, jamais cassé).
async function getRoomMap() {
  try {
    const r = await fetch(ROOMS_URL, { cf: { cacheTtl: CACHE_TTL, cacheEverything: true } });
    if (!r.ok) return { map: {}, keys: [] };
    const data = await r.json();
    const map = {};
    for (const x of data.rooms || []) map[x.nom] = [x.aile || "", x.etage || ""];
    const keys = Object.keys(map).sort((a, b) => b.length - a.length);
    return { map, keys };
  } catch (e) {
    return { map: {}, keys: [] };
  }
}

function makeEnricher(map, keys) {
  const enrich = (name) => {
    const t = name.trim();
    if (!t) return name;
    for (const key of keys) {
      if (t === key || t.startsWith(key + " ") || t.startsWith(key + "-")) {
        const [aile, etage] = map[key];
        let out = aile ? aile + " " + t : t;
        if (etage && !/\(\s*(RDC|\d)/.test(out)) out += " (" + etage + ")";
        return out;
      }
    }
    return name; // salle inconnue -> inchangée
  };
  // une LOCATION peut lister plusieurs salles, séparées par une virgule échappée "\,"
  return (value) => value.split("\\,").map(enrich).join("\\,");
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

    // flux ADE + table des salles en parallèle (les deux mis en cache 1h au bord)
    let feed, rooms;
    try {
      [feed, rooms] = await Promise.all([
        fetch(ade, { cf: { cacheTtl: CACHE_TTL, cacheEverything: true } }),
        getRoomMap(),
      ]);
    } catch (e) {
      return new Response("Flux ADE injoignable.", { status: 502, headers: { "content-type": "text/plain; charset=utf-8" } });
    }
    if (!feed.ok) {
      return new Response("Flux ADE indisponible (" + feed.status + ").",
        { status: 502, headers: { "content-type": "text/plain; charset=utf-8" } });
    }

    let text = await feed.text();
    const transformLocation = makeEnricher(rooms.map, rooms.keys);
    // réécrit chaque propriété LOCATION (en gérant le repliage de ligne)
    text = text.replace(/^LOCATION:((?:.*)(?:\r?\n[ \t].*)*)/gm, (_m, val) => {
      const unfolded = val.replace(/\r?\n[ \t]/g, "");
      return foldLine("LOCATION:" + transformLocation(unfolded));
    });

    return new Response(text, {
      headers: {
        "content-type": "text/calendar; charset=utf-8",
        "cache-control": "public, max-age=" + CACHE_TTL,
        "content-disposition": 'inline; filename="calendar.ics"',
      },
    });
  },
};
