import pygame, utils

CELL_IMAGES = [
    "assets/yellow.png",
    "assets/red.png",
    "assets/orange.png",
    "assets/green.png",
    "assets/blue.png",
    "assets/purple.png",
    "assets/white.png"
]

CELL_SIZE = 64
MARGIN = 20

class Gem(object):
    def __init__(self, gem_type, pos):
        self.reset(gem_type)
        # init position
        self.rect = pygame.Rect(MARGIN, MARGIN, CELL_SIZE, CELL_SIZE) # rectangle surrounding the image
        self.rect.topleft = pos

        # init velocity for moving when swpping gems
        self.vel = []
        self.is_selected = False

    def reset(self, gem_type):
        # images for gem
        self.gem_type = gem_type
        self.images = None
        if gem_type >= 0: # gem exists
            self.images = []
            self.images.append(utils.load_image(CELL_IMAGES[gem_type]))

    def draw(self, surface):        
        if self.images:
            surface.blit(self.images[0], self.rect)
        if self.is_selected:
            pygame.draw.rect(surface, "red", self.rect, 3) # highlight the border
        