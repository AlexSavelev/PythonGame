from loader import *
from ui import *


class Groups:
    def __init__(self, main_instance):
        self.main_instance = main_instance
        self.player = None

        self.all_sprites = pygame.sprite.Group()

        self.object_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

        self.updatable_group = pygame.sprite.Group()

        self.collectable_group = pygame.sprite.Group()
        self.interactive_group = pygame.sprite.Group()


class Object(pygame.sprite.Sprite):
    def __init__(self, groups: Groups, image, rel_pos, has_collision):
        super().__init__(groups.object_group, groups.all_sprites)
        self.image = image

        abs_pos_x, abs_pos_y = \
            rel_pos[0] * TILE_WIDTH + TILE_WIDTH // 2 - self.image.get_rect().width // 2, \
            (rel_pos[1] + 1) * TILE_HEIGHT - self.image.get_rect().height
        self.rect = self.image.get_rect().move(abs_pos_x, abs_pos_y)
        self.has_collision = has_collision


class Tile(Object):
    def __init__(self, groups: Groups, image, rel_pos):
        super().__init__(groups, image, rel_pos, True)


class UpdatableObject(Object):
    def __init__(self, groups: Groups, image, rel_pos):
        super().__init__(groups, image, rel_pos, False)
        groups.updatable_group.add(self)
        self.groups = groups
        self.type = 'Object'

    def update(self, *args):
        pass


class CollectableAnimatedObject(UpdatableObject):
    def __init__(self, groups: Groups, image, rel_pos, update_time=0.2):
        self.frame_index = 0
        self.frames = split_on_tiles(image, image.get_height(), image.get_height())

        super().__init__(groups, self.frames[self.frame_index], rel_pos)
        groups.updatable_group.add(self)
        groups.collectable_group.add(self)

        self.update_time = update_time
        self.time_passed = 0.0

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, self.groups.player_group):
            self.on_collect()
            self.kill()

        self.time_passed += 1 / FPS
        if self.time_passed >= self.update_time:
            self.time_passed %= self.update_time
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def on_collect(self):
        pass


class InteractiveObject(UpdatableObject):
    def __init__(self, groups: Groups, image, rel_pos, interact_once=False,
                 pre_interact_message='?????????????????????????????????? (E)', key=pygame.K_e):
        super().__init__(groups, image, rel_pos)
        groups.updatable_group.add(self)
        groups.interactive_group.add(self)
        self.key = key
        self.is_allow_interact = False
        self.is_key_pressed = False

        self.can_be_interacted = 1 if interact_once else 10000000

        self.text_box = TextBox(
            Text(None, 30, pre_interact_message, COLOR_ORANGE, (0, 0)),
            COLOR_YELLOW, WIDTH // 2, 600)
        self.text_box_name = generate_object_name(self.text_box, self)

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, self.groups.player_group) \
                and self.can_be_interacted != 0:
            self.is_allow_interact = True
            self.text_box.add_to_draw_queue(self.text_box_name)
        elif self.is_allow_interact:
            self.is_allow_interact = False
            self.text_box.remove_from_draw_queue()

        if pygame.key.get_pressed()[self.key] == 1 and \
                not self.is_key_pressed and \
                self.is_allow_interact and self.groups.player.enable_moving:
            self.is_key_pressed = True
            self.on_interact()
            self.can_be_interacted -= 1
        elif self.is_key_pressed and pygame.key.get_pressed()[self.key] == 0:
            self.is_key_pressed = False

    def on_interact(self):
        pass


class Ladder(InteractiveObject):
    def __init__(self, groups: Groups, image, rel_pos):
        super().__init__(groups, image, rel_pos, False, '?????????????????? (E)', pygame.K_e)
        self.type = 'Ladder'

    def on_interact(self):
        self.groups.player.enable_moving = False
        self.groups.player.is_climbs_ladder = True
        self.groups.player.rect.left = \
            self.rect.left + self.rect.width // 2 - self.groups.player.rect.width // 2


