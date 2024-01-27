import pymunk

from blunderbuss.game.map import Map
from blunderbuss.game.models import Character, Direction



class World:
    def __init__(self):
        self.space = pymunk.Space()
        self.map = Map("level1")
        tile_x, tile_y = self.map.get_start_tile()
        self.player = Character(position=(0.5 + tile_x, 0.5 + tile_y))
        self.space.add(self.player.body, self.player.poly)
        self.map.add_map_geometry_to_space(self.space)

    def update(self, dt: float, player_movement_direction: Direction):
        self.player.input_direction = player_movement_direction
        self.player.update(dt)
        self.space.step(dt)
