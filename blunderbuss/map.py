import pygame

from pygame.locals import *

from blunderbuss.game.level import Level
from blunderbuss.game.models import Entity
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
        self.enemy_img = pygame.image.load("data/images/map/stone.png").convert()
        self.enemy_img.set_colorkey((0, 0, 0))
        self.level = Level()

    def draw(
        self,
        display: pygame.Surface,
        screen: pygame.Surface,
        player: Entity,
        enemies: [Entity],
    ):
        for y, row in enumerate(self.level.tile_data):
            for x, tile in enumerate(row):
                blit_image = None
                if tile == 1:
                    blit_image = self.grass_img
                elif tile == 2:
                    blit_image = self.stone_img
                if blit_image:
                    blit_coords = self.calculate_tile_screen_coordinates(
                        x, y, player, blit_image
                    )
                    display.blit(blit_image, blit_coords)
        for enemy in enemies:
            self.draw_entity(enemy, player, self.enemy_img, display)
        #self.draw_entity(player, player, self.player_img, display)
        self.draw_player(display)
        screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))

    def draw_entity(
        self, entity: Entity, camera: Entity, image: pygame.Surface, display: pygame.Surface
    ):
        coords = self.calculate_tile_screen_coordinates(
            entity.x / 10, entity.y / 5, camera, image
        )
        display.blit(image, coords)

    def draw_player(self, display: pygame.Surface):
        display.blit(
            self.player_img,
            (
                CAMERA_OFFSET_X - self.player_img.get_width() // 2,
                CAMERA_OFFSET_Y - self.player_img.get_height() // 2,
            ),
        )

    @classmethod
    def calculate_tile_screen_coordinates(
        cls, tile_x: int, tile_y: int, camera: Entity, image: pygame.Surface
    ):
        x = (
            CAMERA_OFFSET_X
            + tile_x * 10
            - tile_y * 10
            - camera.x
            - image.get_width() // 2
        )
        y = (
            CAMERA_OFFSET_Y
            + tile_x * 5
            + tile_y * 5
            - camera.y
            - image.get_height() // 2
        )
        return (x, y)
