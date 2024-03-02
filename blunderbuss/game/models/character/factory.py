from blunderbuss.game.models.character import NPC


def create_character(character_type: str, x: float, y: float):
    character = NPC(
        position=(0.5 + x, 0.5 + y),
        character_type=character_type,
    )
    return character
