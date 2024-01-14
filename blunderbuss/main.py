import logging
import time

import pygame

from blunderbuss.map import Map
from blunderbuss.models import Entity
from blunderbuss.settings import *
from blunderbuss.util.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


def main():
    pygame.init()
    pygame.display.set_caption("blunderbuss")
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
    display = pygame.Surface((WIDTH // SURFACE_SCALAR, HEIGHT // SURFACE_SCALAR))
    initialize_logging()
    running = True
    gamemap = Map()
    player = Entity()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        player.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * SPEED
        player.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * SPEED

        display.fill((0, 0, 0))
        gamemap.draw(display, screen, player)
        pygame.display.update()
        time.sleep(FRAMERATE)

    pygame.quit()


if __name__ == "__main__":
    main()
