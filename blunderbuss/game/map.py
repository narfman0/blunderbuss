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
        return map(int, self.tmxdata.properties.get("StartTile").split(","))

    def get_tile_type(self, tile_x, tile_y, layer):
        tile_props = self.tmxdata.get_tile_properties(tile_x, tile_y, layer) or {}
        return tile_props.get("type")

    def get_transition_details(self, tile_x, tile_y):
        object = self.tmxdata.get_object_by_name(f"transition,{tile_x},{tile_y}")
        destination_area = object.properties["Destination"]
        dest_x, dest_y = map(int, object.properties["DestinationXY"].split(","))
        return TransitionDetails(destination_area, dest_x, dest_y)

    def has_colliders(self, tile_x, tile_y, layer):
        tile_props = self.tmxdata.get_tile_properties(tile_x, tile_y, layer) or {}
        return tile_props.get("colliders")

    def get_tile_image(self, tile_x, tile_y, layer):
        return self.tmxdata.get_tile_image(tile_x, tile_y, layer)

    def get_tile_layer_count(self):
        return len(list(self.tmxdata.visible_tile_layers))

    @property
    def width(self):
        return self.tmxdata.width

    @property
    def height(self):
        return self.tmxdata.height
