import pymunk

from blunderbuss.game.map import Map
from blunderbuss.game.models import Character, Direction

SPEED = 200


class World:
    def __init__(self):
        self.space = pymunk.Space()
        self.map = Map("level1")
        tile_x, tile_y = self.map.get_start_tile()
        self.player = Character()
        self.player.body.position = (0.5 + tile_x, 0.5 + tile_y)
        self.player.poly = pymunk.Circle(self.player.body, 1)
        self.player.poly.mass = 10
        self.space.add(self.player.body, self.player.poly)
        self.map.add_map_geometry_to_space(self.space)

    def move_player(self, dt: float, direction: Direction):
        if direction:
            self.player.direction = direction
            dpos = direction.to_vector() * SPEED * dt
            self.player.body.velocity = dpos.x, dpos.y
        else:
            self.player.body.velocity = 0, 0

    def update(self, dt: float):
        self.space.step(dt)
