import pygame, sys, time, random

from pygame.locals import *


class Map:
    def __init__(self):
        self.grass_img = pygame.image.load('data/grass.png').convert()
        self.grass_img.set_colorkey((0, 0, 0))

        f = open('data/map.txt')
        self.map_data = [[int(c) for c in row] for row in f.read().split('\n')]
        f.close()

    def tick(self, display, screen):
            for y, row in enumerate(self.map_data):
                for x, tile in enumerate(row):
                    if tile:
                        display.blit(self.grass_img, (150 + x * 10 - y * 10, 100 + x * 5 + y * 5))
            screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
