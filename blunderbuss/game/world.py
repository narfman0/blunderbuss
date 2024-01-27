import pymunk

from blunderbuss.game.models.level import Level
from blunderbuss.game.map import Map
from blunderbuss.game.models.character import Character
from blunderbuss.game.models.direction import Direction


class World:
    def __init__(self, level_name="1"):
        self.space = pymunk.Space()
        self.level = Level.from_yaml_file(f"data/levels/{level_name}.yml")
        self.map = Map(self.level.tmx_path)
        tile_x, tile_y = self.map.get_start_tile()
        self.player = Character(position=(0.5 + tile_x, 0.5 + tile_y))
        self.space.add(self.player.body, self.player.poly)
        self.map.add_map_geometry_to_space(self.space)

    def update(self, dt: float, player_movement_direction: Direction):
        self.player.input_direction = player_movement_direction
        self.player.update(dt)
        self.space.step(dt)
