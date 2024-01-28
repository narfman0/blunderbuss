import logging
from uuid import UUID

import pygame
from pygame.event import Event
from pygame.math import Vector2

from blunderbuss.util.math import cartesian_to_isometric
from blunderbuss.ui.character_sprite import CharacterSprite
from blunderbuss.ui.screen import Screen, ScreenManager
from blunderbuss.game.models.character import Character
from blunderbuss.game.models.direction import Direction
from blunderbuss.game.world import World
from blunderbuss.settings import *

LOGGER = logging.getLogger(__name__)
SCREEN_SCALE = 4
SCREEN_WIDTH = WIDTH // SCREEN_SCALE
SCREEN_HEIGHT = HEIGHT // SCREEN_SCALE
CAMERA_OFFSET_X = SCREEN_WIDTH // 2
CAMERA_OFFSET_Y = SCREEN_HEIGHT // 2


class LevelScreen(Screen):
    def __init__(self, screen_manager: ScreenManager, world: World):
        self.screen_manager = screen_manager
        self.world = world
        self.player_sprite = CharacterSprite(world.player.character_type)
        self.player_sprite.set_position(
            SCREEN_WIDTH // 2 - self.player_sprite.image.get_width() // 2,
            SCREEN_HEIGHT // 2 - self.player_sprite.image.get_height() // 2,
        )
        self.player_sprite_group = pygame.sprite.Group(self.player_sprite)
        self.last_player_move_direction = None
        self.enemy_uuid_to_sprite_map: dict[UUID, CharacterSprite] = {}
        self.enemy_uuid_to_enemy_map: dict[UUID, Character] = {}
        self.enemy_sprite_group = pygame.sprite.Group()
        for enemy in self.world.enemies:
            sprite = CharacterSprite(enemy.character_type)
            self.enemy_uuid_to_sprite_map[enemy.uuid] = sprite
            self.enemy_uuid_to_enemy_map[enemy.uuid] = enemy
            self.enemy_sprite_group.add(sprite)

        self.tile_x_draw_distance = 2 * SCREEN_WIDTH // self.world.map.tile_width
        self.tile_y_draw_distance = 2 * SCREEN_HEIGHT // self.world.map.tile_height

    def update(self, dt: float, events: list[Event]):
        if self.read_input_player_dashing(events):
            if not self.world.player.dashing:
                self.world.player.dash()
        player_move_direction = self.read_input_player_move_direction()
        self.world.update(dt, player_move_direction)
        if player_move_direction:
            if player_move_direction != self.last_player_move_direction:
                self.player_sprite.move(player_move_direction.to_isometric())
            self.player_sprite.active_animation_name = "run"
        else:
            self.player_sprite.active_animation_name = "idle"
        self.last_player_move_direction = player_move_direction
        self.player_sprite_group.update()
        self.enemy_sprite_group.update()

    def draw(self, dest_surface: pygame.Surface):
        player_tile_x = int(self.world.player.position.x)
        player_tile_y = int(self.world.player.position.y)
        tile_x_begin = max(0, player_tile_x - self.tile_x_draw_distance)
        tile_x_end = min(
            self.world.map.width,
            player_tile_x + self.tile_x_draw_distance,
        )
        tile_y_begin = max(0, player_tile_y - self.tile_y_draw_distance)
        tile_y_end = min(
            self.world.map.height,
            player_tile_y + self.tile_y_draw_distance,
        )
        surface = pygame.Surface(size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        for layer in range(self.world.map.get_tile_layer_count()):
            for x in range(tile_x_begin, tile_x_end):
                for y in range(tile_y_begin, tile_y_end):
                    blit_image = self.world.map.get_tile_image(x, y, layer)
                    if blit_image:
                        blit_coords = self.calculate_draw_coordinates(
                            x, y, layer, blit_image
                        )
                        surface.blit(blit_image, blit_coords)
                    if (
                        player_tile_y == y
                        and player_tile_x == x
                        and self.world.map.get_layer_name(layer) == "1f"
                    ):
                        self.player_sprite_group.draw(surface)
        for enemy_uuid, sprite in self.enemy_uuid_to_sprite_map.items():
            enemy = self.enemy_uuid_to_enemy_map[enemy_uuid]
            x, y = self.calculate_draw_coordinates(
                enemy.position.x, enemy.position.y, None, sprite.image
            )
            sprite.set_position(x, y)
            self.enemy_sprite_group.draw(surface)
        pygame.transform.scale_by(
            surface, dest_surface=dest_surface, factor=SCREEN_SCALE
        )

    def calculate_draw_coordinates(
        self,
        x: float,
        y: float,
        layer: int | None,
        image: pygame.Surface,
    ):
        camera_pos = self.world.player.body.position
        x_offset, y_offset = (
            self.world.map.get_layer_offsets(layer) if layer is not None else (0, 0)
        )
        cartesian_x = (x - camera_pos.x) * self.world.map.tile_width // 2
        cartesian_y = (y - camera_pos.y) * self.world.map.tile_width // 2
        isometric_coords = cartesian_to_isometric(Vector2(cartesian_x, cartesian_y))
        x = isometric_coords.x + CAMERA_OFFSET_X - image.get_width() // 2
        y = isometric_coords.y + CAMERA_OFFSET_Y - image.get_height() // 2
        return (x + x_offset, y + y_offset)

    def read_input_player_move_direction(self):
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

    def read_input_player_dashing(self, events: list[Event]) -> bool:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
        return False
