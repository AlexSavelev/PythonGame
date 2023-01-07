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

        self.groups = groups
        self.image = load_texture('mario.png')
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x + 5, TILE_HEIGHT * pos_y - 5)

        self.fly_time = 0.0

    def _move_x(self, dx):
        dx = int(TILE_WIDTH * dx)

        self.rect.x += dx
        if self._check_collisions():
            self.rect.x -= dx

    def _move_y(self, dy):
        dy = int(dy * TILE_HEIGHT)

        self.rect.y += dy
        if self._check_collisions():
            self.rect.y -= dy

    def _physics_check(self):
        delta_time = 1 / FPS
        s = G / 2 * delta_time * (2 * self.fly_time + delta_time)
        self.fly_time += delta_time

        dy = int(s * TILE_HEIGHT)
        self.rect.y += dy
        if self._check_collisions():
            self.rect.y -= dy
            self.fly_time = 0.0

    def _check_collisions(self):
        return pygame.sprite.spritecollideany(self, self.groups.static_group) is not None or \
                pygame.sprite.spritecollideany(self, self.groups.dynamic_group) is not None

    def update(self, *args):
        keys = pygame.key.get_pressed()
        delta_x = PLAYER_V_X / FPS
        delta_y = PLAYER_V_Y / FPS

        dx, dy = 0.0, 0.0
        if keys[pygame.K_w]:
            dy -= delta_y
        if keys[pygame.K_s]:
            dy += delta_y
        if keys[pygame.K_a]:
            dx -= delta_x
        if keys[pygame.K_d]:
            dx += delta_x

        self._move_x(dx)
        self._move_y(dy)
        self._physics_check()


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


