from enum import Enum

from pygame import Vector2


class Direction(Enum):
    N = 1
    NE = 2
    E = 3
    SE = 4
    S = 5
    SW = 6
    W = 7
    NW = 8

    def to_vector(self) -> Vector2:
        # lrucacheable!
        return {
            Direction.N: Vector2(0, -1),
            Direction.NE: Vector2(1, -1),
            Direction.E: Vector2(1, 0),
            Direction.SE: Vector2(1, 1),
            Direction.S: Vector2(0, 1),
            Direction.SW: Vector2(-1, 1),
            Direction.W: Vector2(-1, 0),
            Direction.NW: Vector2(-1, -1),
        }[self].normalize()

    def to_isometric(self):
        return {
            Direction.N: Direction.NE,
            Direction.NE: Direction.E,
            Direction.E: Direction.SE,
            Direction.SE: Direction.S,
            Direction.S: Direction.SW,
            Direction.SW: Direction.W,
            Direction.W: Direction.NW,
            Direction.NW: Direction.N,
        }[self]