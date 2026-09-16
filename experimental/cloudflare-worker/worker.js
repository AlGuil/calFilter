/**
 * calFilter — proxy expérimental d'enrichissement des salles.
 *
 * Récupère le flux iCal officiel d'ADE en direct et réécrit chaque champ
 * LOCATION pour y ajouter l'aile (R1/R2/R3) et l'étage, absents de l'export
 * ADE (ex. "Amphi 2B" -> "R1 Amphi 2B (4e)").
 *
 * Mode redoublant (param `keep`) : ne conserve que les VEVENT dont le SUMMARY
 * correspond à l'une des matières demandées. `keep` = tokens normalisés séparés
 * par « | » (ex. "ue 7|anglais"). Sans `keep`, le flux n'est pas filtré.
 *
 * Filtre de sous-groupe (param `group`) : pour les ressources qui mélangent
 * plusieurs sous-groupes non séparables côté ADE (ex. Officine DFASP2 : « G 1 » /
 * « G 2 » marqués seulement dans la DESCRIPTION). Ne conserve que les VEVENT sans
 * marqueur de groupe (cours communs) OU marqués du/des groupe(s) demandé(s).
 * `group` = marqueurs séparés par « | » (ex. "G 1"). Sans `group`, aucun filtrage.
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

// Comptage d'usage anonyme. On dérive un hash SHA-256 de la liste de ressources
// (normalisée : triée, dédoublonnée). Deux personnes du même groupe -> même hash ;
// une même personne sur 2 appareils -> même hash. Aucune IP, aucun cookie, rien de
// personnel : les ressources sont de simples IDs de groupes. Le hash sert de clé
// pour compter les sélections distinctes actives (plancher du nombre de personnes).
async function hashResources(resources) {
  const norm = [...new Set(resources.split(",").map(s => s.trim()).filter(Boolean))]
    .sort().join(",");
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(norm));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}

// Écrit un point dans Analytics Engine (si le binding USAGE existe), sans bloquer
// la réponse. blob1 = hash (clé distincte) ; blob2 = ressources brutes (IDs de
// groupes, non personnels, pour voir les combinaisons populaires) ; blob3 = nbWeeks.
function recordUsage(env, ctx, resources, weeks) {
  if (!env || !env.USAGE) return;
  const task = (async () => {
    try {
      const h = await hashResources(resources);
      env.USAGE.writeDataPoint({
        indexes: [h.slice(0, 32)],
        blobs: [h, resources, String(weeks)],
        doubles: [1],
      });
    } catch (e) { /* le comptage ne doit jamais casser le flux */ }
  })();
  if (ctx && ctx.waitUntil) ctx.waitUntil(task);
}

// --- Filtrage « mode redoublant » -------------------------------------------
// Normalise un libellé de cours pour la comparaison : minuscules, accents
// retirés, « UE8 »/« UE 8 » ramenés à « ue 8 », espaces compactés. Doit rester
// identique à normSum() côté index.html.
function normSum(s) {
  return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/ue\s*(\d+)/g, "ue $1").replace(/\s+/g, " ").trim();
}

// Un token « ue N » ne matche que ce numéro exact (« ue 1 » n'attrape pas
// « ue 11 ») ; tout autre token est une simple sous-chaîne (ex. "anglais").
function summaryMatches(summary, tokens) {
  const n = normSum(summary);
  for (const t of tokens) {
    const m = /^ue (\d+)$/.exec(t);
    if (m) { if (new RegExp("ue " + m[1] + "(?!\\d)").test(n)) return true; }
    else if (n.includes(t)) return true;
  }
  return false;
}

// Retire chaque VEVENT dont le SUMMARY ne correspond à aucun token. Le reste du
// flux (VCALENDAR, VTIMEZONE, en-têtes) est laissé intact.
function filterBySummary(text, tokens) {
  const lines = text.split(/\r?\n/);
  const out = [];
  let block = null;
  for (const line of lines) {
    if (line === "BEGIN:VEVENT") { block = [line]; continue; }
    if (block) {
      block.push(line);
      if (line === "END:VEVENT") {
        const u = [];                    // déplie les lignes repliées du bloc
        for (const l of block) {
          if ((l[0] === " " || l[0] === "\t") && u.length) u[u.length - 1] += l.slice(1);
          else u.push(l);
        }
        let summary = "";
        for (const l of u) {
          if (/^SUMMARY[;:]/.test(l)) { summary = l.slice(l.indexOf(":") + 1); break; }
        }
        if (summaryMatches(summary, tokens)) for (const l of block) out.push(l);
        block = null;
      }
      continue;
    }
    out.push(line);
  }
  return out.join("\r\n");
}

// --- Filtrage par sous-groupe (marqueur dans la DESCRIPTION) -----------------
// Normalise un marqueur de groupe : minuscules, espaces retirés (« G 1 » -> « g1 »).
function normGroup(s) {
  return s.toLowerCase().replace(/\s+/g, "");
}

// Marqueurs de groupe présents dans une DESCRIPTION : lignes valant exactement
// « G <n> » (séparateur iCal « \n » littéral). Renvoie ["g1"], ["g2"], ... ou [].
function eventGroups(desc) {
  return desc.split("\\n").map((p) => normGroup(p.trim()))
    .filter((p) => /^g\d+$/.test(p));
}

// Retire chaque VEVENT marqué d'un groupe autre que ceux demandés. Un VEVENT sans
// marqueur (cours commun) est toujours conservé. `wanted` = ["g1", ...].
function filterByGroup(text, groups) {
  const wanted = new Set(groups.map(normGroup));
  const lines = text.split(/\r?\n/);
  const out = [];
  let block = null;
  for (const line of lines) {
    if (line === "BEGIN:VEVENT") { block = [line]; continue; }
    if (block) {
      block.push(line);
      if (line === "END:VEVENT") {
        const u = [];                    // déplie les lignes repliées du bloc
        for (const l of block) {
          if ((l[0] === " " || l[0] === "\t") && u.length) u[u.length - 1] += l.slice(1);
          else u.push(l);
        }
        let desc = "";
        for (const l of u) {
          if (/^DESCRIPTION[;:]/.test(l)) { desc = l.slice(l.indexOf(":") + 1); break; }
        }
        const evg = eventGroups(desc);
        if (evg.length === 0 || evg.some((g) => wanted.has(g)))
          for (const l of block) out.push(l);
        block = null;
      }
      continue;
    }
    out.push(line);
  }
  return out.join("\r\n");
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
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const resources = url.searchParams.get("resources");
    if (!resources) {
      return new Response("Paramètre 'resources' manquant.\nEx: ?resources=9077,4125,50942&nbWeeks=52",
        { status: 400, headers: { "content-type": "text/plain; charset=utf-8" } });
    }
    const weeks = url.searchParams.get("nbWeeks") || "52";
    // Mode redoublant : liste de matières à garder (tokens normalisés, séparés « | »).
    const keepTokens = (url.searchParams.get("keep") || "")
      .split("|").map((t) => normSum(t)).filter(Boolean);
    // Filtre de sous-groupe (marqueurs « G N » de la DESCRIPTION, séparés « | »).
    const groupFilters = (url.searchParams.get("group") || "")
      .split("|").map((g) => g.trim()).filter(Boolean);

    // Comptage anonyme (n'ajoute aucune latence : s'exécute après la réponse).
    recordUsage(env, ctx, resources, weeks);
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
    // Filtrages (avant l'enrichissement des salles) : sous-groupe puis matières.
    if (groupFilters.length) text = filterByGroup(text, groupFilters);
    if (keepTokens.length) text = filterBySummary(text, keepTokens);
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
