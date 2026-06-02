import pygame
import random
import sys


# --- Classe Confetti ---
class Confetti:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(-height, 0)
        self.color = random.choice([(255,0,0),(0,255,0),(0,0,255),
                                    (255,255,0),(255,0,255),(0,255,255)])
        self.size = random.randint(5, 10)
        self.speed = random.randint(2, 6)
        self.width = width
        self.height = height

    def update(self):
        self.y += self.speed
        if self.y > self.height:
            self.y = random.randint(-self.height, 0)
            self.x = random.randint(0, self.width)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)
        

# --- Classe Interface de fin ---
class InterfaceFin:
    def __init__(self, screen, width=800, height=600):
        self.screen = screen
        self.width = width
        self.height = height
        self.confettis = [Confetti(width, height) for _ in range(100)]
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("Arial", 70)
        self.button_font = pygame.font.SysFont("Arial", 40)
        self.button_rect = pygame.Rect(width//2 - 220, height//2 + 100, 200, 60)   # Rejouer
        self.quit_rect = pygame.Rect(width//2 + 20,  height//2 + 100, 200, 60)    # Quitter

    def afficher(self, winner_name):
        while True:
            self.screen.fill((0,0,0))

            # Texte gagnant
            text = self.font_big.render(f"{winner_name} a gagné !", True, (255,255,255))
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(text, text_rect)

            # Confettis
            for c in self.confettis:
                c.update()
                c.draw(self.screen)

            # Bouton rejouer
            pygame.draw.rect(self.screen, (50,150,255), self.button_rect)
            btn_text = self.button_font.render("Rejouer", True, (255,255,255))
            self.screen.blit(btn_text, btn_text.get_rect(center=self.button_rect.center))

            pygame.draw.rect(self.screen, (200,50,50), self.quit_rect)
            quit_text = self.button_font.render("Quitter", True, (255,255,255))
            self.screen.blit(quit_text, quit_text.get_rect(center=self.quit_rect.center))

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect.collidepoint(event.pos):
                        return "rejouer"
                    if self.quit_rect.collidepoint(event.pos):
                        return "quit"
