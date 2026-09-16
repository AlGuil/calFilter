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

## Ressources utiles (promo DFGSP 3)

Sondées de la même façon (chaque `resources=<id>` isolément). **Promo commune :
`PHI 3 DFGSP 3`** (~98 CM), incluse dans *toutes* les ressources — donc « gratuite »
comme en 2e année.

> ⚠️ **Différence majeure avec la 2e année :** le flux DFGSP3 **ne met plus le
> n° de groupe dans la `DESCRIPTION`** des TP/ED (tout est marqué `PHI 3 DFGSP 3`).
> On sait donc qu'il y a **5 groupes de TP** et **3 groupes d'ED** (5 emplois du
> temps distincts pour les TP, 3 pour les ED), mais **le flux ne dit pas laquelle
> des ressources = « Groupe 1 »**. Seuls l'**Anglais** et l'« ED GROUPE TP - UE 11 »
> portent un `Groupe N` explicite. Les libellés TP (1–5) et ED (A/B/C) du picker
> sont donc attribués **dans l'ordre des ressources** — d'où la consigne affichée
> « vérifie que les dates correspondent à ton groupe ».

### Travaux pratiques (TP) — 5 groupes
| Ressource | Groupe (picker) | Remarque |
|---|---|---|
| `45999` | Groupe 1 | inclut les **TP d'officine** (UE 13 PO, Salle 001) |
| `46000` | Groupe 2 | inclut les **TP d'officine** (UE 13 PO, Salle 001) |
| `46001` | Groupe 3 | |
| `46002` | Groupe 4 | |
| `46003` | Groupe 5 | |
| `4130` | **Tous** les TP (tous groupes) | |

### Anglais (UE 10) — 5 groupes **étiquetés** par la fac
| Ressource | Groupe |
|---|---|
| `8172` | Groupe 1 |
| `8171` | Groupe 2 |
| `8169` | Groupe 3 |
| `7847` | Groupe 4 |
| `8197` | Groupe 5 |
| `6678` | **Tous** les groupes d'Anglais |

> Le picker expose **TP et Anglais en sections séparées** : le groupe d'anglais peut
> différer du groupe de TP. L'Anglais est étiqueté « Groupe N » dans le flux (fiable),
> contrairement aux TP dont la numérotation est déduite de l'ordre des ressources.

### Enseignements dirigés (ED / TD) — 3 groupes (non étiquetés)
| Ressource | Groupe (picker) |
|---|---|
| `9084` | Groupe A |
| `9085` | Groupe B |
| `9086` | Groupe C |
| `6660` | **Tous** les ED (3 groupes) |

Contenu ED/TD : UE 1 Biochimie, UE 2 Physiologie, UE 3 Hémato, UE 6 Chimie
thérapeutique/Pharmaco, UE 7 Toxico, UE 9 Biopharmacie, UE 12 Numérique en santé.

### Parcours / filière de 3e année
| Ressource | Parcours | Contenu |
|---|---|---|
| *(aucune ressource isolée)* | **Officine** | UE 13 « PO » — **déjà inclus** dans les TP groupes 1 et 2 (`45999`/`46000`). Pas de ressource séparée : le picker le montre pour mémoire, sans ajout. |
| `63702` | **Industrie** | UE 14 Procédés Industriels (5 ED) |
| `6415` | **Internat** | UE 15 INTERNAT (2 ED) |
| `6413` | Industrie **+** Internat | UE 14 + UE 15 combinées |

### Génériques / autres
| Ressource | Contenu |
|---|---|
| `4030` | **TOUT** (promo complète, tous groupes/parcours — 309 évts) |
| `46006` (et la plupart des IDs de la promo) | **CM de promo seuls** (aucun apport de groupe) — utilisé par le picker pour « Ajouter les CM de promo seuls » |
| `19`,`20`,`32`,`40`,`42` | Marqueur « ED GROUPE TP - UE 11 » des groupes 1→5 (une séance ; sert à confirmer la numérotation des groupes de TP) |

