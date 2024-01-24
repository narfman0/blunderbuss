from pygame.math import Vector2


def cartesian_to_isometric(cartesian: Vector2) -> Vector2:
    return Vector2(cartesian.x - cartesian.y, (cartesian.x + cartesian.y) // 2)


def isometric_to_cartesian(isometric: Vector2) -> Vector2:
    cartesian_x = (isometric.x + isometric.y * 2) // 2
    return Vector2(cartesian_x, cartesian_x + isometric.x)


def point_in_polygon(
    nvert: int, vertx: list[float], verty: list[float], testx: float, testy: float
):
    """Adapted from https://wrfranklin.org/Research/Short_Notes/pnpoly.html"""
    c = 0
    j = nvert - 1
    for i in range(nvert):
        if ((verty[i] > testy) != (verty[j] > testy)) and (
            testx
            < (vertx[j] - vertx[i]) * (testy - verty[i]) / (verty[j] - verty[i])
            + vertx[i]
        ):
            c = not c
        j = i
    return c
