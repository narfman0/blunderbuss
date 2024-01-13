import logging
import time

import pygame

from blunderbuss.map import Map
from blunderbuss.util.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


def main():
    pygame.init()
    pygame.display.set_caption('blunderbuss')
    screen = pygame.display.set_mode((900, 900),0,32)
    display = pygame.Surface((300, 300))
    initialize_logging()
    running = True
    gamemap = Map()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        display.fill((0,0,0))
        gamemap.tick(display, screen)
        pygame.display.update()
        time.sleep(1)

    pygame.quit()


if __name__ == "__main__":
    main()
