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
- une interface avec sliders pour régler l'angle et la vitesse.

## Structure actuelle

```text
petit-jeu/
├── main.py
├── configuration.py
├── classes_helpers.py
├── requirements.txt
├── .gitignore
└── README.md
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

## Attention importante

Le projet utilise actuellement des chemins absolus Windows pour charger certaines images, par exemple des fichiers situés dans `C:\Users\...`.

Cela signifie que le jeu peut fonctionner sur la machine d'origine, mais casser sur un autre ordinateur.

Amélioration recommandée : créer un dossier `assets/` dans le dépôt et y placer les images nécessaires :

```text
assets/
├── icon_rocket.png
├── roquette.png
└── panda_assis.png
```

Puis charger les fichiers avec des chemins relatifs en Python.

## Fichiers principaux

- `main.py` : boucle principale du jeu et logique globale ;
- `configuration.py` : constantes du jeu ;
- `classes_helpers.py` : classes utiles comme bâtiments, nuages, gorilles, vent et gestion des scores.

## Statut

Projet personnel d'apprentissage avec Pygame. Le jeu contient déjà une vraie base jouable, mais il reste à nettoyer l'organisation, les chemins d'images et certains bugs de logique.