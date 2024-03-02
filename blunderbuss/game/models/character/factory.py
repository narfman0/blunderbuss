from typing import Callable

from blunderbuss.game.models.character import Character

character_create_methods: dict[str, Callable[..., Character]] = {}


def register(character_type: str, create_method: Callable[..., Character]):
    """Register a new game character type."""
    character_create_methods[character_type] = create_method


def unregister(character_type: str):
    """Unregister a game character type."""
    character_create_methods.pop(character_type, None)


def create_character(character_type: str, x: float, y: float) -> Character:
    try:
        create_method = character_create_methods[character_type]
    except KeyError:
        print(f"Unknown character type {character_type}, defaulting to generic npc")
        create_method = character_create_methods["npc"]
    return create_method(
        position=(0.5 + x, 0.5 + y),
        character_type=character_type,
    )
