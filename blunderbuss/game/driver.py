from blunderbuss.game.level import Level
from blunderbuss.game.models import Entity

class Driver:
    def __init__(self):
        self.level = Level()
        self.player = Entity()
        self.enemies = [Entity()]