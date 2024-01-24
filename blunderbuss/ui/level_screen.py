import logging

import pygame
from pygame.math import Vector2

from blunderbuss.util.math import cartesian_to_isometric
from blunderbuss.ui.character_sprite import CharacterSprite
from blunderbuss.ui.screen import Screen, ScreenManager
from blunderbuss.game.world import World
from blunderbuss.game.models import Direction, Entity
from blunderbuss.settings import *

LOGGER = logging.getLogger(__name__)
CAMERA_OFFSET_X = WIDTH // 2
CAMERA_OFFSET_Y = HEIGHT // 2
TILE_X_SCALAR = 256
TILE_Y_SCALAR = 128
TILE_DRAW_X_DISTANCE = 2 * WIDTH // TILE_X_SCALAR
TILE_DRAW_Y_DISTANCE = 2 * HEIGHT // TILE_Y_SCALAR


class LevelScreen(Screen):
    def __init__(self, screen_manager: ScreenManager, world: World):
        self.screen_manager = screen_manager
        self.world = world
        self.player_sprite = CharacterSprite("kenney_male")
        self.player_sprite.set_position(WIDTH // 2, HEIGHT // 2)
        self.sprites = pygame.sprite.Group(self.player_sprite)
        self.last_player_move_direction = None

    def update(self, dt: float):
        player_move_direction = self.read_player_move_direction()
        self.world.move_player(dt, player_move_direction)
        if player_move_direction:
            if player_move_direction != self.last_player_move_direction:
                self.player_sprite.move(player_move_direction.to_isometric())
            self.player_sprite.active_animation_name = "run"
        else:
            self.player_sprite.active_animation_name = "idle"
        self.last_player_move_direction = player_move_direction
        self.sprites.update()

    def read_player_move_direction(self):
        keys = pygame.key.get_pressed()
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        up = keys[pygame.K_UP] or keys[pygame.K_w]
        down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        direction = None
        if down:
            if right:
                direction = Direction.E
            elif left:
                direction = Direction.S
            else:
                direction = Direction.SE
        elif up:
            if right:
                direction = Direction.N
            elif left:
                direction = Direction.W
            else:
                direction = Direction.NW
        elif left:
            direction = Direction.SW
        elif right:
            direction = Direction.NE
        return direction

    def draw(self, surface: pygame.Surface):
        tile_x_begin = max(0, int(self.world.player.position.x) - TILE_DRAW_X_DISTANCE)
        tile_x_end = min(
            self.world.map.tmxdata.width,
            int(self.world.player.position.x) + TILE_DRAW_X_DISTANCE,
        )
        tile_y_begin = max(0, int(self.world.player.position.y) - TILE_DRAW_Y_DISTANCE)
        tile_y_end = min(
            self.world.map.tmxdata.height,
            int(self.world.player.position.y) + TILE_DRAW_Y_DISTANCE,
        )
        for layer in range(self.world.map.get_tile_layer_count()):
            for x in range(tile_x_begin, tile_x_end):
                for y in range(tile_y_begin, tile_y_end):
                    blit_image = self.world.map.get_tile_image(x, y, layer)
                    if blit_image:
                        blit_coords = self.calculate_tile_screen_coordinates(
                            x, y, self.world.player, blit_image
                        )
                        surface.blit(blit_image, blit_coords)
        self.sprites.draw(surface)

    @classmethod
    def calculate_tile_screen_coordinates(
        cls, tile_x: int, tile_y: int, camera: Entity, image: pygame.Surface
    ):
        cartesian_x = (tile_x - camera.position.x) * TILE_X_SCALAR // 2
        cartesian_y = (tile_y - camera.position.y) * TILE_X_SCALAR // 2
        isometric_coords = cartesian_to_isometric(Vector2(cartesian_x, cartesian_y))
        x = isometric_coords.x + CAMERA_OFFSET_X - image.get_width() // 2
        y = isometric_coords.y + CAMERA_OFFSET_Y - image.get_height() // 2
        return (x, y)