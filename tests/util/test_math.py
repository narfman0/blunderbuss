import unittest
from blunderbuss.util import math


class TestMath(unittest.TestCase):
    def test_point_in_polygon_middle(self):
        vertx = [0, 10, 10, 0]
        verty = [0, 0, 10, 10]
        self.assertEqual(True, math.point_in_polygon(vertx, verty, 5, 5))

    def test_point_in_polygon_outside(self):
        vertx = [0, 10, 10, 0]
        verty = [0, 0, 10, 10]
        self.assertEqual(True, math.point_in_polygon(vertx, verty, 150, 150))
