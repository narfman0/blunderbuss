from dataclasses import dataclass, field
from uuid import UUID, uuid4 as generate_uuid

import pymunk

from blunderbuss.game.models.character import CharacterProperties
from blunderbuss.game.models.direction import Direction


@dataclass
class Character(CharacterProperties):
    uuid: UUID = field(default_factory=generate_uuid)
    facing_direction: Direction = Direction.S
    movement_direction: Direction = None
    shape: pymunk.Shape = None
    body: pymunk.Body = None
    hitbox_shape: pymunk.Shape = None
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
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.mass = self.mass
        self.hitbox_shape = pymunk.Segment(
            self.body, (0, 0), (self.attack_distance, 0), radius=1
        )
        self.hitbox_shape.sensor = True

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
            self.body.angle = self.facing_direction.angle
            dash_scalar = self.dash_scalar if self.dashing else 1.0
            dpos = (
                self.movement_direction.to_vector() * self.run_force * dash_scalar * dt
            )
            self.body.apply_force_at_world_point(
                force=(dpos.x, dpos.y), point=(self.position.x, self.position.y)
            )
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
