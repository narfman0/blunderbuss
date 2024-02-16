from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class AttackProfile(YAMLWizard):
    name: str
    image_path: str
    speed: float
    radius: float
    render_emit_offset_x: float = 0
    render_emit_offset_y: float = 0
