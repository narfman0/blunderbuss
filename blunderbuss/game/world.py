from pygame.math import Vector2

from blunderbuss.game.map import Map
from blunderbuss.game.models import Character, Direction

SPEED = 500
TILE_X_SCALAR = 256
TILE_Y_SCALAR = 128


class World:
    def __init__(self):
        self.map = Map("level1")
        tile_x, tile_y = self.map.get_start_tile()
        x, y = self.tile_coords_to_world_coordinates(tile_x, tile_y)
        self.player = Character(position=Vector2(x, y))

    def move_player(self, dt: float, direction: Direction):
        if direction:
            self.player.direction = direction
            dpos = direction.to_vector() * SPEED * dt
            self.player.position += dpos

    @classmethod
    def tile_coords_to_world_coordinates(cls, tile_x: int, tile_y: int):
        x = (
            (tile_x * TILE_X_SCALAR) // 2
            - (tile_y * TILE_X_SCALAR) // 2
            - TILE_X_SCALAR // 2
        )
        y = (
            (tile_x * TILE_Y_SCALAR) // 2
            + (tile_y * TILE_Y_SCALAR) // 2
            - TILE_Y_SCALAR // 2
        )
        return (x, y)
