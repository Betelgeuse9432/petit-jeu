from game.gorillagame import GorillaGame
from configuration import FPS
from game.systems.interface import show_menu
import pygame
import os

def main():
    running_global = True

    while running_global:
        pseudo1, pseudo2 = show_menu()
        if not pseudo1 or not pseudo2:
            break

        game = GorillaGame(pseudo1=pseudo1, pseudo2=pseudo2)

        running_game = True
        while running_game:
            time_delta = game.clock.tick(FPS) / 1000.0
            running_game = game.handle_events()
            action = game.update(time_delta)
            game.draw()

            if action == "quit":
                running_game = False
                running_global = False
            elif action == "rejouer":
                running_game = False

    pygame.quit()

if __name__ == "__main__":
    main()
