import logging
from dataclasses import dataclass

import pygame
from pygame.event import Event

from blunderbuss.util.math import cartesian_to_isometric
from blunderbuss.ui.level.input import (
    ActionEnum,
    read_input_player_move_direction,
    read_input_player_actions,
)
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
        self.projectile_image_dict = {}
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

        self.ground_renderables = list(self.generate_map_renderables(ground=True))
        self.map_renderables = list(self.generate_map_renderables(ground=False))

    def update(self, dt: float, events: list[Event]):
        player_actions = read_input_player_actions(events)
        self.handle_player_actions(player_actions)
        player_move_direction = read_input_player_move_direction()
        self.world.update(dt, player_move_direction, self)
        self.cam_x, self.cam_y = cartesian_to_isometric(
            self.world.player.position.x * self.world.map.tile_half_width,
            self.world.player.position.y * self.world.map.tile_half_width,
        )
        if (
            self.world.player.alive
            and self.world.player.character_type
            != self.player_struct.sprite.sprite_name
        ):
            # ideally we could pass a callback here but :shrugs:
            self.update_player_sprite()
        self.world.player.facing_direction = player_move_direction
        self.update_character_structs(dt)

    def handle_player_actions(self, player_actions: list[ActionEnum]):
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
        if ActionEnum.PLAYER_HEAL in player_actions:
            self.world.player.handle_healing_received(1)
            print(f"Player now has {self.world.player.hp} hp")
        if ActionEnum.PLAYER_INVICIBILITY in player_actions:
            self.world.player.invincible = not self.world.player.invincible
            print(f"Player invincibility set to {self.world.player.invincible}")

    def draw(self, dest_surface: pygame.Surface):
        renderables = create_renderable_list()
        for map_renderable in self.map_renderables:
            blit_x, blit_y = map_renderable.blit_coords
            bottom_y = blit_y - self.cam_y + map_renderable.blit_image.get_height() - 8
            renderable = BlittableRenderable(
                renderables_generate_key(map_renderable.layer, bottom_y),
                map_renderable.blit_image,
                (blit_x - self.cam_x, blit_y - self.cam_y),
            )
            renderables.add(renderable)
        for renderable in self.generate_projectile_renderables():
            renderables.add(renderable)
        for character_struct in self.character_structs:
            img_height = character_struct.sprite.image.get_height()
            bottom_y = character_struct.sprite.rect.top + img_height // 2
            key = renderables_generate_key(self.world.map.get_1f_layer_id(), bottom_y)
            renderables.add(SpriteRenderable(key, character_struct.sprite_group))

        surface = pygame.Surface(size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        for ground_renderable in self.ground_renderables:
            blit_x, blit_y = ground_renderable.blit_coords
            blit_coords = (blit_x - self.cam_x, blit_y - self.cam_y)
            surface.blit(ground_renderable.blit_image, blit_coords)
        for renderable in renderables:
            renderable.draw(surface)
        pygame.transform.scale_by(
            surface, dest_surface=dest_surface, factor=SCREEN_SCALE
        )

    def generate_projectile_renderables(self):
        for projectile in self.world.projectiles:
            image = self.projectile_image_dict.get(projectile.attack_profile.image_path)
            if image is None:
                path = f"data/projectiles/{projectile.attack_profile.image_path}.png"
                image = pygame.image.load(path).convert_alpha()
                self.projectile_image_dict[projectile.attack_profile.image_path] = image
            blit_x, blit_y = self.calculate_draw_coordinates(
                projectile.x, projectile.y, image
            )
            bottom_y = blit_y - self.cam_y + image.get_height()
            yield BlittableRenderable(
                renderables_generate_key(self.world.map.get_1f_layer_id(), bottom_y),
                image,
                (blit_x - self.cam_x, blit_y - self.cam_y),
            )

    def update_character_structs(self, dt: float):
        for character_struct in self.character_structs:
            character = character_struct.character
            sprite = character_struct.sprite
            if character.alive:
                if not character.attacking:
                    if character.movement_direction:
                        if (
                            character.movement_direction
                            != character_struct.last_movement_direction
                        ):
                            sprite.move(character.movement_direction.to_isometric())
                        sprite.change_animation("run")
                    else:
                        sprite.change_animation("idle")
                character_struct.last_movement_direction = character.facing_direction
            else:
                if sprite.sprite_name != "death":
                    sprite.change_animation("death", loop=False)
            x, y = self.calculate_draw_coordinates(
                character.position.x, character.position.y, sprite.image
            )
            sprite.set_position(x - self.cam_x, y - self.cam_y)

        for character_struct in self.character_structs:
            character_struct.sprite_group.update(dt)

    def ai_attack_callback(self, npc: NPC):
        for character_struct in self.character_structs:
            if character_struct.character == npc:
                character_struct.sprite.change_animation("attack")
                character_struct.sprite.move(npc.facing_direction)

    def generate_map_renderables(self, ground: bool):
        """We can statically generate the blit coords once in the beginning, avoiding a bunch of coordinate conversions."""
        ground_ids = self.world.map.get_ground_layer_ids()
        for layer in range(self.world.map.get_tile_layer_count()):
            if ground and layer not in ground_ids or not ground and layer in ground_ids:
                continue
            x_offset, y_offset = self.world.map.get_layer_offsets(layer)
            for x in range(0, self.world.map.width):
                for y in range(0, self.world.map.height):
                    blit_image = self.world.map.get_tile_image(x, y, layer)
                    if blit_image:
                        blit_x, blit_y = self.calculate_draw_coordinates(
                            x, y, blit_image
                        )
                        yield MapRenderable(
                            layer=layer,
                            blit_image=blit_image,
                            blit_coords=(blit_x + x_offset, blit_y + y_offset),
                        )

    def calculate_draw_coordinates(
        self,
        x: float,
        y: float,
        image: pygame.Surface,
    ):
        cartesian_x = x * self.world.map.tile_half_width
        cartesian_y = y * self.world.map.tile_half_width
        iso_x, iso_y = cartesian_to_isometric(cartesian_x, cartesian_y)
        x = iso_x + CAMERA_OFFSET_X - image.get_width() // 2
        y = iso_y + CAMERA_OFFSET_Y - image.get_height() // 2
        return (x, y)

    def update_player_sprite(self):
        sprite = CharacterSprite(self.world.player.character_type)
        sprite.set_position(
            SCREEN_WIDTH // 2 - sprite.image.get_width() // 2,
            SCREEN_HEIGHT // 2 - sprite.image.get_height() // 2,
        )
        self.player_struct.sprite = sprite
        self.player_struct.sprite_group.empty()
        self.player_struct.sprite_group.add(sprite)
