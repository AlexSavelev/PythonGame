import pygame

from config import *
from loader import *


class Groups:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()

        self.static_group = pygame.sprite.Group()
        self.dynamic_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, groups: Groups, tile_image, pos_x, pos_y):
        super().__init__(groups.static_group, groups.all_sprites)
        self.image = tile_image
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, groups: Groups, pos_x, pos_y):
        super().__init__(groups.player_group, groups.all_sprites)
        self.image = load_texture('mario.png')
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x + 15, TILE_HEIGHT * pos_y + 5)

    def update(self, *args):
        self.rect.x += TILE_WIDTH * args[0]
        self.rect.y += TILE_HEIGHT * args[1]
        """
        if pygame.sprite.spritecollideany(self, tiles_group).type != 'empty':
            self.rect.x -= tile_width * args[0]
            self.rect.y -= tile_height * args[1]
        """


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


