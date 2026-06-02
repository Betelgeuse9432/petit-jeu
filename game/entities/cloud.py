import random
import pygame


from collections import deque
from configuration import *








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
