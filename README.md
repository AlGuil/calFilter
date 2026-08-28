# calFilter

Une page web qui te fabrique l'URL de **ton** emploi du temps à partir du
calendrier officiel de la fac (ADE / UCA) : tu coches tes groupes, tu obtiens un
lien d'abonnement filtré. **Aucun serveur, aucune maintenance** — c'est la fac
qui met le calendrier à jour, ton agenda se resynchronise tout seul.

👉 **[Ouvrir le picker](index.html)** (une fois publié sur GitHub Pages, l'URL
sera `https://<ton-user>.github.io/calFilter/`).

## Pourquoi si simple ?

Le flux ADE de la fac se trie **entièrement via les ressources de l'URL**
(`resources=<id>,<id>…`) : chaque ressource correspond à un groupe précis, et le
serveur de la fac génère le calendrier en direct. Donc :

- pas besoin de télécharger/re-publier quoi que ce soit — l'URL ADE **est** déjà
  un flux hébergé et tenu à jour par la fac ;
- « filtrer » = choisir les bons IDs de ressources ;
- le seul point pénible (trouver ses IDs) est réglé par le picker, qui affiche
  les groupes en clair et génère l'URL.

La cartographie des ressources est dans [docs/RESSOURCES.md](docs/RESSOURCES.md).

## Utiliser le picker

1. Ouvre la page.
2. Coche ton groupe de TP, ton groupe d'ED, ta remise à niveau, tes options.
   (Les CM communs de la promo sont inclus automatiquement.)
3. **Copie le lien** ou clique **S'abonner (webcal)**.
4. Ajoute-le comme calendrier **par abonnement** (pas un import ponctuel) :
   - Google Agenda : *Autres agendas → À partir de l'URL*.
   - Apple/iPhone : le bouton « S'abonner » ouvre la fenêtre d'abonnement.
   - Outlook : *Ajouter un calendrier → S'abonner à partir du web*.

La page inclut aussi un **répertoire de salles** cherchable (« Où sont les
salles ? ») : l'export ADE ne donne que le nom court (`Amphi 2B`), le répertoire
indique l'aile (R1/R2/R3), l'étage et le surnom — utile pour les nouveaux
étudiants. Détails et maintenance : [docs/SALLES.md](docs/SALLES.md).

## Publier sur GitHub Pages (une fois)

*Settings → Pages → Build and deployment → Source : **Deploy from a branch***,
branche `main`, dossier `/ (root)`. Au bout d'une minute la page est en ligne à
`https://<ton-user>.github.io/calFilter/`. C'est cette URL que tu partages.

## Adapter les ressources

Le picker couvre **deux promos** via un sélecteur « Ta promo » (2e / 3e année).
Les IDs vivent dans [index.html](index.html) (constante `PROMOS`, avec `PROMOS["2"]`
= DFGSP 2 et `PROMOS["3"]` = DFGSP 3) et sont cartographiés dans
[docs/RESSOURCES.md](docs/RESSOURCES.md) — valables pour l'année **2026-2027**. Si
la fac renumérote ses ressources, régénère la correspondance :

```bash
python scripts/probe_resources.py --promo 3 --weeks 30
```

Le script interroge chaque ressource isolément et affiche son groupe/contenu.
Reporte les nouveaux IDs dans `PROMOS` (dans `index.html`). En DFGSP 3, la fac
n'étiquette plus le n° de groupe dans le flux : les libellés TP/ED sont attribués
dans l'ordre des ressources (voir la note dans `docs/RESSOURCES.md`).

## Partager avec tes camarades

Envoie-leur simplement l'URL de la page. Chacun coche **ses** groupes et récupère
**son** lien. Rien à installer, rien à configurer par personne.

## Structure du dépôt

```
index.html                     ← le picker + répertoire des salles (tout est là)
rooms.json                     ← source unique des salles (aile/étage), éditable
docs/RESSOURCES.md             ← cartographie des ressources (ID → groupe)
docs/SALLES.md                 ← localisation des salles (aile/étage/amphi)
docs/MAINTENANCE.md            ← quoi faire quand le S2 sort / màj groupes & salles
docs/FLUX.md                   ← structure/vocabulaire du flux ADE
scripts/probe_resources.py     ← re-cartographier les ressources
experimental/cloudflare-worker ← proxy optionnel : aile R1/R2/R3 dans le lieu
legacy/                        ← ancien back-end (Python/gist/workflow), parqué
```

## Option expérimentale : l'aile (R1/R2/R3) dans le lieu du cours

L'export ADE ne donne que le nom court de la salle (`Amphi 2B`). Un petit
**proxy Cloudflare Worker** (gratuit) peut récupérer le flux en direct et
réécrire chaque lieu en `R1 Amphi 2B (4e)`. Une fois déployé, renseigne son URL
dans `PROXY_BASE` (en haut du script de `index.html`) : l'option « 🧪
Expérimental » s'active alors dans l'onglet Calendrier.

⚠️ **À savoir** : activer l'option fait dépendre les agendas abonnés de la
disponibilité de ce proxy (et plus seulement de la fac). Réservé à ceux qui
veulent vraiment l'aile en clair. Tout est dans
[experimental/cloudflare-worker/](experimental/cloudflare-worker/README.md).

## Et le back-end d'avant ?

Une première version passait par un back Python + Gist + workflow horaire + mail.
On l'a **abandonné** : la fac fait déjà les mises à jour, donc ce back ne faisait
que recréer un problème qu'il devait ensuite surveiller. Il est conservé dans
[legacy/](legacy/) au cas où un besoin d'**exclusion fine** (sauter une semaine,
retirer un cours précis) deviendrait un jour incontournable — ce que les
ressources seules ne savent pas faire. Voir [legacy/README.md](legacy/README.md).
