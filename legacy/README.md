# legacy/ — back-end parqué (non utilisé)

Ce dossier contient la première approche : un back-end Python qui téléchargeait
le flux, le filtrait, le republiait dans un Gist via un workflow horaire, avec
alerte mail en cas d'échec.

**Il n'est plus utilisé.** On a découvert que le tri se fait entièrement en
choisissant les bonnes ressources dans l'URL ADE, et que le serveur de la fac
met déjà le calendrier à jour en temps réel. Un back-end de notre côté ne servait
donc qu'à recréer (et surveiller) un problème qu'il était seul à introduire.

Le produit actuel est la page statique [`../index.html`](../index.html) (picker
de ressources), qui génère directement l'URL officielle ADE.

## Quand ressortir ce code ?

Uniquement si un besoin que les ressources ne savent **pas** exprimer devient
incontournable :
- exclure une plage de dates précise (ex. sauter une semaine) ;
- retirer un cours particulier par son intitulé ;
- fusionner/nettoyer des flux de sources différentes.

Dans ce cas, le moteur hybride (`calfilter/`) sait déjà faire tout ça : voir
`filters.yaml` (clés `keep_only`, `exclude`, `date_from`/`date_to`) et le
workflow `.github/workflows/update.yml` à remettre à la racine.

Contenu :
- `calfilter/` — moteur (fetch → sélection ressources → affinage → réémission)
- `filters.yaml` — config à profils (ressources + affinage)
- `tests/` — tests du moteur
- `requirements.txt` — dépendances Python
- `.github/workflows/update.yml` — workflow horaire + publication Gist + mail
