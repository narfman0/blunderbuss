from pygame.math import Vector2


def cartesian_to_isometric(cartesian: Vector2) -> Vector2:
    return Vector2(cartesian.x - cartesian.y, (cartesian.x + cartesian.y) // 2)


def isometric_to_cartesian(isometric: Vector2) -> Vector2:
    cartesian_x = (isometric.x + isometric.y * 2) // 2
    return Vector2(cartesian_x, cartesian_x + isometric.x)
