import pygame
import yaml

from blunderbuss.game.models import Direction


class CharacterSprite(pygame.sprite.Sprite):
    SUBFRAMES_PER_FRAME = 1

    def __init__(self, sprite_name, scale=1, offset=(0, 0)):
        super(CharacterSprite, self).__init__()
        self.sprite_name = sprite_name
        self.offset = offset
        self.active_animation_name = "idle"
        self.active_direction = Direction.S

        with open(f"data/images/characters/{sprite_name}/animations.yml") as f:
            animations_yml = yaml.safe_load(f)

        self.images: dict[dict[list[pygame.Surface]]] = {}
        for animation_name, direction_list_path_map in animations_yml.items():
            self.images[animation_name] = {}
            for direction_str, animation_list_path in direction_list_path_map.items():
                direction = Direction[direction_str]
                animation_direction_images = []
                for image_path in animation_list_path:
                    path = f"data/images/characters/{sprite_name}/{image_path}"
                    image = pygame.image.load(path).convert_alpha()
                    if scale != 1:
                        width, height = image.get_size()
                        image = pygame.transform.scale(
                            image, (int(width * scale), int(height * scale))
                        )
                    animation_direction_images.append(image)
                self.images[animation_name][direction] = animation_direction_images

        self.index = 0
        self.moving = False
        self.subframe = 0

        self.image = self.active_images[self.index]
        width, height = self.image.get_size()
        self.rect = pygame.Rect(0, 0, width, height)

    def move(self, direction):
        self.moving = True
        self.active_direction = direction
        self.index = 0

    def stop(self):
        self.moving = False
        self.index = 0

    def update(self):
        if self.moving:
            if self.subframe == CharacterSprite.SUBFRAMES_PER_FRAME:
                self.index += 1
                self.subframe = 0
            else:
                self.subframe += 1

        if self.index >= len(self.active_images):
            self.index = 0

        self.image = self.active_images[self.index]

    def set_position(self, x, y):
        width, height = self.image.get_size()
        self.rect.left = x + self.offset[0] - width // 2
        self.rect.top = y + self.offset[1] - height // 2

    @property
    def active_images(self):
        return self.images[self.active_animation_name][self.active_direction]
