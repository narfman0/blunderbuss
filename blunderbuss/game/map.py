from dataclasses import dataclass

import pytmx


@dataclass
class TransitionDetails:
    destination_area: str
    destination_x: int
    destination_y: int


class Map:
    def __init__(self, area: str):
        self.area = area
        self.tmxdata = pytmx.load_pygame(f"data/tiled/{area}.tmx")

    def get_start_tile(self):
        return map(int, self.tmxdata.properties.get("StartXY").split(","))

    def get_tile_image(self, tile_x: int, tile_y: int, layer: int):
        return self.tmxdata.get_tile_image(tile_x, tile_y, layer)

    def get_tile_layer_count(self):
        return len(list(self.tmxdata.visible_tile_layers))
    
    def has_colliders(self, tile_x: int, tile_y: int):
        colliders_present = False
        for layer in range(self.get_tile_layer_count()):
            tile_props = self.tmxdata.get_tile_properties(tile_x, tile_y, layer) or {}
            colliders_present |= "colliders" in tile_props
        return colliders_present

    @property
    def width(self):
        return self.tmxdata.width

    @property
    def height(self):
        return self.tmxdata.height
