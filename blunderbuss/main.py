import logging
import time

import pygame

from blunderbuss.util.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


def main():
    screen = pygame.display.set_mode([500, 500])
    initialize_logging()
    running = True

    while running:
        # Did the user click the window close button?

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background with white

        screen.fill((255, 255, 255))

        # Draw a solid blue circle in the center

        pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

        # Flip the display

        pygame.display.flip()

    # Done! Time to quit.

    pygame.quit()


if __name__ == "__main__":
    main()
