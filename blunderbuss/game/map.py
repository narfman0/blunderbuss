from dataclasses import dataclass

from pygame.math import Vector2
import pymunk
import pytmx

from blunderbuss.util.math import cartesian_to_isometric

USE_COMPLEX_COLLIDERS = False

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

    def add_map_geometry_to_space(self, space: pymunk.Space):
        for layer in range(self.get_tile_layer_count()):
            for y in range(self.height):
                for x in range(self.width):
                    tile_props = self.tmxdata.get_tile_properties(x, y, layer) or {}
                    colliders: list = tile_props.get("colliders", [])
                    if colliders:
                        for collider in colliders:
                            body = pymunk.Body(body_type=pymunk.Body.STATIC)
                            body.position = (0.5 + x, 0.5 + y)
                            if USE_COMPLEX_COLLIDERS:
                                points = list(self.points_to_world_linked(collider.points))
                                segments = []
                                a = len(points)-1
                                for b in range(len(points)):
                                    apt = points[a]
                                    bpt = points[b]
                                    segments.append(pymunk.Segment(body, (apt.x, apt.y), (bpt.x, bpt.y), 0.01))
                                    a = b
                                space.add(body, *segments)
                            else:
                                poly = pymunk.Poly.create_box(body, size=(1, 1))
                                poly.mass = 10
                                space.add(body, poly)
        return False

    def points_to_world_linked(self, points: list):
        for point in points:
            iso = cartesian_to_isometric(Vector2(point.x, point.y))
            iso.x /= 128
            iso.y /= 128
            yield iso

    @property
    def width(self):
        return self.tmxdata.width

    @property
    def height(self):
        return self.tmxdata.height
