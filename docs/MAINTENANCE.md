# Mise à jour — semestre 2, changement de groupe, année suivante

Guide de ce qu'il faut faire (ou pas) quand l'emploi du temps évolue.

---

## ✅ Ce qui se met à jour tout seul — rien à faire

- **Les cours du semestre 2** apparaissent automatiquement dès que la fac les
  publie : le flux est en direct et la fenêtre est glissante (`nbWeeks=52`).
  Aucune manip, aucun réabonnement.
- **Les abonnements déjà pris** (Google/Apple/Outlook) continuent de marcher :
  l'URL ne change pas.
- **Le site et le worker** lisent [`../rooms.json`](../rooms.json) en direct
  (worker : cache ~1 h). Éditer ce fichier + `git push` suffit.

Autrement dit : si rien ne change côté groupes/ressources ni salles, **il n'y a
rien à faire** pour le S2.

---

## 📋 Quand le semestre 2 sort — check en 3 points

### 1. Vérifier que les ressources (groupes) n'ont pas changé

La fac peut renuméroter ses ressources entre semestres. On re-sonde et on compare
à [RESSOURCES.md](RESSOURCES.md) :

```bash
python scripts/probe_resources.py --weeks 30
```

- Si les IDs → groupes correspondent toujours (TP gr.3 = `4125`, ED gr.B = `9077`,
  etc.) : **rien à changer**.
- Si un ID a changé ou un nouveau groupe/option apparaît : mettre à jour la
  constante `SECTIONS` dans [`../index.html`](../index.html) (et RESSOURCES.md),
  puis `git push`.

> Si c'est **ton** groupe qui change au S2 (ex. tu passes en TP gr.2) : rien à
> coder — tu re-coches dans le picker et tu te réabonnes avec le nouveau lien.
> Pareil pour tes camarades.

### 2. Ajouter les nouvelles salles à `rooms.json`

Le S2 peut utiliser des salles absentes de `rooms.json` : elles s'afficheront
sans aile/étage (annuaire) et non enrichies (worker). Pour lister les salles du
flux et repérer les nouvelles :

```bash
curl -s "https://edt.uca.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=4029&projectId=4&calType=ical&displayConfigId=128&nbWeeks=30" \
  | grep '^LOCATION:' | sed 's/^LOCATION://' | sort -u
```

(`4029` = toutes les ressources de la promo, pour voir un maximum de salles.)

Pour chaque salle **absente** de `rooms.json`, ajouter une entrée :

```json
{"nom": "Salle 612", "etage": "6e", "aile": "", "repere": ""}
```

- `nom` : **exactement** le nom court affiché (sans le suffixe « - TP … »).
- `etage` : déduit du numéro (`6xx` → `6e`, etc.).
- `aile` : `R1`/`R2`/`R3` si connue via le plan, sinon `""`.

Puis `git push`. Le site et le worker se mettent à jour tout seuls (worker sous
~1 h). **Pas besoin de re-coller le worker.**

### 3. (Rare) Nouveau plan de la fac

Si la fac diffuse un nouveau plan des salles :

```bash
# remplacer plan-salles.pdf par le nouveau, puis :
brew install poppler        # si pas déjà installé
pdftoppm -png -r 150 plan-salles.pdf assets/plan   # regénère assets/plan-1.png et plan-2.png
```

`git push`. (Vérifier les ailes dans `rooms.json` si des salles ont bougé.)

---

## Autres cas courants

| Situation | Quoi faire |
|---|---|
| Mon groupe change | Re-cocher dans le picker + se réabonner. Rien à coder. |
| Ajouter un·e ami·e d'un autre groupe | Il/elle coche **ses** groupes dans le picker et prend **son** lien. Rien à faire. |
| Compléter/corriger une aile | Éditer `rooms.json` + `git push`. |
| Changer la fréquence/l'horizon | `nbWeeks` par défaut dans `index.html` (et le worker lit `nbWeeks` de l'URL). |

---

## Deux promos : le sélecteur DFGSP 2 / DFGSP 3

Le picker propose un menu **« Ta promo »** (2e / 3e année) qui bascule les groupes
affichés. Les deux jeux de ressources vivent dans la constante **`PROMOS`** de
[`../index.html`](../index.html) (`PROMOS["2"]` = DFGSP2, `PROMOS["3"]` = DFGSP3) ;
chacun porte ses `sections`, sa ressource `cm` (CM de promo seuls) et son `cmName`.
Le lien produit reste unique et partageable, et la 2e année est inchangée.

Pour re-sonder une promo précise (si la fac renumérote) :

```bash
python scripts/probe_resources.py --promo 3 --weeks 30   # DFGSP3
python scripts/probe_resources.py --promo 2 --weeks 30   # DFGSP2 (défaut)
```

> ⚠️ En DFGSP3, la fac **n'étiquette plus le n° de groupe** dans les TP/ED du flux
> (voir [RESSOURCES.md](RESSOURCES.md)). Les libellés TP (1–5) et ED (A/B/C) sont
> donc attribués **dans l'ordre des ressources** ; le picker affiche « vérifie tes
> dates ». Si la fac change cet ordre, corrige le mapping dans `PROMOS["3"]`.

## Où est quoi

| Quoi | Fichier |
|---|---|
| Groupes / ressources (picker) | `index.html` → `PROMOS` · [RESSOURCES.md](RESSOURCES.md) |
| Salles (aile/étage) | [`../rooms.json`](../rooms.json) — **source unique** |
| Proxy expérimental (aile dans le lieu) | `experimental/cloudflare-worker/` |
| Re-cartographier les ressources | `scripts/probe_resources.py` |
| Ancien back-end (non utilisé) | `legacy/` |

---

## Checklist express « le S2 est sorti »

- [ ] `python scripts/probe_resources.py --weeks 30` → les IDs de groupes n'ont pas bougé
- [ ] (si besoin) mettre à jour `SECTIONS` dans `index.html` + RESSOURCES.md
- [ ] Lister les salles du flux → ajouter les nouvelles à `rooms.json`
- [ ] `git push`
- [ ] Rien à faire pour : les abonnements existants, le worker, GitHub Pages
