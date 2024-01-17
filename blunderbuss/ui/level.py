import pygame

from pygame.locals import *

from blunderbuss.game.driver import Driver
from blunderbuss.game.models import Entity
from blunderbuss.settings import *

CAMERA_OFFSET_X = (WIDTH // SURFACE_SCALAR) // 2
CAMERA_OFFSET_Y = (HEIGHT // SURFACE_SCALAR) // 2
TILE_X_SCALAR = 256
TILE_Y_SCALAR = 128


class LevelUI:
    def __init__(self):
        self.player_img = pygame.image.load("data/images/player.png").convert()
        self.player_img.set_colorkey((255, 0, 0))
        self.enemy_img = pygame.image.load("data/images/player.png").convert()
        self.enemy_img.set_colorkey((0, 0, 0))

    def draw(
        self,
        display: pygame.Surface,
        screen: pygame.Surface,
        driver: Driver,
    ):
        tile_x_begin = 0
        tile_x_end = driver.map.tmxdata.width
        tile_y_begin = 0
        tile_y_end = driver.map.tmxdata.height
        for layer in range(driver.map.get_tile_layer_count()):
            for x in range(tile_x_begin, tile_x_end):
                for y in range(tile_y_begin, tile_y_end):
                    blit_image = driver.map.get_tile_image(x, y, layer)
                    if blit_image:
                        blit_coords = self.calculate_tile_screen_coordinates(
                            x, y, driver.player, blit_image
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

    @classmethod
    def calculate_tile_screen_coordinates(
        cls, tile_x: int, tile_y: int, camera: Entity, image: pygame.Surface
    ):
        x = (
            CAMERA_OFFSET_X
            + (tile_x * TILE_X_SCALAR) // 2
            - (tile_y * TILE_X_SCALAR) // 2
            - camera.position.x
            - image.get_width() // 2
        )
        y = (
            CAMERA_OFFSET_Y
            + (tile_x * TILE_Y_SCALAR) // 2
            + (tile_y * TILE_Y_SCALAR) // 2
            - camera.position.y
            - image.get_height() // 2
        )
        return (x, y)
