import pygame

from pygame.locals import *


class Map:
    def __init__(self):
        self.grass_img = pygame.image.load('data/images/map/grass.png').convert()
        self.grass_img.set_colorkey((0, 0, 0))
        self.stone_img = pygame.image.load('data/images/map/stone.png').convert()
        self.stone_img.set_colorkey((0, 0, 0))

        f = open('data/map.txt')
        self.map_data = [[int(c) for c in row] for row in f.read().split('\n')]
        f.close()

    def draw(self, display: pygame.Surface, screen: pygame.Surface):
            for y, row in enumerate(self.map_data):
                for x, tile in enumerate(row):
                    blit_coords = (150 + x * 10 - y * 10, 100 + x * 5 + y * 5)
                    blit_image = None
                    if tile == 1:
                        blit_image = self.grass_img
                    elif tile == 2:
                        blit_image = self.stone_img
                    if blit_image:
                        display.blit(blit_image, blit_coords)
            screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
