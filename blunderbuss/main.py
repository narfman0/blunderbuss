import logging
import time

import pygame

from blunderbuss.game.world import World
from blunderbuss.game.models import Direction
from blunderbuss.ui.screen import ScreenManager
from blunderbuss.ui.level_screen import LevelScreen
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
    initialize_logging()
    pygame.init()
    pygame.display.set_caption("blunderbuss")
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    clock = pygame.time.Clock()

    world = World()
    screen_manager = ScreenManager()
    screen_manager.push(LevelScreen(screen_manager, world))

    while running:
        dt = clock.tick(60) / 1000.0
        key_events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                key_events.append(event)

        screen_manager.current.update(dt, key_events)
        surface.fill((0, 0, 0))
        screen_manager.current.draw(surface)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
