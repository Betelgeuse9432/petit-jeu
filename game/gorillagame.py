import pygame
import pygame_gui
import random
import math
from configuration import *
from game.entities.buildings import Building
from game.entities.cloud import CloudManager
from game.entities.gorilla import Gorilla
from game.systems.wind import Wind
from game.systems.scoremanager import ScoreManager
from game.systems.interface_fin import InterfaceFin


class GorillaGame:

    def __init__(self, scale_factor=0.05, pseudo1="Joueur1", pseudo2="Joueur2"):
        pygame.init()
        pygame.display.set_caption("Gorilla - Pygame Edition")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.font = pygame.font.SysFont(FONT_NAME, 18)

        self.wind = Wind(values=WIND_VALUES, steps_per_transition=STEPS_PER_TRANSISION, delay_update_wind=DELAY_UPDATE_WIND)
        self.cloud_manager = CloudManager(count=NUAGE_COUNT, y_base=60, screen_width=WIDTH, wind=self.wind)

        self.pseudo1 = pseudo1
        self.pseudo2 = pseudo2

        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(((WIDTH // 2) - 275, HEIGHT - 50), (200, 30)),
            start_value=200,
            value_range=(20, 1000),
            manager=self.manager
        )
        self.speed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(((WIDTH // 2) - 275, HEIGHT - 70), (150, 20)),
            text="Vitesse = " + str(self.speed_slider.get_current_value()),
            manager=self.manager
        )

        self.angle_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(((WIDTH // 2) + 75, HEIGHT - 50), (200, 30)),
            start_value=45,
            value_range=(1, 179),
            manager=self.manager
        )
        self.angle_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(((WIDTH // 2) + 75, HEIGHT - 70), (150, 20)),
            text="Angle = " + str(self.angle_slider.get_current_value()),
            manager=self.manager
        )

        self.fire_button = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(WIDTH // 2 - 25, HEIGHT - 80, 50, 50),
            image_surface=pygame.image.load(SPRITES["icon_rocket"]).convert_alpha(),
            manager=self.manager
        )

        self.reset_match()

        self.rocket_img = pygame.image.load(SPRITES["rocket"]).convert_alpha()
        w = int(self.rocket_img.get_width() * scale_factor)
        h = int(self.rocket_img.get_height() * scale_factor)
        self.rocket_img = pygame.transform.smoothscale(self.rocket_img, (w, h))

        self.score_manager = ScoreManager(SCORES_FILE)
        self.pending_action = None

    def reset_match(self):
        self.buildings = []
        self.gorillas = []
        self.generate_buildings()
        self.place_gorillas()
        self.cloud_manager.reset(reposition=True)
        self.projectile = None
        self.explosions = []

        self.wind.start_value = random.choice(WIND_VALUES)
        self.wind.end_value = random.choice(WIND_VALUES)
        self.wind.current_force = self.wind.start_value
        self.wind.current_step = 0
        self.wind.in_pause = False
        self.wind.pause_timer = 0

        self.current_player = random.choice([0, 1])
        self.scores = [0, 0]
        self.round_active = True
        self.round_winner = None
        self.angle = 45.0
        self.speed = 200.0
        self.pending_action = None

    def new_round(self):
        self.buildings = []
        self.gorillas = []
        self.generate_buildings()
        self.place_gorillas()
        self.projectile = None
        self.explosions = []

        self.wind.start_value = random.choice(WIND_VALUES)
        self.wind.end_value = random.choice(WIND_VALUES)
        self.wind.current_force = self.wind.start_value
        self.wind.current_step = 0
        self.wind.in_pause = False
        self.wind.pause_timer = 0

        self.round_active = True
        self.round_winner = None
        self.pending_action = None
        self.cloud_manager.reset(reposition=True)

    def end_round(self):
        if self.round_winner is not None:
            self.scores[self.round_winner] += 1
            self.round_active = False

        match_winner = None
        if self.scores[0] >= ROUNDS_TO_WIN:
            match_winner = 0
        elif self.scores[1] >= ROUNDS_TO_WIN:
            match_winner = 1

        if match_winner is not None:
            return self.show_match_end(match_winner)

        self.current_player = 1 - self.round_winner
        pygame.time.set_timer(pygame.USEREVENT + 3, 1500)
        return None

    def show_match_end(self, winner_index):
        winner_text = f"{self.pseudo1 if winner_index == 0 else self.pseudo2} remporte la partie!"

        dlg = pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect((WIDTH // 2 - 220, HEIGHT // 2 - 140), (440, 160)),
            manager=self.manager,
            window_title="Fin de la partie",
            html_message=f"{winner_text}"
        )

        pygame.display.update()
        pygame.time.delay(1000)
        self.score_manager.save_match(self.pseudo1, self.pseudo2, self.scores, winner_index)
        dlg.kill()

        winner_name = self.pseudo1 if winner_index == 0 else self.pseudo2
        fin_ui = InterfaceFin(self.screen, WIDTH, HEIGHT)
        return fin_ui.afficher(winner_name)

    def generate_buildings(self):
        x = 0
        for _ in range(NUM_BUILDINGS):
            w = random.randint(BUILDING_MIN_W, BUILDING_MAX_W)
            gap = random.randint(2, 8)
            if x + w > WIDTH:
                w = WIDTH - x - 1
            h = random.randint(BUILDING_MIN_H, BUILDING_MAX_H)
            color = (random.randint(30, 90), random.randint(30, 70), random.randint(30, 70))
            self.buildings.append(Building(x, w, h, color))
            x += w + gap
            if x >= WIDTH - 10:
                break

        while x < WIDTH - 20:
            w = random.randint(50, 80)
            h = random.randint(BUILDING_MIN_H, BUILDING_MAX_H)
            color = (random.randint(30, 90), random.randint(30, 70), random.randint(30, 70))
            self.buildings.append(Building(x, w, h, color))
            x += w + 5

    def place_gorillas(self):
        left_b = self.buildings[max(0, len(self.buildings) // 4)]
        right_b = self.buildings[min(len(self.buildings) - 1, 3 * len(self.buildings) // 4)]
        lx = left_b.x + left_b.w // 2
        ly = HEIGHT - left_b.h - 1
        rx = right_b.x + right_b.w // 2
        ry = HEIGHT - right_b.h - 1
        self.gorillas = [Gorilla(lx, ly, 'left'), Gorilla(rx, ry, 'right')]

    def fire_projectile(self, angle_deg, speed):
        g = self.gorillas[self.current_player]
        sign = 1 if g.side == 'left' else -1
        hand_offset_x = g.width // 2 - 5
        start_x = g.x + sign * hand_offset_x
        start_y = g.y - g.height - PROJECTILE_RADIUS
        angle_rad = math.radians(angle_deg)
        vx = speed * math.cos(angle_rad) * sign
        vy = -speed * math.sin(angle_rad)
        self.projectile = {'x': start_x, 'y': start_y, 'vx': vx, 'vy': vy, 'radius': PROJECTILE_RADIUS, 'alive': True}

    def apply_explosion(self, x, y, radius):
        self.explosions.append({'x': x, 'y': y, 'r': radius, 't': 0})
        for b in self.buildings:
            b.damage_at(x, y, radius)
        for g in self.gorillas:
            if not g.alive:
                continue
            dx = g.x - x
            dy = g.y - y
            dist = math.hypot(dx, dy)
            gorilla_radius = max(g.width, g.height) / 2
            if dist <= radius + gorilla_radius:
                damage_factor = max(0, 1 - dist / (radius + gorilla_radius))
                damage_amount = int(damage_factor * EXPLOSION_MAX_DAMAGE)
                g.health -= damage_amount
                if g.health <= 0:
                    g.health = 0
                    g.alive = False
        self.cloud_manager.explode(x, y, radius)

    def handle_projectile_physics(self, dt):
        if not self.projectile or not self.projectile['alive']:
            return

        current_wind = self.wind.update()
        p = self.projectile
        p['vx'] += current_wind * dt
        p['vy'] += GRAVITY * dt
        p['x'] += p['vx'] * dt
        p['y'] += p['vy'] * dt
        p['angle'] = math.degrees(math.atan2(-p['vy'], p['vx']))

        if p['x'] < -50 or p['x'] > WIDTH + 50 or p['y'] > HEIGHT + 200 or p['y'] < -200:
            p['alive'] = False
            if p['y'] >= HEIGHT - 5:
                self.apply_explosion(p['x'], HEIGHT - 2, EXPLOSION_RADIUS)
            self.projectile = None
            self.current_player = 1 - self.current_player
            return

        if self.cloud_manager.check_collision(p['x'], p['y'], p['radius']):
            self.apply_explosion(p['x'], p['y'], EXPLOSION_RADIUS)
            p['alive'] = False
            self.projectile = None
            self.current_player = 1 - self.current_player
            return

        for b in self.buildings:
            if b.check_collision(p['x'], p['y'], p['radius']):
                self.apply_explosion(p['x'], p['y'], EXPLOSION_RADIUS)
                p['alive'] = False
                self.projectile = None
                self.current_player = 1 - self.current_player
                return

        for i, g in enumerate(self.gorillas):
            if not g.alive:
                continue
            if i == self.current_player and math.hypot(g.x - p['x'], g.y - p['y']) < g.width:
                continue
            if pygame.Rect(g.x - g.width // 2, g.y - g.height, g.width, g.height).collidepoint(p['x'], p['y']):
                self.apply_explosion(p['x'], p['y'], EXPLOSION_RADIUS)
                p['alive'] = False
                self.projectile = None
                self.current_player = 1 - self.current_player
                return

    def draw_scene(self):
        s = self.screen
        s.fill(SKY_COLOR)

        sun_pos = (WIDTH - 90, 80)
        sun_radius = 40
        pygame.draw.circle(s, SUN_COLOR, sun_pos, sun_radius)

        eye_offset_x = 15
        eye_offset_y = 10
        eye_radius = 5
        left_eye = [sun_pos[0] - eye_offset_x, sun_pos[1] - eye_offset_y]
        right_eye = [sun_pos[0] + eye_offset_x, sun_pos[1] - eye_offset_y]

        if self.projectile and self.projectile['alive']:
            px, py = self.projectile['x'], self.projectile['y']
            dx = px - sun_pos[0]
            dy = py - sun_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                max_eye_move = 5
                dx = dx / dist * max_eye_move
                dy = dy / dist * max_eye_move
                left_eye[0] += dx
                left_eye[1] += dy
                right_eye[0] += dx
                right_eye[1] += dy

        pygame.draw.circle(s, (0, 0, 0), left_eye, eye_radius)
        pygame.draw.circle(s, (0, 0, 0), right_eye, eye_radius)

        self.cloud_manager.draw(s)

        for b in self.buildings:
            b.draw(s)

        pygame.draw.rect(s, GROUND_COLOR, pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

        for g in self.gorillas:
            if not g.alive:
                pygame.draw.line(s, (180, 180, 180), (g.x - 10, g.y - 4), (g.x + 10, g.y + 10), 3)
                pygame.draw.line(s, (180, 180, 180), (g.x + 10, g.y - 4), (g.x - 10, g.y + 10), 3)
            else:
                g.draw(s)

        current_name = self.pseudo1 if self.current_player == 0 else self.pseudo2
        hud = self.font.render(
            f"Tour de: {current_name}  |  Scores: {self.pseudo1} {self.scores[0]} - {self.scores[1]} {self.pseudo2}",
            True, (0, 0, 0)
        )
        s.blit(hud, (WIDTH // 2 - hud.get_width() // 2, 10))

        if self.projectile:
            px = int(self.projectile['x'])
            py = int(self.projectile['y'])
            ang = self.projectile.get('angle', 0)
            rocket_rot = pygame.transform.rotate(self.rocket_img, ang)
            rect = rocket_rot.get_rect(center=(px, py))
            s.blit(rocket_rot, rect)

        for e in self.explosions:
            alpha = max(0, 200 - int(e['t'] * 200))
            surf = pygame.Surface((e['r'] * 2, e['r'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*EXPLOSION_COLOR, alpha), (e['r'], e['r']), int(e['r']))
            s.blit(surf, (e['x'] - e['r'], e['y'] - e['r']))

        for i, g in enumerate(self.gorillas):
            bar_width = 200
            bar_height = 15
            bar_x = 50 if i == 0 else WIDTH - 250
            bar_y = HEIGHT - 60
            pygame.draw.rect(s, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            health_ratio = max(0, g.health / 100)
            pygame.draw.rect(s, (0, 200, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
            health_text = self.font.render(f"{g.health} HP", True, (255, 255, 255))
            s.blit(health_text, (bar_x + bar_width // 2 - health_text.get_width() // 2, bar_y - 15))

        if self.round_active:
            for i, g in enumerate(self.gorillas):
                if not g.alive:
                    self.round_winner = 1 - i
                    self.pending_action = self.end_round()
                    break

    def handle_events(self):
        running = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT + 3:
                pygame.time.set_timer(pygame.USEREVENT + 3, 0)
                self.new_round()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.fire_button.rect.collidepoint(event.pos):
                    if self.round_active and not self.projectile:
                        angle = self.angle_slider.get_current_value()
                        speed = self.speed_slider.get_current_value()
                        self.angle = angle
                        self.speed = speed
                        self.fire_projectile(angle, speed)

            self.manager.process_events(event)
        return running

    def update(self, time_delta):
        self.speed_label.set_text("Vitesse = " + str(self.speed_slider.get_current_value()))
        self.angle_label.set_text("Angle = " + str(self.angle_slider.get_current_value()))
        self.cloud_manager.update(time_delta)
        self.manager.update(time_delta)
        self.handle_projectile_physics(time_delta)

        for e in list(self.explosions):
            e['t'] += time_delta
            if e['t'] > 0.6:
                self.explosions.remove(e)

        for b in self.buildings:
            b.update_windows()

        return self.pending_action

    def draw(self):
        self.draw_scene()
        self.manager.draw_ui(self.screen)
        pygame.display.update()
