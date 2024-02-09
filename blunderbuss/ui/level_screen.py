import logging
from dataclasses import dataclass
from enum import Enum

import pygame
from pygame.event import Event
from pygame.math import Vector2

from blunderbuss.util.math import cartesian_to_isometric
from blunderbuss.ui.character_sprite import CharacterSprite
from blunderbuss.ui.renderables import *
from blunderbuss.ui.screen import Screen, ScreenManager
from blunderbuss.game.models.character import Character, NPC
from blunderbuss.game.models.direction import Direction
from blunderbuss.game.world import World
from blunderbuss.game.world_callback import WorldCallback
from blunderbuss.settings import *

LOGGER = logging.getLogger(__name__)
SCREEN_SCALE = 4
SCREEN_WIDTH = WIDTH // SCREEN_SCALE
SCREEN_HEIGHT = HEIGHT // SCREEN_SCALE
CAMERA_OFFSET_X = SCREEN_WIDTH // 2
CAMERA_OFFSET_Y = SCREEN_HEIGHT // 2


class ActionEnum(Enum):
    DASH = 1
    ATTACK = 2
    CHARACTER_SWAP = 3


@dataclass
class CharacterStruct:
    character: Character
    sprite: CharacterSprite
    sprite_group: pygame.sprite.Group
    last_movement_direction: Direction


class LevelScreen(Screen, WorldCallback):
    def __init__(self, screen_manager: ScreenManager, world: World):
        self.screen_manager = screen_manager
        self.world = world
        self.player_struct = CharacterStruct(
            self.world.player,
            None,
            pygame.sprite.Group(),
            None,
        )
        self.update_player_sprite()
        self.character_structs = [self.player_struct]
        for enemy in self.world.enemies:
            sprite = CharacterSprite(enemy.character_type)
            self.character_structs.append(
                CharacterStruct(enemy, sprite, pygame.sprite.Group(sprite), None)
            )

        self.tile_x_draw_distance = 2 * SCREEN_WIDTH // self.world.map.tile_width
        self.tile_y_draw_distance = 2 * SCREEN_HEIGHT // self.world.map.tile_height

    def update(self, dt: float, events: list[Event]):
        player_actions = self.read_input_player_actions(events)
        if ActionEnum.DASH in player_actions:
            if not self.world.player.dashing:
                self.world.player.dash()
        if ActionEnum.CHARACTER_SWAP in player_actions:
            if not self.world.player.swapping:
                self.world.player.swap()
                self.update_player_sprite()
        if ActionEnum.ATTACK in player_actions:
            if self.world.player.alive and not self.world.player.attacking:
                self.world.player.attack()
                self.player_struct.sprite.change_animation("attack")
        player_move_direction = self.read_input_player_move_direction()
        self.world.update(dt, player_move_direction, self)
        if (
            self.world.player.alive
            and self.world.player.character_type
            != self.player_struct.sprite.sprite_name
        ):
            # ideally we could pass a callback here but :shrugs:
            self.update_player_sprite()
        self.world.player.facing_direction = player_move_direction

        for character_struct in self.character_structs:
            character = character_struct.character
            sprite = character_struct.sprite
            if character.alive:
                if not character.attacking:
                    if character.facing_direction:
                        if (
                            character.facing_direction
                            != character_struct.last_movement_direction
                        ):
                            sprite.move(character.facing_direction.to_isometric())
                        sprite.change_animation("run")
                    else:
                        sprite.change_animation("idle")
                character_struct.last_movement_direction = character.facing_direction
            else:
                if sprite.sprite_name != "death":
                    sprite.change_animation("death", loop=False)
            x, y = self.calculate_draw_coordinates(
                character.position.x, character.position.y, None, sprite.image
            )
            sprite.set_position(x, y)

        for character_struct in self.character_structs:
            character_struct.sprite_group.update(dt)

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
        renderables = create_renderable_list()
        surface = pygame.Surface(size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        for layer in range(self.world.map.get_tile_layer_count()):
            for x in range(tile_x_begin, tile_x_end):
                for y in range(tile_y_begin, tile_y_end):
                    blit_image = self.world.map.get_tile_image(x, y, layer)
                    if blit_image:
                        blit_x, blit_y = self.calculate_draw_coordinates(
                            x, y, layer, blit_image
                        )
                        bottom_y = blit_y + blit_image.get_height()
                        renderable = BlittableRenderable(
                            renderables_generate_key(layer, bottom_y),
                            blit_image,
                            (blit_x, blit_y),
                        )
                        renderables.add(renderable)
        for character_struct in self.character_structs:
            img_height = character_struct.sprite.image.get_height()
            bottom_y = character_struct.sprite.rect.top + img_height // 2
            key = renderables_generate_key(self.world.map.get_1f_layer_id(), bottom_y)
            renderables.add(SpriteRenderable(key, character_struct.sprite_group))
        for renderable in renderables:
            renderable.draw(surface)
        pygame.transform.scale_by(
            surface, dest_surface=dest_surface, factor=SCREEN_SCALE
        )

    def ai_attack_callback(self, npc: NPC):
        for character_struct in self.character_structs:
            if character_struct.character == npc:
                character_struct.sprite.change_animation("attack")
                character_struct.sprite.move(npc.facing_direction)

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
        iso_x, iso_y = cartesian_to_isometric(cartesian_x, cartesian_y)
        x = iso_x + CAMERA_OFFSET_X - image.get_width() // 2
        y = iso_y + CAMERA_OFFSET_Y - image.get_height() // 2
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

    def read_input_player_actions(self, events: list[Event]) -> list[ActionEnum]:
        actions = []
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    actions.append(ActionEnum.DASH)
                elif event.key == pygame.K_e or event.key == pygame.K_q:
                    actions.append(ActionEnum.CHARACTER_SWAP)
                elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    actions.append(ActionEnum.ATTACK)
                elif event.key == pygame.K_F2:
                    self.world.player.handle_healing_received(1)
                    print(f"Player now has {self.world.player.hp} hp")
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    actions.append(ActionEnum.ATTACK)
        return actions

    def update_player_sprite(self):
        sprite = CharacterSprite(self.world.player.character_type)
        sprite.set_position(
            SCREEN_WIDTH // 2 - sprite.image.get_width() // 2,
            SCREEN_HEIGHT // 2 - sprite.image.get_height() // 2,
        )
        self.player_struct.sprite = sprite
        self.player_struct.sprite_group.empty()
        self.player_struct.sprite_group.add(sprite)
