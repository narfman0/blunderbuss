from dataclasses import dataclass, field

from pymunk import Body, Circle

from blunderbuss.game.models.character import Character


@dataclass
class Projectile:
    x: float
    y: float
    dx: float
    dy: float
    origin: Character
    attack_profile_name: str
    body: Body = None
    shape: Circle = None

    def __post_init__(self):
        self.body = Body()
        self.body.position = (self.x, self.y)
        self.shape = Circle(body=self.body, radius=0.5)

    def update(self, dt: float):
        self.x += dt * self.dx
        self.y += dt * self.dy
        self.body.position = (self.x, self.y)
