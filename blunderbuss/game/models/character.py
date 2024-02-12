from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4 as generate_uuid

import pymunk
from dataclass_wizard import YAMLWizard

from blunderbuss.game.models.direction import Direction
from blunderbuss.game.world_callback import WorldCallback

SWAP_DURATION = 0.1


class AttackType(Enum):
    MELEE = 1
    RANGED = 2


@dataclass
class CharacterProperties(YAMLWizard):
    mass: float = 10
    dash_cooldown: float = None
    dash_duration: float = None
    dash_scalar: float = None
    run_force: float = 1000
    running_stop_threshold: float = 1.0
    max_velocity: float = 1
    radius: float = 0.5
    attack_duration: float = None
    attack_distance: float = None
    attack_time_until_damage: float = None
    attack_type: AttackType = AttackType.MELEE
    attack_profile_name: str = None
    hp_max: int = 1
    chase_distance: float = 15


@dataclass
class Character(CharacterProperties):
    uuid: UUID = field(default_factory=generate_uuid)
    facing_direction: Direction = Direction.S
    movement_direction: Direction = None
    poly: pymunk.Poly = None
    body: pymunk.Body = None
    dashing: bool = False
    dash_time_remaining: float = 0
    dash_cooldown_remaining: float = 0
    attacking: bool = False
    attack_time_remaining: float = 0
    attack_damage_time_remaining: float = 0
    should_process_attack: bool = False
    character_type: str = None
    hp: int = 1
    invincible: bool = False

    def __init__(self, position: tuple[float, float], character_type: str):
        self.character_type = character_type
        self.uuid = generate_uuid()
        self.apply_character_properties()
        self.hp = self.hp_max
        self.body = pymunk.Body()
        self.body.character = self
        self.body.position = position
        self.poly = pymunk.Circle(self.body, self.radius)
        self.poly.mass = self.mass

    def handle_damage_received(self, dmg: int):
        if not self.invincible:
            self.hp = max(0, self.hp - dmg)
            if not self.alive:
                self.body._set_type(pymunk.Body.STATIC)

    def handle_healing_received(self, amount: int):
        self.hp = min(self.hp_max, self.hp + amount)
        if self.alive:
            self.body._set_type(pymunk.Body.DYNAMIC)

    def update(self, dt: float):
        if self.alive and self.movement_direction and not self.attacking:
            self.facing_direction = self.movement_direction
            dash_scalar = self.dash_scalar if self.dashing else 1.0
            dpos = (
                self.movement_direction.to_vector() * self.run_force * dash_scalar * dt
            )
            self.body.apply_force_at_local_point(force=(dpos.x, dpos.y))
            if self.body.velocity.length > self.max_velocity * dash_scalar:
                self.body.velocity = self.body.velocity.scale_to_length(
                    self.max_velocity * dash_scalar
                )
        else:
            if self.body.velocity.get_length_sqrd() > self.running_stop_threshold:
                self.body.velocity = self.body.velocity.scale_to_length(
                    0.7 * self.body.velocity.length
                )
            else:
                self.body.velocity = (0, 0)
        if not self.alive:
            return
        if self.dashing:
            self.dash_time_remaining -= dt
            if self.dash_time_remaining <= 0:
                self.dashing = 0
                self.dash_time_remaining = 0
                self.dash_cooldown_remaining = self.dash_cooldown
        elif self.dash_cooldown_remaining > 0:
            self.dash_cooldown_remaining -= dt
            if self.dash_cooldown_remaining <= 0:
                self.dash_cooldown_remaining = 0

        if self.attacking:
            self.attack_time_remaining -= dt
            if self.attack_damage_time_remaining > 0:
                self.attack_damage_time_remaining -= dt
                if self.attack_damage_time_remaining <= 0:
                    self.attack_damage_time_remaining = 0
                    self.should_process_attack = True
            if self.attack_time_remaining <= 0:
                self.attacking = False

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.attack_time_remaining = self.attack_duration
            self.attack_damage_time_remaining = self.attack_time_until_damage
            if self.movement_direction:  # maybe standing still
                self.facing_direction = self.movement_direction

    def dash(self):
        if not self.dashing and self.dash_cooldown_remaining <= 0:
            self.dashing = True
            self.dash_time_remaining = self.dash_duration

    def apply_character_properties(self):
        path = f"data/characters/{self.character_type}/character.yml"
        character_properties = CharacterProperties.from_yaml_file(path)
        self.__dict__.update(character_properties.__dict__)

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position

    @property
    def alive(self) -> bool:
        return self.hp > 0


class Player(Character):
    swapping: bool = False
    swap_time_remaining: float = 0
    swap_character_type: str = None

    def update(self, dt: float):
        super().update(dt)
        if self.alive and self.swapping:
            self.swap_time_remaining -= dt
            if self.swap_time_remaining <= 0:
                self.swap_time_remaining = 0
                self.swapping = False
                self.character_type = self.swap_character_type
                self.swap_character_type = None
                self.apply_character_properties()

    def swap(self):
        if not self.alive or self.swapping:
            return
        if self.character_type == "pigsassin":
            self.swap_character_type = "droid_assassin"
        elif self.character_type == "droid_assassin":
            self.swap_character_type = "pigsassin"
        else:
            print(f"Unknown character type {self.character_type}")
        self.swap_time_remaining = SWAP_DURATION
        self.swapping = True

    def dash(self):
        if not self.swapping:
            super().dash()


class NPC(Character):
    def ai(self, dt: float, player: Character, world_callback: WorldCallback):
        if not self.alive:
            return
        self.movement_direction = None
        if not player.alive:
            return
        player_dst_sqrd = self.position.get_dist_sqrd(player.position)
        if player_dst_sqrd < self.chase_distance**2:
            self.movement_direction = Direction.direction_to(
                self.position, player.position
            )
        if player_dst_sqrd < self.attack_distance**2 and not self.attacking:
            self.attack()
            world_callback.ai_attack_callback(self)
