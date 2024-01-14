import pygame

from pygame.locals import *

from blunderbuss.models import Entity
from blunderbuss.settings import *

CAMERA_OFFSET_X = (WIDTH // SURFACE_SCALAR) // 2
CAMERA_OFFSET_Y = (HEIGHT // SURFACE_SCALAR) // 2


class Map:
    def __init__(self):
        self.grass_img = pygame.image.load("data/images/map/grass.png").convert()
        self.grass_img.set_colorkey((0, 0, 0))
        self.stone_img = pygame.image.load("data/images/map/stone.png").convert()
        self.stone_img.set_colorkey((0, 0, 0))
        self.player_img = pygame.image.load("data/images/player.png").convert()
        self.player_img.set_colorkey((255, 0, 0))

        f = open("data/map.txt")
        self.map_data = [[int(c) for c in row] for row in f.read().split("\n")]
        f.close()

    def draw(self, display: pygame.Surface, screen: pygame.Surface, player: Entity):
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                blit_image = None
                if tile == 1:
                    blit_image = self.grass_img
                elif tile == 2:
                    blit_image = self.stone_img
                if blit_image:
                    blit_coords = (
                        CAMERA_OFFSET_X
                        + x * 10
                        - y * 10
                        - player.x
                        - blit_image.get_width() // 2,
                        CAMERA_OFFSET_Y
                        + x * 5
                        + y * 5
                        - player.y
                        - blit_image.get_height() // 2,
                    )
                    display.blit(blit_image, blit_coords)
        self.draw_player(display)
        screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))

    def draw_player(self, display: pygame.Surface):
        display.blit(
            self.player_img,
            (
                CAMERA_OFFSET_X - self.player_img.get_width() // 2,
                CAMERA_OFFSET_Y - self.player_img.get_height() // 2,
            ),
        )