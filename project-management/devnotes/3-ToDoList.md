# EXTRA-DRAFT document

### WIP-jferone git branch to-do-list

---

| TO-DO | Authors: jferone, qbourine | Based on: 1-Rules.md + 2-Logic.md (2026-06-17) | Date: 2026-06-17 |
|---|---|---|---|

> Phase 1 = une seule référence à cocher intégralement, bonus compris.
> jferone : interface + wrapping logique (`src/__main__.py`, `src/scenes/*`, `src/ui/*`).
> qbourine : logique de jeu (`entities/*`, `tools/*`). Sections "à deux" pour plus tard.

</details>

---

`team`

<details>
<summary>Décisions verrouillées (O1-O7)</summary>

## Décisions verrouillées (O1-O7)

| ID | Décision |
|---|---|
| O1 | Clés config = clés suggérées (highscore_filename, level[], width/height, lives, pacgum, points_per_*, seed, level_max_time, durées frightened/respawn) |
| O2 | Highscore = fichier JSON sur disque |
| O3 | IA fantômes = comportement authentique des 4 fantômes (Blinky chase direct, Pinky 4 cases devant, Inky vecteur via Blinky, Clyde chase/scatter selon distance ; alternance scatter/chase ; flee en frightened ; retour "yeux" au spawn) |
| O4 | Timeout niveau = perte d'1 vie + reset ; base 3 vies (modifiable par cheat bonus) |
| O5 | Lib graphique = pygame |
| O6 | Cheat = skip de niveau (prio) + invincibilité (secondaire) ; pas de freeze fantômes |
| O7 | Déploiement = Itch.io (gratuit, non-listé) |

</details>

---

`jferone`

<details>
<summary>🟦 UI + wrapping (`__main__.py`, `scenes/*`, `ui/*`)</summary>

## 🟦 jferone - UI + wrapping (`__main__.py`, `scenes/*`, `ui/*`)

| Fait | # | Tâche | Réf |
|---|---|---|---|
| [x] | J1 | Flow de scènes complet : MainMenu -> level -> GameOver/Victory + saisie nom -> MainMenu | M48, M46-M47 |
| [x] | J2 | Compléter MainMenu : ajouter "View Highscores" et "Instructions" | M49 |
| [x] | J3 | `scores_menu.py` : écran Top 10 (nom + score), branché sur le highscore | M14, M17 |
| [x] | J4 | Overlay-stase pause générique dans `ui/pause_hud.py` piloté par `core.py` (PAS une scène du registry). `P`/`ESC` ouvre/ferme ; Resume + Return to main menu ; gèle `update`, garde le rendu dessous, met la musique en pause | M45, M51 |
| [x] | J5 | HUD permanent : score, vies, niveau, temps restant | M50 |
| [x] | J6 | Écrans GameOver (score final + saisie nom) et Victory (score + félicitations + saisie nom) | M52, M53 |
| [x] | J7 | `ui/components.py` : widget TextInput (nom <= 10 char, alphanum + espaces) + idéalement nav clavier | M12, M16, M54 |
| [x] | J8 | Sortir les constantes en dur de `playing_level.py` (vies=3, temps=300, scores 10/50/200, frightened) vers la config | M2, M32-M34, M42 |
| [x] | J9 | Cheat : skip de niveau (prio) + invincibilité (secondaire). Ajouter `M40` au `Covers` de `playing_level` à l'implémentation | M40, O6, B3 |
| [⏸] | J10 | `__main__.py` : retour propre (`sys.exit(main())`), ne plus régénérer les niveaux à chaque lancement - **bloqué** : dépend de mazegen (Quentin/Q5) | F18 |
| [x] | J11 | Timeout (O4) : `lives -= 1` + `reset_positions()` + reset `remaining_time` (remplacer le retour menu actuel `playing_level.py:137`) | M42, O4 |
| [⏸] | J12 | `playing_level` possède l'horloge scatter/chase et la passe aux fantômes - **Quentin** | O3 |
| [ ] | J13 | README complet : 1re ligne en italique + toutes les sections imposées | M59, M60, F21 |

</details>

---

`qbourine`

<details>
<summary>🟥 Logique de jeu (`entities/*`, `tools/*`)</summary>

## 🟥 qbourine - logique de jeu (`entities/*`, `tools/*`)

| Fait | # | Tâche | Réf |
|---|---|---|---|
| [ ] | Q1 | IA fantômes authentique : ciblage par personnalité (Blinky/Pinky/Inky/Clyde) + scatter/chase + flee edible | M36, M37, O3 |
| [ ] | Q2 | Délai de respawn 5-10s du fantôme mangé (état "yeux" -> retour spawn -> normal) | M38, A4 |
| [ ] | Q3 | Placement : Pac-Man au centre (pas `[9,9]` en dur), exclure spawns/centre/coins du remplissage pacgum | M23, A6 |
| [ ] | Q4 | Résoudre conflit coins = super-pacgums ET spawns fantômes | M21, M22 |
| [ ] | Q5 | Wrapper `mazegen` : génération paresseuse, seed niveau 1 = 42, suivants random ; gérer échec générateur ; décider régénération par partie vs install (cf. point ouvert #3) | M9, M10, M19, M41 |
| [ ] | Q6 | (cosmétique) Homogénéiser les états FR (`mort/appeure`) si voulu | F2 |

</details>

---

`team`

<details>
<summary>🟪 Plus tard</summary>


| Fait | # | Tâche | Réf |
|---|---|---|---|
| [x] | S1 | Parser config JSON-avec-commentaires `#` : defaults robustes, clamp, ignore clés inconnues, jamais de traceback | M2-M5, F19, A5 |
| [x] | S2 | CLI `pac-man.py config.json` : 1 arg, `.json`, messages d'erreur clairs | F16-F18 |
| [x] | S3 | Highscore persistant (JSON disque) : robuste fichier manquant/corrompu, load au start / save à la fin | M11-M15, O2 |
| [ ] | S4 | Loader A-Maze-ing officiel quand assigné (s'adapter au package, `PERFECT=False`) | M6-M10, A2 |
| [ ] | S5 | Makefile : `install`, corriger `lint`/`lint-strict` (cible `src/`, pas `main.py`), `debug`, `clean` | F9-F14 |
| [ ] | S6 | Déploiement Itch.io + instructions in-package (contrôles, options, config) | M55, M56, O7 |
| [ ] | S7 | Dossier project-management (timeline, risques, test plan) | M58, F22 |
| [ ] | S8 | Docstrings PEP257 partout + passer `mypy`/`flake8` | F5, F6 |
| [x] | S9 | `pyproject.toml` : déclarer `pygame` et `mazegen` en dépendances | F9 |

</details>

---

`team`

<details>
<summary>Points non bloquants à trancher</summary>

- [x] **Cheat M40** : code dans `playing_level` (F1 invincibilité, F2 skip niveau).
- [x] **`settings_menu.py` orphelin** : recyclé en `instructions_menu.py`.
- [ ] **Régénération maze** : à chaque partie (rejouabilité) vs une fois à l'install ? -> tracer en A10 dans `1-Rules.md` si verrouillé. (⏸ Quentin/Q5)
- [ ] **Pas de "ghost house"** : simplification assumée (spawns directs dans les coins) -> à mentionner dans le debrief doc.
- [x] **Durée frightened** : 6.0s via `config.json` (clé `frightened_duration`).

</details>

---
