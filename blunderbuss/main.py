import logging
import time

import pygame

from blunderbuss.game.driver import Driver
from blunderbuss.game.models import Direction
from blunderbuss.ui.level import LevelUI
from blunderbuss.settings import *
from blunderbuss.util.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


def read_player_direction():
    keys = pygame.key.get_pressed()
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    up = keys[pygame.K_UP] or keys[pygame.K_w]
    down = keys[pygame.K_DOWN] or keys[pygame.K_s]
    direction = None
    if down:
        if right:
            direction = Direction.SE
        elif left:
            direction = Direction.SW
        else:
            direction = Direction.S
    elif up:
        if right:
            direction = Direction.NE
        elif left:
            direction = Direction.NW
        else:
            direction = Direction.N
    elif left:
        direction = Direction.W
    elif right:
        direction = Direction.E
    return direction


def main():
    pygame.init()
    pygame.display.set_caption("blunderbuss")
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
    display = pygame.Surface((WIDTH // SURFACE_SCALAR, HEIGHT // SURFACE_SCALAR))
    initialize_logging()
    running = True
    driver = Driver()
    levelui = LevelUI()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        driver.move_player(read_player_direction())

        display.fill((0, 0, 0))
        levelui.draw(display, screen, driver)
        pygame.display.update()
        time.sleep(FRAMERATE)

    pygame.quit()


if __name__ == "__main__":
    main()
