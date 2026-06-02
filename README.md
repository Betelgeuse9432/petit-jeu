# Petit-jeu

Jeu Python/Pygame inspiré du principe de *Gorillas* : deux joueurs se tirent dessus avec un projectile en tenant compte de l'angle, de la vitesse, de la gravité et du vent.

## Description

Le projet contient un petit jeu en 2D avec :

- deux personnages placés sur des bâtiments ;
- des bâtiments destructibles par explosions ;
- un projectile soumis à la gravité ;
- un vent variable ;
- des nuages destructibles ;
- des barres de vie ;
- des scores ;
- un menu de saisie des pseudos ;
- une interface de fin avec bouton rejouer/quitter ;
- une interface avec sliders pour régler l'angle et la vitesse.

## Structure actuelle

```text
petit-jeu/
├── main.py
├── configuration.py
├── do_not_ask.py
├── requirements.txt
├── .gitignore
├── README.md
├── assets/
│   └── sprites/
│       ├── icon_rocket.png
│       ├── roquette.png
│       └── panda_assis.png
└── game/
    ├── gorillagame.py
    ├── entities/
    │   ├── buildings.py
    │   ├── cloud.py
    │   └── gorilla.py
    └── systems/
        ├── interface.py
        ├── interface_fin.py
        ├── scoremanager.py
        └── wind.py
```

## Installation

Créer un environnement virtuel, puis installer les dépendances :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Sous Linux/macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

## Assets nécessaires

Les images sont chargées depuis `assets/sprites/` via `do_not_ask.py`.

Le jeu attend actuellement :

```text
assets/sprites/icon_rocket.png
assets/sprites/roquette.png
assets/sprites/panda_assis.png
```

Si ces fichiers ne sont pas présents dans le dépôt ou sur ta machine locale, Pygame plantera au chargement. Oui, un jeu sans images qui exige des images, c'est apparemment une tension dramatique.

## Fichiers principaux

- `main.py` : point d'entrée du programme ;
- `configuration.py` : constantes du jeu ;
- `do_not_ask.py` : chemins vers les assets ;
- `game/gorillagame.py` : logique principale du jeu ;
- `game/entities/` : bâtiments, nuages, gorilles ;
- `game/systems/` : menu, écran de fin, score manager et vent.

## Statut

Projet personnel d'apprentissage avec Pygame. Le code est maintenant séparé en modules plus propres qu'une version monolithique, mais il reste à vérifier les assets et à tester le lancement depuis un clone propre du dépôt.