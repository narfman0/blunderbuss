import pymunk

from blunderbuss.game.models.level import Level
from blunderbuss.game.map import Map
from blunderbuss.game.models.character import Character, NPC, Player
from blunderbuss.game.models.direction import Direction
from blunderbuss.game.world_callback import WorldCallback


class World:
    def __init__(self, level_name="1"):
        self.space = pymunk.Space()
        self.level = Level.from_yaml_file(f"data/levels/{level_name}.yml")
        self.map = Map(self.level.tmx_path)
        self.map.add_map_geometry_to_space(self.space)

        # initialize player
        tile_x, tile_y = self.map.get_start_tile()
        self.player = Player(
            position=(0.5 + tile_x, 0.5 + tile_y), character_type="samurai"
        )
        self.space.add(self.player.body, self.player.poly)

        # initialize enemies
        self.enemies: list[NPC] = []
        for level_enemy in self.level.enemies:
            enemy = NPC(
                position=(0.5 + level_enemy.x, 0.5 + level_enemy.y),
                character_type=level_enemy.character_type,
            )
            self.enemies.append(enemy)
            self.space.add(enemy.body, enemy.poly)

    def update(
        self,
        dt: float,
        player_movement_direction: Direction,
        world_callback: WorldCallback,
    ):
        self.player.movement_direction = player_movement_direction
        self.player.update(dt)
        if self.player.should_process_attack_damage:
            self.process_attack_damage(self.player, self.enemies)
        for enemy in self.enemies:
            enemy.ai(dt, self.player, world_callback)
            enemy.update(dt)
            if enemy.should_process_attack_damage:
                self.process_attack_damage(enemy, [self.player])
        self.space.step(dt)

    def process_attack_damage(self, attacker: Character, enemies: list[Character]):
        attacker.should_process_attack_damage = False
        for enemy in enemies:
            if (
                attacker.position.get_distance(enemy.position)
                - attacker.radius
                - enemy.radius
                < attacker.attack_distance
            ):
                enemy.hp -= 1
                print(f"Attack successful, enemy has {enemy.hp} hp")
