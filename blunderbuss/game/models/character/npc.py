from blunderbuss.game.models.character import Character
from blunderbuss.game.models.direction import Direction
from blunderbuss.game.world_callback import WorldCallback


class NPC(Character):
    def ai(self, dt: float, player: Character, world_callback: WorldCallback):
        if not self.alive:
            return
        self.movement_direction = None
        if not player.alive:
            return
        player_dst_sqrd = self.position.get_dist_sqrd(player.position)
        if player_dst_sqrd < self.chase_distance**2:
            self.movement_direction = Direction.direction_to(
                self.position, player.position
            )
        if player_dst_sqrd < self.attack_distance**2 and not self.attacking:
            self.attack()
            world_callback.ai_attack_callback(self)
