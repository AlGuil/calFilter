# Proxy expérimental — aile (R1/R2/R3) dans le lieu du cours

⚠️ **Expérimental.** Ce proxy récupère le flux ADE **en direct** et réécrit
chaque `LOCATION` pour y ajouter l'aile et l'étage
(`Amphi 2B` → `R1 Amphi 2B (4e)`). Il ne stocke rien, ne met rien en cache
durablement (TTL 5 min), et une seule instance sert toute la promo.

## À savoir avant d'activer

- **Dépendance** : les agendas abonnés au proxy dépendent de **sa** disponibilité,
  pas seulement de la fac. S'il tombe (ou si tu arrêtes de le maintenir), les
  agendas de ceux qui l'utilisent ne se mettent plus à jour. L'URL ADE brute, elle,
  ne dépend que de la fac. À réserver à ceux qui veulent vraiment l'aile en clair.
- **Fiabilité de la donnée** : l'aile vient du plan UCA 2021, lue depuis
  `rooms.json` à la racine du dépôt (source unique, cache ~1h). Édite `rooms.json`
  + push : le worker se met à jour tout seul, **plus besoin de le re-coller**.
  Une salle inconnue est laissée telle quelle.

## Pourquoi Cloudflare et pas GitHub ?

GitHub **n'héberge pas** de fonction HTTP qui s'exécute à chaque requête :
- GitHub **Pages** = statique uniquement (ne peut pas aller chercher + transformer
  le flux à la volée) ;
- GitHub **Actions** = tâches planifiées (CI), pas un point d'accès qui répond en
  direct — seulement l'ancienne approche « gist mis à jour toutes les heures »,
  qu'on a écartée (périmé + ne passe pas à l'échelle).

Il n'y a donc pas d'équivalent GitHub à Cloudflare Workers pour un proxy en
direct. Cloudflare Workers offre **100 000 requêtes/jour gratuites** (largement
suffisant). Alternatives équivalentes si besoin : Val.town, Deno Deploy.

## Déployer (compte Cloudflare gratuit)

### Étape 0 — créer le compte
1. Va sur **https://dash.cloudflare.com/sign-up**.
2. Email + mot de passe → valide l'email. C'est gratuit, aucune carte demandée
   pour le plan Workers gratuit.

### Option A — en ligne de commande (recommandé)

```bash
npm install -g wrangler      # une fois
wrangler login               # ouvre le navigateur, connexion Cloudflare
cd experimental/cloudflare-worker
wrangler deploy
```

Wrangler affiche l'URL publique, du type
`https://calfilter.<ton-sous-domaine>.workers.dev`.

### Option B — sans CLI (dashboard)

1. dash.cloudflare.com → **Workers & Pages** → **Create** → **Worker**.
2. Remplace le code par défaut par le contenu de [`worker.js`](worker.js), **Deploy**.
3. Récupère l'URL `…workers.dev` du worker.

## Brancher à la page

Dans [`../../index.html`](../../index.html), renseigne la constante :

```js
const PROXY_BASE = "https://calfilter.<ton-sous-domaine>.workers.dev";
```

L'option « 🧪 Expérimental — aile dans le lieu » s'active alors dans l'onglet
Calendrier ; le lien généré pointe vers le proxy au lieu d'ADE.

## Tester

```
https://<ton-worker>.workers.dev/?resources=9077,4125,50942&nbWeeks=52
```

Doit renvoyer un `.ics` où les `LOCATION` portent l'aile et l'étage.

## Paramètres acceptés

| Param | Défaut | Rôle |
|---|---|---|
| `resources` | *(obligatoire)* | IDs de ressources, séparés par des virgules |
| `nbWeeks` | `52` | horizon (fenêtre glissante) |

Les autres paramètres ADE (`projectId`, `calType`, `displayConfigId`) sont fixés
par le worker.
