from dataclasses import dataclass

from blunderbuss.game.models.character import Character


@dataclass
class Projectile:
    x: float
    y: float
    dx: float
    dy: float
    origin: Character
    attack_profile_name: str

    def update(self, dt: float):
        self.x += dt * self.dx
        self.y += dt * self.dy
