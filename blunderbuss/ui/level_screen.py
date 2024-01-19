import logging

import pygame


from blunderbuss.ui.screen import Screen, ScreenManager
from blunderbuss.game.world import World
from blunderbuss.game.models import Direction, Entity
from blunderbuss.settings import *

LOGGER = logging.getLogger(__name__)
CAMERA_OFFSET_X = WIDTH // 2
CAMERA_OFFSET_Y = HEIGHT // 2
TILE_X_SCALAR = 256
TILE_Y_SCALAR = 128


class LevelScreen(Screen):
    def __init__(self, screen_manager: ScreenManager, world: World):
        self.screen_manager = screen_manager
        self.world = world
        self.player_img = pygame.image.load("data/images/characters/kenney_male/Male_3_Idle0.png").convert()
        self.player_img.set_colorkey((0, 255, 0))

    def update(self, dt: float):
        player_move_direction = self.read_player_move_direction()
        self.world.move_player(dt, player_move_direction)

    def read_player_move_direction(self):
        keys = pygame.key.get_pressed()
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        up = keys[pygame.K_UP] or keys[pygame.K_w]
        down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        direction = None
        if down:
            if right:
                direction = Direction.SE
            elif left:
                direction = Direction.SW
            else:
                direction = Direction.S
        elif up:
            if right:
                direction = Direction.NE
            elif left:
                direction = Direction.NW
            else:
                direction = Direction.N
        elif left:
            direction = Direction.W
        elif right:
            direction = Direction.E
        return direction

    def draw(
        self,
        surface: pygame.Surface,
    ):
        tile_x_begin = 0
        tile_x_end = self.world.map.tmxdata.width
        tile_y_begin = 0
        tile_y_end = self.world.map.tmxdata.height
        for layer in range(self.world.map.get_tile_layer_count()):
            for x in range(tile_x_begin, tile_x_end):
                for y in range(tile_y_begin, tile_y_end):
                    blit_image = self.world.map.get_tile_image(x, y, layer)
                    if blit_image:
                        blit_coords = self.calculate_tile_screen_coordinates(
                            x, y, self.world.player, blit_image
                        )
                        surface.blit(blit_image, blit_coords)
        self.draw_player(surface)

    def draw_player(self, surface: pygame.Surface):
        surface.blit(
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
