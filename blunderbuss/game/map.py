from dataclasses import dataclass

from pygame.math import Vector2
import pytmx

from blunderbuss.util.math import point_in_polygon, cartesian_to_isometric


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

    def collides(self, x: float, y: float):
        for layer in range(self.get_tile_layer_count()):
            tile_props = self.tmxdata.get_tile_properties(int(x), int(y), layer) or {}
            colliders: list = tile_props.get("colliders")
            if colliders:
                return True
                # TODO phase 2 collisions
                # for collider in colliders:
                #     vert_x, vert_y = self.points_to_vertxy(collider.points)
                #     # need to convert world coordinates to tile coordinates or vice versa
                #     test_x = (x - int(x)) * self.tmxdata.tilewidth
                #     test_y = (y - int(y)) * self.tmxdata.tileheight
                #     test_xy = cartesian_to_isometric(Vector2(test_x, test_y))
                #     if point_in_polygon(vert_x, vert_y, test_xy.x, test_xy.y):
                #         return True
        return False

    @classmethod
    def points_to_vertxy(cls, points: list) -> tuple[list[float], list[float]]:
        vertx = []
        verty = []
        for point in points:
            vertx.append(point.x)
            verty.append(point.y)
        return vertx, verty

    @property
    def width(self):
        return self.tmxdata.width

    @property
    def height(self):
        return self.tmxdata.height