> **Liste complète des ressources DFGSP3** (relevée depuis l'URL de la fac) : voir
> la constante `RESOURCES_DFGSP3` dans `scripts/probe_resources.py`.

## Ressources utiles (promo DFASP 1 — 4e année)

Sondées de la même façon (chaque `resources=<id>` isolément). **Promo commune :
`PHI 4 DFASP 1`** (~53 CM + 3 TD communs + « Rencontres »), incluse dans *toutes*
les ressources — donc « gratuite » comme aux autres années.

> ✅ **Différence favorable avec la 3e année :** le flux DFASP1 **remet le n° de
> groupe dans la `DESCRIPTION`** — « **Gpe N** » pour les TP, « **Groupe N** » pour
> l'anglais, « **Groupe A/B/C** » pour les ED. L'affectation des libellés du picker
> est donc **fiable** (pas de « vérifie tes dates » comme en 3e année).

### Travaux pratiques (TP) — 5 groupes **étiquetés** (« Gpe N »)
Contenu : TP UE 1 EC 1 (Stratégies anti-infectieuses) + TP UE 3 (Toxicologie).
| Ressource | Groupe |
|---|---|
| `7483` | Gpe 1 |
| `7484` | Gpe 2 |
| `7485` | Gpe 3 |
| `7486` | Gpe 4 |
| `48353` | Gpe 5 |
| `7482` | **Tous** les TP (5 groupes) |

### Anglais (UE 8) — 5 groupes **étiquetés** (« Groupe N »)
| Ressource | Groupe |
|---|---|
| `5053` | Groupe 1 |
| `5054` | Groupe 2 |
| `5055` | Groupe 3 |
| `5056` | Groupe 4 |
| `5309` | Groupe 5 |
| `4208` | **Tous** les groupes d'Anglais |

> Le picker expose **TP et Anglais en sections séparées** : le groupe d'anglais peut
> différer du groupe de TP, et chacun est étiqueté indépendamment dans le flux
> (« Gpe N » pour les TP, « Groupe N » pour l'anglais).

### Enseignements dirigés (ED / TD) — 3 groupes **étiquetés** (A/B/C)
| Ressource | Groupe |
|---|---|
| `3824` | Groupe A |
| `8824` | Groupe B |
| `49424` | Groupe C |
| `4137` | **Tous** les ED (3 groupes) |

Contenu ED/TD : UE 2 Cardiovasculaire, UE 3 Toxicologie spécialisée, UE 6
Oncologie, UE 7 Biothérapies…

### UE de pré-orientation / parcours (selon inscription)
| Ressource | UE | Contenu |
|---|---|---|
| `7487` | UE 10 | Pré-orientation officine (« Journée officinale ») |
| `7489` | UE 11 | Échantillons biologiques (+ 1 visite labo) |
| `9075` | UE 12 | Développement de substances d'origine végétale (CM + TD) |
| `3705` | — | Les trois UE 10 + 11 + 12 réunies |

### Génériques / autres
| Ressource | Contenu |
|---|---|
| `4055` | **TOUT** (promo complète, tous groupes/parcours — 207 évts) |
| `51137` (et la plupart des IDs de la promo, 59 évts, `nonpromo=0`) | **CM de promo seuls** — utilisé par le picker pour « Ajouter les CM de promo seuls » |
| `47812`, `62644`–`62653` | Séances **POP** (une ressource par groupe POP ; « Groupe POP » non numéroté dans le flux — non exposé dans le picker) |
| `34125` | Vide (aucun cours) |

> **Liste complète des ressources DFASP1** (relevée depuis l'URL de la fac) : voir
> la constante `RESOURCES_DFASP1` dans `scripts/probe_resources.py`.

## Ressources utiles (promo DFASP 2, 5e année)

La 5e année **n'est pas organisée par groupes de TP** mais **par parcours**
(filière). L'URL fournie par la fac ne contient que 5 ressources, toutes des
nœuds de parcours ; il n'y a **pas de ressource « CM de promo »** distincte (les
parcours sont disjoints — `Officine` + `Internat` = exactement le total).

### Parcours (filière)
| Ressource | Parcours (picker) | Contenu / remarque |
|---|---|---|
| `4098` | **Officine** (2 sous-groupes) | UE Off 5/6/7/9, LC5/LC6, rencontres pro, formations 5AHU, colles, examens (≈107 évts). Sous-groupes « G 1 » / « G 2 » (31 évts chacun + 45 communs), marqués **uniquement dans la `DESCRIPTION`** — donc **inséparables côté ADE**. Le picker les sépare **via le proxy** (voir ci-dessous). |
| `4099` | **Internat** | Prépa internat, sections I à V, UE Int 3 (≈41 évts) |
| `4097` | **Industrie** | **Aucun cours** — étudiants en stage. Exposé pour mémoire, se remplira quand la fac publiera. |
| `4096` | **Tous les parcours** | Superset = Officine ∪ Internat (≈148 évts = 107 + 41) |
| `32783` | *(non exposé)* | Nœud vide, non identifié (0 évt) |

> 🔧 **Officine G1/G2 = filtrage par le proxy.** La fac ne sépare pas les deux
> groupes en ressources distinctes ; le marqueur « G 1 » / « G 2 » n'est que dans la
> `DESCRIPTION`. Le picker route donc l'officine par le worker avec un paramètre
> `group` (ex. `…/?resources=4098&group=G%201`) : le worker garde les cours **sans
> marqueur** (communs) **+** ceux du groupe demandé (→ 76 évts pour G1). Sans proxy,
> l'item retombe sur `resources=4098` direct = **les deux groupes**. Voir
> `experimental/cloudflare-worker/worker.js` (`filterByGroup`).

> ⚠️ Pas de CM commun en 5e année : chaque parcours porte l'intégralité de son
> emploi du temps. Le picker masque donc, pour cette promo, le rappel « CM de promo
> inclus » et l'option « Ajouter les CM de promo seuls » (`cm: ""` dans `PROMOS["5"]`).
> Le **mode redoublant** est aussi masqué (pas de catalogue de matières fiable : le
> flux étiquette les cours par UE de parcours, `UE Off N` / `Section N`, pas par UE
> transverses).

> **Liste des ressources DFASP2** : voir la constante `RESOURCES_DFASP2` dans
> `scripts/probe_resources.py`.

## Méthode (reproductible)

Script : `scripts/probe_resources.py` (interroge chaque ID isolément, agrège
types/groupes/UE). Relancer si la fac renumérote ses ressources d'une année sur
l'autre. Augmenter `nbWeeks` si une ressource ne renvoie pas assez de cours pour
être identifiée. Les IDs des quatre promos sont dans le script (constantes
`RESOURCES` = DFGSP2, `RESOURCES_DFGSP3` = DFGSP3, `RESOURCES_DFASP1` = DFASP1,
`RESOURCES_DFASP2` = DFASP2), sélectionnables via `--promo 2|3|4|5`.
