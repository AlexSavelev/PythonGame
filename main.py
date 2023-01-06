import sys
import pygame

from loader import *
from ui import *
from objects import *


class Main:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_NAME)
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()

        self.static_tiles = {i: j for i, j in enumerate(split_on_tiles(
            load_texture('GP_Tiles.png', '#b3afbb'), TILE_WIDTH, TILE_HEIGHT))}

        self.groups = Groups()
        self.player = None

    def terminate(self):
        self.player = None  # TODO: Save
        pygame.quit()
        sys.exit()

    def start_screen(self):
        background = pygame.transform.scale(load_texture('CPO_BG.png'), (WIDTH, HEIGHT))
        self.screen.blit(background, (0, 0))

        title = Text(None, 70, GAME_NAME, COLOR_ORANGE, (0, 0))
        title.move(((WIDTH - title.get_wh()[0]) // 2, 50))
        title.draw(self.screen)

        # Updater
        update_text = Text(None, 40, 'Обновление игры...', COLOR_YELLOW, (0, 0))
        update_text.move(((WIDTH - update_text.get_wh()[0]) // 2, 250))
        update_text.draw(self.screen)

        loading_pb = load_texture('LoadingPB.png')
        loading_pb_rect = loading_pb.get_rect()
        loading_pb_rect.x, loading_pb_rect.y = 340, 300
        self.screen.blit(loading_pb, loading_pb_rect)

        loading_p = load_texture('LoadingP.png')
        # loading_p_rect = loading_p.get_rect()
        # loading_p_rect.x, loading_p_rect.y = 340, 300
        # screen.blit(loading_p, loading_p_rect)

        updater = update_game()
        for i in updater:
            self.screen.fill((0, 0, 0))
            self.screen.blit(background, (0, 0))
            title.draw(self.screen)

            if i < 0.0:
                update_text.set_text('Сетевая ошибка. Игра будет запущена без обновлений')
                update_text.move(((WIDTH - update_text.get_wh()[0]) // 2, 250))
            elif i <= 100.0:
                update_text.set_text(f'Обновление игры... ({i}%)')
                update_text.move(((WIDTH - update_text.get_wh()[0]) // 2, 250))

                loading_ps = pygame.transform.scale(loading_p, (600 * i // 100, 50))
                loading_ps_rect = loading_p.get_rect()
                loading_ps_rect.x, loading_ps_rect.y = 340, 300
                self.screen.blit(loading_ps, loading_ps_rect)
                self.screen.blit(loading_pb, loading_pb_rect)

            update_text.draw(self.screen)
            pygame.display.flip()
            if i < 0.0:
                sleep(5)
                break

        self.screen.fill((0, 0, 0))
        self.screen.blit(background, (0, 0))
        title.draw(self.screen)

        rules_font = pygame.font.Font(None, 30)
        text_coord = 100
        for line in GAME_RULES:
            string_rendered = rules_font.render(line, True, COLOR_YELLOW)
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

        play_btn = Button(Text(None, 60, 'Старт', COLOR_BLUE, (0, 0)), COLOR_YELLOW,
                          rect=pygame.Rect(WIDTH // 2 - 100, 350, 200, 100))
        play_btn.draw(self.screen)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_btn.get_collide_rect().collidepoint(event.pos) \
                            and pygame.mouse.get_pressed()[0] == 1:
                        return
            pygame.display.flip()
            self.clock.tick(FPS)

    def make_level(self, level):
        for y, row in enumerate(level):
            for x, item in enumerate(row):
                if item < 0:
                    continue
                Tile(self.groups, self.static_tiles[item], x, y)

    def run(self):
        self.start_screen()

        self.make_level(load_map('mapT.csv'))

        player = Player(self.groups, 5, 50)
        camera = Camera()

        running = True
        while running:
            self.screen.fill('white')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        player.update(0, -1)
                    elif event.key == pygame.K_s:
                        player.update(0, 1)
                    elif event.key == pygame.K_a:
                        player.update(-1, 0)
                    elif event.key == pygame.K_d:
                        player.update(1, 0)

            camera.update(player)
            for sprite in self.groups.all_sprites:
                camera.apply(sprite)

            self.groups.all_sprites.draw(self.screen)

            self.clock.tick(FPS)
            pygame.display.flip()
        pygame.quit()


if __name__ == '__main__':
    main = Main()
    main.run()
