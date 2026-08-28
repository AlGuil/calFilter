# Structure du flux et vocabulaire (référence)

Ce document décrit le **contenu texte** des cours, utile pour écrire l'affinage
optionnel (`keep_only` / `exclude`) de `filters.yaml`. Pour le tri principal par
**ressources**, voir plutôt [RESSOURCES.md](RESSOURCES.md).

## Ressources vs contenu

Deux niveaux d'information :

- **Ressources** (`resources=<id>` dans l'URL) : le tri principal. Chaque
  ressource correspond à un groupe et renvoie un paquet complet. C'est propre et
  robuste — voir [RESSOURCES.md](RESSOURCES.md).
- **Contenu de chaque cours** (`SUMMARY`, `DESCRIPTION`) : ce qu'on lit pour
  l'affinage fin (retirer un cours, une date…). Un `VEVENT` **ne contient aucun
  identifiant de ressource ni de groupe structuré** : le groupe est du texte
  libre. D'où le vocabulaire ci-dessous.

## Anatomie d'un cours (`VEVENT`)

```
SUMMARY:CM - UE 3 Dysfonctionnement cellulaire      <- type + UE
LOCATION:Amphi 4                                    <- salle
DESCRIPTION:\n\nPHI 2 DFGSP 2\nGUEIRARD PASCALE\n\n(Updated :23/07/2026 16:05)
             ^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^
             groupe            intervenant
```

- **`SUMMARY`** : commence par le **type** (`CM`, `TD`, `TP`, `ED`, `CC`…),
  éventuellement suivi d'un numéro (`TP3-`, `ED1`, `TP2/3`), puis l'UE.
- **`DESCRIPTION`** : lignes séparées par `\n`. On y trouve le **groupe** et
  l'**intervenant** (dans un ordre variable), plus une ligne `(Updated …)`.

## Types de cours × groupes réellement présents

Relevé sur un export de 8 semaines (230 cours). À réactualiser si la fac change
ses conventions.

| Type | Groupes rencontrés dans la description |
|---|---|
| **CM** | `PHI 2 DFGSP 2` (promo entière) ; qq CM `Groupe 1/2 MISE A NIVEAU` (UE 11) |
| **ED** | `Groupe A` / `Groupe B` / `Groupe C` (ED réguliers) ; `Groupe 1/2 MISE A NIVEAU` (UE 12 remise à niveau) |
| **TD** | **uniquement** `Groupe 1/2 MISE A NIVEAU` (UE 11 remise à niveau) + 1 Herbier |
| **TP** | `Groupe 1` … `Groupe 5` (+ Herbier, Risque AVF) |
| **CC** | `Groupe 1/2 MISE A NIVEAU`, `PHI 2 DFGSP 2` |
| **SEANCE POP** | `Groupe POP` |
| **OBLIGATOIRE / Rencontres** | `PHI 2 DFGSP 2` (+ autres promos pour les rencontres) |

### Points d'attention

- **TD ≡ ED** dans cette fac. Les seuls cours notés `TD` sont la remise à niveau
  (UE 11) ; les enseignements dirigés des autres UE sont notés `ED`.
- La **remise à niveau** couvre deux UE : **UE 11** (notée `TD`) et **UE 12**
  (notée `ED`). Ses groupes sont `Groupe 1 MISE A NIVEAU` / `Groupe 2 MISE A NIVEAU`.
- Les **ED réguliers** utilisent des lettres (`Groupe A/B/C`), les **TP** des
  chiffres (`Groupe 1`…`5`). Pour l'étudiant du profil `alban`, groupe **2** ≡
  groupe **B**.
- `group_contains: "Groupe 2"` attrape aussi `Groupe 2 MISE A NIVEAU` (sous-chaîne).
  Combine avec `type` et `summary_contains` pour cibler précisément.

## Autres UE / cours notables (non filtrés par défaut)

Si tu veux les ajouter au profil un jour :

- `CC` / `UE 11 - CC …` : contrôles continus (remise à niveau, chimie, biophysique).
- `SEANCE POP`, `Rencontres PRO OFFICINE`, `OBLIGATOIRE - …` : événements ponctuels.
- UE régulières vues : UE 1 (techniques/gestes), UE 2 (bio végétale/fongique),
  UE 3 (dysfonctionnement cellulaire), UE 4 (voies d'accès), UE 5 (physiologie),
  UE 6 (infectiologie), UE 7 (biochimie), UE 8 (sciences analytiques),
  UE Endocrinologie, UE Physiologie des régulations, UE Herbier.
