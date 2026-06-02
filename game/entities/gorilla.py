import pygame



from configuration import SPRITES




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
            sprite_path = SPRITES["panda"]

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
