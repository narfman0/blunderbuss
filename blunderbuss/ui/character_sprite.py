import pygame
import yaml

from blunderbuss.game.models.direction import Direction


class CharacterSprite(pygame.sprite.Sprite):
    SUBFRAMES_PER_FRAME = 5

    def __init__(self, sprite_name, scale: float = 1, offset=(0, 0)):
        super(CharacterSprite, self).__init__()
        self.sprite_name = sprite_name
        self.offset = offset
        self.active_animation_name = "idle"
        self.active_direction = Direction.S

        with open(f"data/characters/{sprite_name}/animations.yml") as f:
            animations_yml = yaml.safe_load(f)

        path_to_nonflipped_image: dict[str, pygame.Surface] = {}
        path_to_flipped_image: dict[str, pygame.Surface] = {}
        self.images: dict[dict[list[pygame.Surface]]] = {}
        for animation_name, direction_list_path_map in animations_yml.items():
            self.images[animation_name] = {}
            for direction_str, animation_struct in direction_list_path_map.items():
                direction = Direction[direction_str]
                animation_direction_images = []
                for image_path in animation_struct["images"]:
                    path = f"data/characters/{sprite_name}/images/{image_path}"
                    flipped = animation_struct.get("flipped")
                    if flipped:
                        path_image_map = path_to_flipped_image
                    else:
                        path_image_map = path_to_nonflipped_image
                    if path in path_image_map:
                        image = path_image_map[path]
                    else:
                        image = pygame.image.load(path).convert_alpha()
                        if scale != 1:
                            width, height = image.get_size()
                            image = pygame.transform.scale(
                                image, (int(width * scale), int(height * scale))
                            )
                        if flipped:
                            image = pygame.transform.flip(
                                image, flip_x=True, flip_y=False
                            )
                        path_image_map[path] = image
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
        if self.subframe == CharacterSprite.SUBFRAMES_PER_FRAME:
            self.index += 1
            self.subframe = 0
        else:
            self.subframe += 1

        if self.index >= len(self.active_images):
            self.index = 0

        self.image = self.active_images[self.index]

    def set_position(self, x, y):
        self.rect.left = x + self.offset[0]
        self.rect.top = y + self.offset[1]

    @property
    def active_images(self) -> list[pygame.Surface]:
        return self.images[self.active_animation_name][self.active_direction]
