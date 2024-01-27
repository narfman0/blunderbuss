from dataclasses import dataclass

import pymunk

from blunderbuss.game.models.direction import Direction

CHARACTER_MASS = 10
DASH_COOLDOWN = 0.25
DASH_DURATION = 0.25
DASH_SCALAR = 3
RUN_FORCE = 25000
RUNNING_STOP_THRESHOLD = 2
MAX_VELOCITY = 5

@dataclass
class Character:
    facing_direction: Direction = Direction.S
    input_direction: Direction = None
    poly: pymunk.Poly = None
    body: pymunk.Body = None
    dashing: bool = False
    dash_time_remaining: float = 0
    dash_cooldown_remaining: float = 0

    def __init__(self, position: tuple[float, float]):
        self.body = pymunk.Body()
        self.body.position = position
        self.poly = pymunk.Circle(self.body, 0.5)
        self.poly.mass = CHARACTER_MASS

    def update(self, dt: float):
        if self.dashing:
            self.dash_time_remaining -= dt
            if self.dash_time_remaining <= 0:
                self.dashing = 0
                self.dash_time_remaining = 0
                self.dash_cooldown_remaining = DASH_COOLDOWN
        elif self.dash_cooldown_remaining > 0:
            self.dash_cooldown_remaining -= dt
            if self.dash_cooldown_remaining <= 0:
                self.dash_cooldown_remaining = 0
        if self.input_direction:
            self.facing_direction = self.input_direction
            dash_scalar = DASH_SCALAR if self.dashing else 1.0
            dpos = self.input_direction.to_vector() * RUN_FORCE * dash_scalar * dt
            self.body.apply_force_at_local_point(force=(dpos.x, dpos.y))
            if self.body.velocity.length > MAX_VELOCITY * dash_scalar:
                self.body.velocity = self.body.velocity.scale_to_length(
                    MAX_VELOCITY * dash_scalar
                )
        else:
            if self.body.velocity.get_length_sqrd() > RUNNING_STOP_THRESHOLD:
                self.body.velocity = self.body.velocity.scale_to_length(
                    0.7 * self.body.velocity.length
                )
            else:
                self.body.velocity = (0, 0)

    def dash(self):
        if not self.dashing and self.dash_cooldown_remaining <= 0:
            self.dashing = True
            self.dash_time_remaining = DASH_DURATION

    @property
    def position(self):
        return self.body.position
