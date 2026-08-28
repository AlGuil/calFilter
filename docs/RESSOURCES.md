# Cartographie des ressources (identifiants de l'URL)

Obtenue en interrogeant **chaque `resources=<id>` isolément** (voir la méthode en
bas). Contrairement à ce qu'on pensait d'abord, on **peut** trier par ressources :
chaque ressource « groupe » est un paquet complet et fidèle.

## À retenir

- **Chaque ressource renvoie toujours les ~76 CM communs de la promo**
  (`PHI 2 DFGSP 2`) **plus** sa partie spécifique. Les CM de promo viennent donc
  « gratuitement » avec n'importe quelle ressource, et sont dédoublonnés quand on
  combine plusieurs ressources (par `UID`).
- Une ressource de groupe est **tout ou rien** : on prend tout le paquet du
  groupe, on ne peut pas retrancher un cours précis via l'URL (ça, c'est le rôle
  de l'affinage Python optionnel).

## Ressources utiles (promo DFGSP 2)

### Travaux pratiques (TP) — groupes chiffrés
| Ressource | Groupe |
|---|---|
| `4114` | TP Groupe 1 |
| `4116` | TP Groupe 2 |
| `4125` | TP Groupe 3 |
| `4127` | TP Groupe 4 |
| `5644` | TP Groupe 5 |
| `4110` | **Tous** les TP (tous groupes) |

### Enseignements dirigés (ED / « TD » des UE régulières) — groupes lettrés
| Ressource | Groupe |
|---|---|
| `9078` | ED Groupe A |
| `9077` | ED Groupe B |
| `9079` | ED Groupe C |
| `4109` | **Tous** les ED (tous groupes) |

### Remise à niveau (UE 11 en « TD » + UE 12 en « ED » + CC)
| Ressource | Groupe |
|---|---|
| `50941` | Remise à niveau Groupe 1 |
| `50942` | Remise à niveau Groupe 2 |
| `51288` | Remise à niveau (paquet complet, TD:20 / ED:14) |

### UE optionnelles / thématiques (à vérifier selon inscription)
| Ressource | Contenu |
|---|---|
| `6125`, `6126` | Risque A.V.F. |
| `6127` | Physiologie (option) |
| `6130` | Endocrinologie (option) |
| `6139` | Herbier |

### Autres
| Ressource | Contenu |
|---|---|
| `4029` | **TOUT** (promo complète, tous groupes — 369 évts) |
| `48538`, `38837`, `51289`, `51290`, `54153`, `60862`, `60863`, `61318`, `61319`, `63997`–`64001` | Séances **POP** (une par groupe POP) |
| `51292`–`51303` | Groupes « POP » numérotés (I à IX) — 76 CM + 1 séance |
| `4321`, `4382`, `4385`–`4388`, `51291`, `51303`, `60524`–`60530` | **Génériques** : uniquement les CM de promo (aucun apport de groupe) |
| `34457` | Vide (aucun cours) |

> Les libellés « UE optionnelles » et « POP » sont déduits du contenu ; à
> confirmer avec le secrétariat si tu comptes t'y fier pour une option précise.

## Recette pour le profil `alban`

Besoins → ressources :

| Besoin | Ressource |
|---|---|
| Cours de promo (`PHI 2 DFGSP 2`) | *(inclus dans n'importe quelle ressource)* |
| CM + TD/ED remise à niveau **groupe 2** (+CC/partiels) | `50942` |
| TP **groupe 3** | `4125` |
| ED **groupe B** | `9077` |

URL correspondante (paramètre `resources=9077,4125,50942`). Vérifié : donne
**exactement** les cours attendus (superset de 106 + 5 contrôles continus de
remise à niveau).

## Méthode (reproductible)

Script : `scripts/probe_resources.py` (interroge chaque ID isolément, agrège
types/groupes/UE). Relancer si la fac renumérote ses ressources d'une année sur
l'autre. Augmenter `nbWeeks` si une ressource ne renvoie pas assez de cours pour
être identifiée.
