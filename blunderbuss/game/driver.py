from pygame import Vector2

from blunderbuss.game.map import Map
from blunderbuss.game.models import Character, Direction

SPEED = 5


class Driver:
    def __init__(self):
        self.map = Map("level1")
        self.player = Character()

    def move_player(self, direction: Direction):
        if direction:
            self.player.direction = direction
            self.player.position += (direction.to_vector() * SPEED)
