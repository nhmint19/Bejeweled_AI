import pygame
from pathlib import Path

def load_image(filename):
    return pygame.image.load(Path(filename)).convert_alpha()

class Text(object):
    def __init__(self, font_size, msg, pos = (0, 0), color = "black"):
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.text = self.font.render(msg, 1, color)
        self.rect = self.text.get_rect(topleft = pos)
    
    def update_msg(self, msg):
        self.text = self.font.render(msg, 1, self.color)
        
    def draw(self, screen):
        screen.blit(self.text, self.rect)