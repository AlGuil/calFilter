# Localisation des salles (référence)

Le calendrier ADE n'exporte que le **nom court** de la salle (`Amphi 2B`),
jamais l'aile (`R1`) ni l'étage — cette info n'existe que dans l'appli web de la
fac. Comme chaque salle est **unique**, son emplacement est une propriété fixe :
on peut donc la donner via une table statique. Elle est embarquée dans
`index.html` (constante `ROOMS`) et affichée par le répertoire cherchable.

## Structure du bâtiment

- **R1 / R2 / R3** = les trois **ailes** (chacune avec escaliers + ascenseurs).
- **Étages** : RDC, 1er, 2e, 3e, 4e, 5e, 6e.
- L'étage d'une salle se déduit de son numéro : `0xx`=RDC, `1xx`=1er, `2xx`=2e,
  `3xx`=3e, `4xx`=4e, `5xx`=5e, `6xx`=6e (confirmé par le plan).

## Amphithéâtres (emplacement complet)

| Amphi | Étage | Aile | Surnom |
|---|---|---|---|
| Amphi 1 | 1er | R1 | Puy de la Nugère |
| Amphi 4 | 1er | R2 | Puy de Pariou |
| Amphi 5 | 1er | R3 | Puy Mary |
| Amphi 2A | 3e | R1 | Puy de Jume |
| Amphi 6A | 3e | R3 | Puy Petit Sarcouy |
| Amphi 2B | 4e | R1 | Puy de coquille |
| Amphi 6B | 4e | R3 | Puy grand Sarcouy |
| Amphi 3 | 5e | R1 | Puy de Côme |
| Amphi Volcans (B) | RDC | — | Accès CRBC (côté R3) |
| Auditorium | RDC | — | Aile ouest, près du CROUS |

## Source & maintenance

Données relevées sur le **plan officiel UCA « Localisation amphithéâtres et
salles de cours » (2021)**. L'aile n'est renseignée que pour les salles figurant
explicitement au plan ; pour les autres, seul l'étage (déduit du numéro) est
donné. Si un amphi/une salle déménage, mettre à jour la constante `ROOMS` dans
[`../index.html`](../index.html).
