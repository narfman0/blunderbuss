from blunderbuss.game.map import Map
from blunderbuss.game.models import Entity

SPEED = 5


class Driver:
    def __init__(self):
        self.map = Map("level1")
        self.player = Entity()
        self.enemies = [Entity()]

    def move_player(self, x: int, y: int):
        self.player.x += x * SPEED
        self.player.y += y * SPEED
