from pygame.math import Vector2

from blunderbuss.game.map import Map
from blunderbuss.game.models import Character, Direction

SPEED = 5


class World:
    def __init__(self):
        self.map = Map("level1")
        tile_x, tile_y = self.map.get_start_tile()
        position = Vector2(0.5 + tile_x, 0.5 + tile_y)
        self.player = Character(position=position)

    def move_player(self, dt: float, direction: Direction):
        if direction:
            self.player.direction = direction
            dpos = direction.to_vector() * SPEED * dt
            self.player.position += dpos
