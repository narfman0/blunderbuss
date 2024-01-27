from dataclasses import dataclass, field
from enum import Enum

from pygame import Vector2
import pymunk

NPC_MASS = 10


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


@dataclass
class Character:
    direction: Direction = Direction.S
    poly: pymunk.Poly = None
    body: pymunk.Body = None

    def __init__(self, position: tuple[float, float]):
        self.body = pymunk.Body()
        self.body.position = position
        self.poly = pymunk.Circle(self.body, 1)
        self.poly.mass = NPC_MASS

    @property
    def position(self):
        return self.body.position
