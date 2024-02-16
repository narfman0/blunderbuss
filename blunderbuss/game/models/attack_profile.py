from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class AttackProfile(YAMLWizard):
    name: str
    image_path: str
    speed: float
    radius: float
