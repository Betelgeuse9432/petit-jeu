import random
import time
import pygame
import math


from configuration import BLOCK_SIZE, HEIGHT




class Building:

    def __init__(self, x, w, h, color):
        self.x = x
        self.w = w
        self.h = h
        self.color = color

        # Crée la grille de blocs (gx, gy) : gx de 0..grid_w-1, gy de 0..grid_h-1 (0 = au bas)
        self.grid_w = (w + BLOCK_SIZE - 1) // BLOCK_SIZE
        self.grid_h = (h + BLOCK_SIZE - 1) // BLOCK_SIZE
        # True = intact, False = détruit
        self.blocks = [[True for _ in range(self.grid_h)] for _ in range(self.grid_w)]

        # hauteur actuelle recalculée en blocs
        self._recalc_height()

        self.cols = max(2, w // 20)
        self.rows = max(3, h // 24)
        self.window_states = [[random.choice([True, False]) for _ in range(self.cols)] for _ in range(self.rows)]
        self.last_window_update = time.time()

    def _recalc_height(self):
        max_blocks = 0
        for gx in range(self.grid_w):
            # compte combien de blocs intacts dans la colonne gx (bas -> haut)
            col_blocks = 0
            for gy in range(self.grid_h):
                if self.blocks[gx][gy]:
                    col_blocks = gy + 1  # gy index +1
            if col_blocks > max_blocks:
                max_blocks = col_blocks
        # hauteur en pixels
        self.h = max_blocks * BLOCK_SIZE

    def rect(self):
        #Hitbox basée exactement sur les blocs intacts.
        # colonnes contenant au moins un bloc intact
        intact_cols = [gx for gx in range(self.grid_w) if any(self.blocks[gx])]
        if not intact_cols:
            return pygame.Rect(self.x, HEIGHT, 0, 0)  # plus de blocs intacts

        left_gx = min(intact_cols)
        right_gx = max(intact_cols)

        # hauteur max parmi ces colonnes
        max_gy = 0
        for gx in intact_cols:
            col_height = max([gy+1 for gy, alive in enumerate(self.blocks[gx]) if alive], default=0)
            if col_height > max_gy:
                max_gy = col_height

        x = self.x + left_gx * BLOCK_SIZE
        w = (right_gx - left_gx + 1) * BLOCK_SIZE
        y = HEIGHT - max_gy * BLOCK_SIZE
        h = max_gy * BLOCK_SIZE
        return pygame.Rect(x, y, w, h)

    def check_collision(self, px, py, radius):
        #Retourne True si le projectile touche un bloc intact.
        for gx in range(self.grid_w):
            for gy in range(self.grid_h):
                if not self.blocks[gx][gy]:
                    continue
                bx = self.x + gx * BLOCK_SIZE + BLOCK_SIZE/2
                by = HEIGHT - (gy * BLOCK_SIZE) - BLOCK_SIZE/2
                if math.hypot(px - bx, py - by) <= radius + BLOCK_SIZE/2:
                    return True
        return False

    def draw(self, surface):
        for gx in range(self.grid_w):
            for gy in range(self.grid_h):
                if not self.blocks[gx][gy]:
                    continue
                px = self.x + gx * BLOCK_SIZE
                py = HEIGHT - (gy + 1) * BLOCK_SIZE

                # ombre décalée
                shadow_rect = pygame.Rect(
                    px + 6,        # décalage horizontal
                    py + 10,       # décalage vertical
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                pygame.draw.rect(surface, (10, 10, 10), shadow_rect)

        # Batiments
        for gx in range(self.grid_w):
            for gy in range(self.grid_h):
                if not self.blocks[gx][gy]:
                    continue

                px = self.x + gx * BLOCK_SIZE
                py = HEIGHT - (gy + 1) * BLOCK_SIZE

                pygame.draw.rect(surface, self.color,
                                pygame.Rect(px, py, BLOCK_SIZE, BLOCK_SIZE))

        # --- Fenêtres ---
        for cy in range(self.rows):
            for cx in range(self.cols):
                # calcule bloc correspondant
                gx = int(cx * self.grid_w / self.cols)
                gy = int(cy * self.grid_h / self.rows)
                if gx >= self.grid_w or gy >= self.grid_h:
                    continue
                if not self.blocks[gx][gy]:
                    continue  # on saute si bloc détruit

                # position exacte de la fenêtre
                wx = self.x + 6 + cx * (self.w / self.cols)
                wy = HEIGHT - (gy + 1) * BLOCK_SIZE + 2  # +2 pour un léger décalage
                ww, wh = 10, 6
                win_col = (255, 246, 170) if self.window_states[cy][cx] else (20, 20, 20)
                pygame.draw.rect(surface, win_col, pygame.Rect(wx, wy, ww, wh))

    def damage_at(self, ex, ey, radius):
        # Détruit uniquement les blocs dans le rayon de l’explosion et retourne le nombre de blocs détruits.
        damage_count = 0
        for gx in range(self.grid_w):
            for gy in range(self.grid_h):
                if not self.blocks[gx][gy]:
                    continue
                # centre du bloc
                px = self.x + gx * BLOCK_SIZE + BLOCK_SIZE / 2
                py = HEIGHT - (gy * BLOCK_SIZE) - BLOCK_SIZE / 2
                dist = math.hypot(px - ex, py - ey)
                if dist <= radius:
                    self.blocks[gx][gy] = False
                    damage_count += 1

        if damage_count > 0:
            # recalculer la hauteur visible après destruction
            self._recalc_height()
        return damage_count

    def update_windows(self):
        now = time.time()
        if now - self.last_window_update >= 2.0:  # 2 sec écoulées
            for r in range(self.rows):
                for c in range(self.cols):
                    self.window_states[r][c] = random.random() < 0.5  # 50% chance on/off
            self.last_window_update = now
