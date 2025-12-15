import pygame
import pygame_gui
import random
import math
import time
import json
import os
# from noise import pnoise2
from collections import deque
from datetime import datetime
from configuration import *



# ---------- Classes & helpers -------------



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
        """Hitbox basée exactement sur les blocs intacts."""
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



class Cloud:

    def __init__(self, x, y, min_blocks=CLOUD_MIN_BLOCKS, max_blocks=CLOUD_MAX_BLOCKS):
        self.x = x
        self.y = y
        self.min_blocks = min_blocks
        self.max_blocks = max_blocks
        self._generate_blob()
        self._make_surfaces()

    def _generate_blob(self):
        # Génération d’un set de blocs
        target_blocks = random.randint(self.min_blocks, self.max_blocks)
        blocks_set = {(0, 0)}
        frontier = deque([(0, 0)])
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]

        while len(blocks_set) < target_blocks:
            bx, by = frontier[0]
            dx, dy = random.choice(dirs)
            nx, ny = bx + dx, by + dy
            if random.random() < 0.65:
                blocks_set.add((nx, ny))
                frontier.append((nx, ny))
            else:
                frontier.rotate(1)

        # Normalisation en grille 2D
        xs = [x for x, y in blocks_set]
        ys = [y for x, y in blocks_set]
        min_x, min_y = min(xs), min(ys)
        shifted = [(x - min_x, y - min_y) for x, y in blocks_set]

        self.grid_w = max(sx for sx, sy in shifted) + 1
        self.grid_h = max(sy for sx, sy in shifted) + 1
        self.blocks = [[False]*self.grid_h for _ in range(self.grid_w)]
        for sx, sy in shifted:
            self.blocks[sx][sy] = True

        self.w = self.grid_w * BLOCK_SIZE
        self.h = self.grid_h * BLOCK_SIZE

    def _make_surfaces(self):
        alpha = random.randint(CLOUD_MIN_ALPHA, CLOUD_MAX_ALPHA)
        self.block_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        self.block_surf.fill((255, 255, 255, alpha))
        self.shadow_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        self.shadow_surf.fill((0, 0, 0, alpha // 4))

    def update(self, dt, wind):
        self.x += wind * dt
        if self.x > WIDTH:
            self.x -= WIDTH
        elif self.x + self.w < 0:
            self.x += WIDTH

    def draw(self, surface):
        sox, soy = SHADOW_OFFSET
        for gx in range(self.grid_w):
            for gy in range(self.grid_h):
                if not self.blocks[gx][gy]:
                    continue
                px = self.x + gx * BLOCK_SIZE
                py = self.y + gy * BLOCK_SIZE
                # Ombre
                surface.blit(self.shadow_surf, (px + sox, py + soy))
                # Bloc visible
                surface.blit(self.block_surf, (px, py))

    def damage_at(self, ex, ey, radius):
        destroyed = 0
        for gx in range(self.grid_w):
            for gy in range(self.grid_h):
                if not self.blocks[gx][gy]:
                    continue
                bx = self.x + gx*BLOCK_SIZE + BLOCK_SIZE/2
                by = self.y + gy*BLOCK_SIZE + BLOCK_SIZE/2
                if (bx - ex)**2 + (by - ey)**2 <= radius**2:
                    self.blocks[gx][gy] = False
                    destroyed += 1
        return destroyed

    def check_collision(self, px, py, radius):
        for gx in range(self.grid_w):
            for gy in range(self.grid_h):
                if not self.blocks[gx][gy]:
                    continue
                bx = self.x + gx*BLOCK_SIZE + BLOCK_SIZE/2
                by = self.y + gy*BLOCK_SIZE + BLOCK_SIZE/2
                if (bx - px)**2 + (by - py)**2 <= (BLOCK_SIZE/2 + radius)**2:
                    return True
        return False



class CloudManager:

    def __init__(self, count=NUAGE_COUNT, y_base=50, screen_width=WIDTH, wind=None):
        self.screen_width = screen_width
        self.clouds = []

        # Vent
        self.wind = wind

        min_dist = 120
        attempts = 20

        for _ in range(count):
            for _attempt in range(attempts):
                w = random.randint(4*BLOCK_SIZE, 12*BLOCK_SIZE)
                h = random.randint(2*BLOCK_SIZE, 6*BLOCK_SIZE)
                x = random.uniform(0, screen_width - w)
                y = y_base + random.randint(-20, 20)

                ok = True
                for c in self.clouds:
                    dx = (x + w/2) - (c.x + c.w/2)
                    dy = (y + h/2) - (c.y + c.h/2)
                    if dx*dx + dy*dy < min_dist*min_dist:
                        ok = False
                        break
                if ok:
                    break

            self.clouds.append(Cloud(x, y))

    def update(self, dt):
        if self.wind is not None:
            wind_force = self.wind.update()  # <-- valeur interpolée ou en pause
        else:
            wind_force = 0  # fallback

        for c in self.clouds:
            c.update(dt, wind_force)

    def draw(self, surface):
        for c in self.clouds:
            c.draw(surface)

    def explode(self, ex, ey, radius):
        return sum(c.damage_at(ex, ey, radius) for c in self.clouds)

    def check_collision(self, px, py, radius):
        return any(c.check_collision(px, py, radius) for c in self.clouds)

    def reset(self, reposition=True):
        min_dist = 120
        attempts = 20
        for c in self.clouds:
            c._generate_blob()
            if not reposition:
                continue
            w, h = c.w, c.h
            for _attempt in range(attempts):
                x = random.uniform(0, self.screen_width - w)
                y = c.y + random.randint(-10, 10)
                ok = True
                for other in self.clouds:
                    if other is c:
                        continue
                    dx = (x + w/2) - (other.x + other.w/2)
                    dy = (y + h/2) - (other.y + other.h/2)
                    if dx*dx + dy*dy < min_dist*min_dist:
                        ok = False
                        break
                if ok:
                    break
            c.x, c.y = x, y



class Gorilla:

    def __init__(self, x, y, side, sprite_path=None, scale_factor=0.05):
        
        self.x = x
        self.y = y
        self.side = side
        self.alive = True
        self.max_health = 100  # santé max
        self.health = self.max_health

        # chemin par défaut si non fourni
        if sprite_path is None:
            sprite_path = r"C:\Users\Betel\OneDrive\Documents\ecam\2BA\info\programme\png\panda_assis.png"

        # Chargement du sprite
        self.sprite = pygame.image.load(sprite_path).convert_alpha()

        # Redimensionnement
        self.sprite = pygame.transform.smoothscale(
            self.sprite,
            (int(self.sprite.get_width() * scale_factor),
             int(self.sprite.get_height() * scale_factor))
        )

        # flip horizontal si gorille du côté gauche
        if side == 'left':
            self.sprite = pygame.transform.flip(self.sprite, True, False)

        # dimensions finales
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()

    def rect(self):
        #hitbox autour du gorille
        return pygame.Rect(self.x - self.width//2, self.y - self.height, self.width, self.height)

    def draw(self, surface):
        #affiche la sprite sur la hitbox
        surface.blit(self.sprite, (self.x - self.width//2, self.y - self.height))



class Wind:

    def __init__(self, values, steps_per_transition=STEPS_PER_TRANSISION, delay_update_wind=DELAY_UPDATE_WIND):
        self.values = values
        self.steps_per_transition = steps_per_transition
        self.delay_update_wind = delay_update_wind

        self.start_value = random.choice(values)
        self.end_value = random.choice(values)
        self.current_force = self.start_value

        self.current_step = 0
        self.pause_timer = 0
        self.in_pause = False

    def update(self):
        if self.in_pause:
            # on reste sur la valeur finale
            self.pause_timer += 1
            if self.pause_timer >= self.delay_update_wind:
                # on choisit une nouvelle cible
                self.start_value = self.end_value
                self.end_value = random.choice(self.values)
                self.current_step = 0
                self.pause_timer = 0
                self.in_pause = False
        else:
            # interpolation vers end_value
            t = self.current_step / self.steps_per_transition
            self.current_force = self.start_value + (self.end_value - self.start_value) * t
            self.current_step += 1
            if self.current_step >= self.steps_per_transition:
                # on atteint la valeur cible, on lance le pause
                self.current_force = self.end_value
                self.in_pause = True
                self.pause_timer = 0

        return self.current_force



class ScoreManager:
    def __init__(self, scores_file):
        self.scores_file = scores_file

    def save_match(self, p1, p2, scores, winner_index):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "player1": p1,
            "player2": p2,
            "score": scores,
            "winner": f"Joueur {winner_index + 1}"
        }

        data = []
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []

        data.append(entry)

        with open(self.scores_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)



class Sun:

    def __init__(self, x, y, radius, block_size=BLOCK_SIZE, update_speed=0.05):
        self.x = x
        self.y = y
        self.radius = radius
        self.block_size = int(block_size)
        self.update_speed = update_speed  # vitesse de mise à jour des couleurs
        self.grid = []
        self.time_accumulator = 0.0

        # Initialisation de la grille de couleur
        for bx in range(-radius, radius, self.block_size):
            row = []
            for by in range(-radius, radius, self.block_size):
                if bx**2 + by**2 <= radius**2:
                    # couleur initiale aléatoire entre orange foncé et jaune clair
                    r = random.randint(200, 255)
                    g = random.randint(100, 200)
                    b = 0
                    row.append([r, g, b])
                else:
                    row.append(None)
            self.grid.append(row)

    def update(self, dt):
        self.time_accumulator += dt
        if self.time_accumulator < self.update_speed:
            return
        self.time_accumulator = 0.0

        # Mise à jour des couleurs avec influence des voisins
        new_grid = []
        for i, row in enumerate(self.grid):
            new_row = []
            for j, cell in enumerate(row):
                if cell is None:
                    new_row.append(None)
                    continue
                # moyenne avec les voisins (pour un effet plus doux)
                neighbors = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < len(self.grid) and 0 <= nj < len(row):
                            neighbor_cell = self.grid[ni][nj]
                            if neighbor_cell:
                                neighbors.append(neighbor_cell)
                # moyenne des valeurs R,G,B
                avg_r = sum([c[0] for c in neighbors]) / len(neighbors)
                avg_g = sum([c[1] for c in neighbors]) / len(neighbors)
                avg_b = sum([c[2] for c in neighbors]) / len(neighbors)
                # petite variation aléatoire
                new_r = max(0, min(255, int(avg_r + random.randint(-5, 5))))
                new_g = max(0, min(255, int(avg_g + random.randint(-5, 5))))
                new_b = max(0, min(255, int(avg_b + random.randint(-2, 2))))
                new_row.append([new_r, new_g, new_b])
            new_grid.append(new_row)
        self.grid = new_grid

    def draw(self, screen):
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell is None:
                    continue
                bx = self.x + (i * self.block_size - self.radius)
                by = self.y + (j * self.block_size - self.radius)
                pygame.draw.rect(screen, cell, (bx, by, self.block_size, self.block_size))









