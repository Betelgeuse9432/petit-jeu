import os
import random
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")

SPRITES = {
    "icon_rocket": os.path.join(SPRITES_DIR, "icon_rocket.png"),
    "rocket":      os.path.join(SPRITES_DIR, "roquette.png"),
    "panda":       os.path.join(SPRITES_DIR, "panda_assis.png"),
}
