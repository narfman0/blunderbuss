import pymunk

from blunderbuss.game.models.level import Level
from blunderbuss.game.models.projectile import Projectile
from blunderbuss.game.map import Map
from blunderbuss.game.models.attack_type import AttackType
from blunderbuss.game.models.character import Character, NPC, Player
from blunderbuss.game.models.direction import Direction
from blunderbuss.game.world_callback import WorldCallback

PROJECTILE_SPEED = 2.0


class World:
    def __init__(self, level_name="1"):
        self.projectiles: list[Projectile] = []
        self.space = pymunk.Space()
        self.level = Level.from_yaml_file(f"data/levels/{level_name}.yml")
        self.map = Map(self.level.tmx_path)
        self.map.add_map_geometry_to_space(self.space)

        # initialize player
        tile_x, tile_y = self.map.get_start_tile()
        self.player = Player(
            position=(0.5 + tile_x, 0.5 + tile_y), character_type="pigsassin"
        )
        self.space.add(self.player.body, self.player.shape, self.player.hitbox_shape)

        # initialize enemies
        self.enemies: list[NPC] = []
        for level_enemy in self.level.enemies:
            enemy = NPC(
                position=(0.5 + level_enemy.x, 0.5 + level_enemy.y),
                character_type=level_enemy.character_type,
            )
            self.enemies.append(enemy)
            self.space.add(enemy.body, enemy.shape, enemy.hitbox_shape)

    def update(
        self,
        dt: float,
        player_movement_direction: Direction,
        world_callback: WorldCallback,
    ):
        self.player.movement_direction = player_movement_direction
        self.player.update(dt)
        if self.player.should_process_attack:
            self.process_attack_damage(self.player, self.enemies)
        for enemy in self.enemies:
            enemy.ai(dt, self.player, world_callback)
            enemy.update(dt)
            if not enemy.alive and not enemy.body_removal_processed:
                enemy.body_removal_processed = True
                self.space.remove(enemy.body, enemy.shape, enemy.hitbox_shape)
            if enemy.should_process_attack:
                if enemy.attack_type == AttackType.MELEE:
                    self.process_attack_damage(enemy, [self.player])
                elif enemy.attack_type == AttackType.RANGED:
                    velocity = enemy.facing_direction.to_vector().scale_to_length(
                        PROJECTILE_SPEED
                    )
                    projectile = Projectile(
                        x=enemy.position.x,
                        y=enemy.position.y,
                        dx=velocity.x,
                        dy=velocity.y,
                        origin=enemy,
                        attack_profile_name=enemy.attack_profile_name,
                    )
                    self.projectiles.append(projectile)
                    enemy.should_process_attack = False
        self.update_projectiles(dt)
        self.space.step(dt)

    def update_projectiles(self, dt: float):
        for projectile in self.projectiles:
            projectile.update(dt)
            should_remove = False
            for query_info in self.space.shape_query(projectile.shape):
                if hasattr(query_info.shape.body, "character"):
                    character = query_info.shape.body.character
                    # let's avoid friendly fire. eventually it'd be cool to have factions.
                    player_involved = (
                        projectile.origin == self.player or character == self.player
                    )
                    if player_involved and projectile.origin != character:
                        character.handle_damage_received(1)
                        should_remove = True
                else:
                    should_remove = True
            if should_remove:
                self.projectiles.remove(projectile)

    def process_attack_damage(self, attacker: Character, enemies: list[Character]):
        attacker.should_process_attack = False
        for enemy in enemies:
            if attacker.hitbox_shape.shapes_collide(enemy.shape).points:
                enemy.handle_damage_received(1)
