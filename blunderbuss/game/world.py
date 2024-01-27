import pymunk

from blunderbuss.game.map import Map
from blunderbuss.game.models import Character, Direction

RUN_FORCE = 25000
RUNNING_STOP_THRESHOLD = 2
MAX_VELOCITY = 5


class World:
    def __init__(self):
        self.space = pymunk.Space()
        self.map = Map("level1")
        tile_x, tile_y = self.map.get_start_tile()
        self.player = Character(position=(0.5 + tile_x, 0.5 + tile_y))
        self.space.add(self.player.body, self.player.poly)
        self.map.add_map_geometry_to_space(self.space)

    def move_player(self, dt: float, direction: Direction):
        if direction:
            self.player.direction = direction
            dpos = direction.to_vector() * RUN_FORCE * dt
            self.player.body.apply_force_at_local_point(force=(dpos.x, dpos.y))
            if self.player.body.velocity.length > MAX_VELOCITY:
                self.player.body.velocity = self.player.body.velocity.scale_to_length(
                    MAX_VELOCITY
                )
        else:
            if self.player.body.velocity.get_length_sqrd() > RUNNING_STOP_THRESHOLD:
                self.player.body.velocity = self.player.body.velocity.scale_to_length(
                    0.7 * self.player.body.velocity.length
                )
            else:
                self.player.body.velocity = (0, 0)

    def update(self, dt: float):
        self.space.step(dt)
