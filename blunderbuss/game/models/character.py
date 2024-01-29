from dataclasses import dataclass, field
from uuid import UUID, uuid4 as generate_uuid

import pymunk
from dataclass_wizard import YAMLWizard

from blunderbuss.game.models.direction import Direction


@dataclass
class CharacterProperties(YAMLWizard):
    mass: float = None
    dash_cooldown: float = None
    dash_duration: float = None
    dash_scalar: float = None
    run_force: float = None
    running_stop_threshold: float = None
    max_velocity: float = None
    radius: float = None


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
    character_type: str = None

    def __init__(self, position: tuple[float, float], character_type: str):
        self.character_type = character_type
        self.uuid = generate_uuid()
        character_properties = CharacterProperties.from_yaml_file(
            f"data/characters/{character_type}.yml"
        )
        self.__dict__.update(character_properties.__dict__)
        self.body = pymunk.Body()
        self.body.position = position
        self.poly = pymunk.Circle(self.body, self.radius)
        self.poly.mass = self.mass

    def update(self, dt: float):
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
        if self.movement_direction:
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

    def dash(self):
        if not self.dashing and self.dash_cooldown_remaining <= 0:
            self.dashing = True
            self.dash_time_remaining = self.dash_duration

    @property
    def position(self):
        return self.body.position


class NPC(Character):
    def ai(self, dt: float, player: Character):
        self.movement_direction = Direction.direction_to(self.position, player.position)
