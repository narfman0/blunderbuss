from blunderbuss.game.level import Level
from blunderbuss.game.models import Entity

SPEED = 1.5


class Driver:
    def __init__(self):
        self.level = Level()
        self.player = Entity()
        self.enemies = [Entity()]

    def move_player(self, x: int, y: int):
        self.player.x += x * SPEED
        self.player.y += y * SPEED