class Fountain(UpdatableObject):
    def __init__(self, groups: Groups, image, rel_pos, is_turned_on: bool, key: str):
        t = split_on_tiles(image, image.get_height(), image.get_height())
        self.off_image = t[0]
        self.on_frames = t[1:]
        self.on_frame_index = 0

        self.turned_on = is_turned_on

        self.key_to_update_state = groups.main_instance.cdata[key]['enable_condition']
        self.new_map_name = groups.main_instance.cdata[key]['teleport_map_name']

        self.sound = None

        super().__init__(groups,
                         self.on_frames[self.on_frame_index] if self.turned_on else self.off_image,
                         rel_pos)

        self.update_time = 0.1
        self.time_passed = 0.0

    def kill(self):
        if self.sound is not None:
            self.sound.stop()
            self.sound = None
        super().kill()

    def update(self, *args):
        if not self.turned_on and self.sound is not None:
            self.sound.stop()
            self.sound = None

        if self.key_to_update_state in self.groups.main_instance.gp_var:
            if self.groups.main_instance.gp_var[self.key_to_update_state]:
                if not self.turned_on:
                    self.turned_on = True
                    self.on_frame_index = 0
                    self.image = self.on_frames[self.on_frame_index]
            else:
                if self.turned_on:
                    self.turned_on = False
                    self.image = self.off_image

        if not self.turned_on:
            return

        self.time_passed += 1 / FPS
        if self.time_passed >= self.update_time:
            self.time_passed %= self.update_time
            self.on_frame_index = (self.on_frame_index + 1) % len(self.on_frames)
            self.image = self.on_frames[self.on_frame_index]

        if self.sound is None:
            self.sound = load_sound('fountain_sfx').play(loops=-1)

        def get_vxy_magnitude():
            return ((self.rect.x - WIDTH // 2) ** 2 + (self.rect.y - HEIGHT // 2) ** 2) ** 0.5

        magnitude = get_vxy_magnitude()
        new_volume = min((magnitude / SOUND_CHANNEL_DELTAS) ** -1, 1.0)
        self.sound.set_volume(new_volume)

        if magnitude <= 60.0:
            self.groups.main_instance.load_new_map(self.new_map_name)


class Chest(InteractiveObject):
    def __init__(self, groups: Groups, image, rel_pos, key: str):
        self.frame_index = 0
        self.frames = split_on_tiles_with_intervals(image, 30, image.get_height(), 2)

        super().__init__(groups, self.frames[self.frame_index], rel_pos,
                         True, '?????????????? (E)', pygame.K_e)

        self.i_key = key

        self.is_playing = False
        self.update_time = 0.3
        self.time_passed = 0.0

    def on_interact(self):
        cond_key = self.groups.main_instance.cdata[self.i_key]['open_condition']
        if cond_key in self.groups.main_instance.gp_var and \
                self.groups.main_instance.gp_var[cond_key]:
            self.is_playing = True
        else:
            self.can_be_interacted += 1

    def update(self, *args):
        super().update(*args)

        if not self.is_playing:
            return

        self.time_passed += 1 / FPS
        if self.time_passed >= self.update_time:
            self.time_passed %= self.update_time
            self.frame_index += 1
            self.image = self.frames[self.frame_index]
        if self.frame_index == len(self.frames) - 1:
            self.is_playing = False
            self.groups.main_instance.interact_chest(self.i_key)


class Bench(InteractiveObject):
    def __init__(self, groups: Groups, image, rel_pos):
        super().__init__(groups, image, rel_pos,
                         False, '?????????????????? ???????? (F5)', pygame.K_F5)
        self.abs_pos = \
            rel_pos[0] * TILE_WIDTH + TILE_WIDTH // 2 - self.image.get_rect().width // 2, \
            (rel_pos[1] + 1) * TILE_HEIGHT - self.image.get_rect().height

    def on_interact(self):
        self.groups.main_instance.save_game(self.abs_pos)


class Money(CollectableAnimatedObject):
    def __init__(self, groups: Groups, image, rel_pos, key):
        super().__init__(groups, image, rel_pos, 0.2)
        self.key = key

    def on_collect(self):
        self.groups.main_instance.collect_money(self.key)


class Card(CollectableAnimatedObject):
    def __init__(self, groups: Groups, image, rel_pos, key):
        super().__init__(groups, image, rel_pos, 0.2)
        self.key = key

    def on_collect(self):
        self.groups.main_instance.collect_card(self.key)


class Skateboard(CollectableAnimatedObject):
    def __init__(self, groups: Groups, image, rel_pos, key):
        super().__init__(groups, image, rel_pos, 0.2)
        self.key = key

    def on_collect(self):
        self.groups.main_instance.collect_skateboard(self.key)


class Player(pygame.sprite.Sprite):
    def __init__(self, groups: Groups, abs_pos_x, abs_pos_y):
        super().__init__(groups.player_group, groups.all_sprites)

        self.groups = groups
        t = load_texture('mario.png')
        self.image_set = {'R': pygame.transform.flip(t, True, False), 'L': t}

        self.image_state = 'R'
        self.image = self.image_set[self.image_state]

        self.rect = self.image.get_rect().move(abs_pos_x, abs_pos_y)
        self.groups.player = self

        self.enable_moving = True
        self.is_climbs_ladder = False

        self.fly_time = 0.0
        self.v_y = 0.0

    def _move_x(self, dx):
        dx = int(TILE_WIDTH * dx)

        if dx > 0 and self.image_state != 'R':
            self.image_state = 'R'
            self.image = self.image_set[self.image_state]
        elif dx < 0 and self.image_state != 'L':
            self.image_state = 'L'
            self.image = self.image_set[self.image_state]

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
        self.fly_time += delta_time

        self.v_y = self.v_y + G * delta_time
        s = self.v_y * delta_time

        if self.v_y >= 60:
            self.groups.main_instance.load_last_save()

        dy = int(s * TILE_HEIGHT)
        self.rect.y += dy
        if self._check_collisions():
            self.rect.y -= dy
            self.fly_time = 0.0
            self.v_y = 0.0

    def _climb_ladder(self):
        dy = TILE_HEIGHT * PLAYER_CLIMB_V_Y / FPS
        self.rect.y -= dy
        if self._check_ladder_collisions():
            return

        while not self._check_ladder_collisions():
            self.rect.y += 1
        self.rect.y -= 1

        self.rect.x += TILE_WIDTH
        self.rect.y += 1
        if not self._check_collisions():
            self.rect.x -= 2 * TILE_WIDTH
        self.rect.y -= 1

        self.is_climbs_ladder = False
        self.enable_moving = True

    def _check_ladder_collisions(self):
        t = pygame.sprite.spritecollide(self, self.groups.object_group, False)
        if t and any([i.type == 'Ladder' for i in t]):
            return True
        return False

    def _check_collisions(self):
        t = pygame.sprite.spritecollide(self, self.groups.object_group, False)
        if t and any([i.has_collision for i in t]):
            return True
        return False

    def update(self, *args):
        if self.is_climbs_ladder:
            self._climb_ladder()

        keys = pygame.key.get_pressed()
        delta_x = PLAYER_V_X / FPS

        if not self.enable_moving:
            return

        dx, dy = 0.0, 0.0
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.fly_time == 0.0:
            self.v_y = -PLAYER_V_Y
        if keys[pygame.K_a]:
            dx -= delta_x
        if keys[pygame.K_d]:
            dx += delta_x

        self._move_x(dx)
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
