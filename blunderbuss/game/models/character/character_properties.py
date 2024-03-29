from dataclasses import dataclass
from dataclass_wizard import YAMLWizard

from blunderbuss.game.models.attack_type import AttackType


@dataclass
class CharacterProperties(YAMLWizard):
    mass: float = 10
    dash_cooldown: float = None
    dash_duration: float = None
    dash_scalar: float = None
    run_force: float = 1000
    running_stop_threshold: float = 1.0
    max_velocity: float = 1
    radius: float = 0.5
    attack_duration: float = None
    attack_distance: float = None
    attack_time_until_damage: float = None
    attack_type: AttackType = AttackType.MELEE
    attack_profile_name: str = None
    hp_max: int = 1
    chase_distance: float = 15
