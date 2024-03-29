import logging
from pstats import SortKey
import pygame

from blunderbuss.game.world import World
from blunderbuss.settings import *
from blunderbuss.ui.screen import ScreenManager
from blunderbuss.ui.level.level_screen import LevelScreen
from blunderbuss.util.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


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

    if ENABLE_PROFILING:
        import cProfile, pstats, io

        pr = cProfile.Profile()
        pr.enable()
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False
            else:
                events.append(event)

        screen_manager.current.update(dt, events)
        surface.fill((0, 0, 0))
        screen_manager.current.draw(surface)
        pygame.display.update()

    if ENABLE_PROFILING:
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        with open("pstats.log", "w+") as f:
            f.write(s.getvalue())
    pygame.quit()


if __name__ == "__main__":
    main()
