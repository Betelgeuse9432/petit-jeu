import pygame
import random

from configuration import WIDTH, HEIGHT, FPS
from game.gorillagame import GorillaGame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)

pygame.init()
font = pygame.font.Font(None, 40)

def show_menu():
    # Fenêtre du menu
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Menu GorillaGame")

    # Jeu démo en fond
    demo_game = GorillaGame(pseudo1="Demo1", pseudo2="Demo2")
    demo_game.round_active = True

    pseudo1 = ""
    pseudo2 = ""
    active_input = None

    clock = pygame.time.Clock()
    running = True

    input1_rect = pygame.Rect((WIDTH // 2) - 200, 150, 400, 40)
    input2_rect = pygame.Rect((WIDTH // 2) - 200, 250, 400, 40)
    button_rect = pygame.Rect((WIDTH // 2) - 50, 400, 100, 40)
    quit_rect = pygame.Rect((WIDTH // 2) - 50, 460, 100, 40)

    last_shot_time = 0.0
    SHOT_DELAY = 3.0

    while running:
        dt = clock.tick(FPS) / 1000.0

        last_shot_time += dt
        if last_shot_time >= SHOT_DELAY and not demo_game.projectile:
            angle = random.randint(30, 85)
            speed = random.randint(150, 500)
            demo_game.fire_projectile(angle, speed)
            last_shot_time = 0.0

        for g in demo_game.gorillas:
            g.health = 100
            g.alive = True

        demo_game.handle_projectile_physics(dt)
        demo_game.cloud_manager.update(dt)
        for e in list(demo_game.explosions):
            e['t'] += dt
            if e['t'] > 0.6:
                demo_game.explosions.remove(e)

        demo_game.screen = screen
        demo_game.draw_scene()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input1_rect.collidepoint(event.pos):
                    active_input = 1
                elif input2_rect.collidepoint(event.pos):
                    active_input = 2
                else:
                    active_input = None

                if button_rect.collidepoint(event.pos):
                    if pseudo1 and pseudo2:
                        return pseudo1, pseudo2

                if quit_rect.collidepoint(event.pos):
                    return None, None

            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    if active_input == 1:
                        pseudo1 = pseudo1[:-1]
                    else:
                        pseudo2 = pseudo2[:-1]
                else:
                    if active_input == 1 and len(pseudo1) < 10:
                        pseudo1 += event.unicode
                    elif active_input == 2 and len(pseudo2) < 10:
                        pseudo2 += event.unicode

        # zones pseudo
        pygame.draw.rect(screen, WHITE, input1_rect, 2)
        pygame.draw.rect(screen, WHITE, input2_rect, 2)
        screen.blit(font.render(pseudo1, True, WHITE), (input1_rect.x + 10, input1_rect.y + 5))
        screen.blit(font.render(pseudo2, True, WHITE), (input2_rect.x + 10, input2_rect.y + 5))

        # bouton Start
        pygame.draw.rect(screen, BLUE, button_rect)
        text_surf = font.render("Start", True, WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)

        # bouton Quit
        pygame.draw.rect(screen, (200,50,50), quit_rect)
        quit_surf = font.render("Quitter", True, WHITE)
        quit_rect_text = quit_surf.get_rect(center=quit_rect.center)
        screen.blit(quit_surf, quit_rect_text)

        pygame.display.flip()
