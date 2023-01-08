import sys

from objects import *


class Main:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_NAME)
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()

        self.asset_map = {}
        self.prepare_asset_map()

        self.groups = Groups(self)
        self.player = None

        self.cdata = {}
        self.gp_var = {'true': 1, 'false': 0}
        self.money_balance = 0
        self.chest_opened = 0
        self.skateboards = set()

    def terminate(self):
        self.asset_map.clear()
        pygame.quit()
        sys.exit()

    def prepare_asset_map(self):
        # Tiles 0-95
        self.asset_map = {i: j for i, j in enumerate(split_on_tiles(
            load_texture('GP_Tiles.png', '#b3afbb'), TILE_WIDTH, TILE_HEIGHT))}
        # Dynamic 96-107
        self.asset_map[96] = load_texture('GP_Card.png')
        self.asset_map[97] = load_texture('GP_Chest.png')
        self.asset_map[98] = load_texture('GP_Money.png')
        self.asset_map[99] = load_texture('GP_Skateboard.png')
        self.asset_map[100] = load_texture('GP_Fountain.png', (255, 255, 255))
        self.asset_map[102] = load_texture('GP_Ladder_1.png')
        self.asset_map[103] = load_texture('GP_Ladder_2.png')
        # Bench 108-119
        for i in range(4):
            self.asset_map[2 * i + 108] = load_texture(f'GP_Bench_{i + 1}.png')
        # Bush 120-143a
        for i in range(20):
            self.asset_map[i + 120] = load_texture(f'GP_Bush_{i + 1}.png')
        # Stone 144-148
        for i in range(5):
            self.asset_map[i + 144] = load_texture(f'GP_Stone_{i + 1}.png')
        # Ramp 149-155
        self.asset_map[149] = load_texture('GP_Ramp.png')
        # Box 156-167
        self.asset_map[156] = load_texture('GP_Box.png')
        # Tree 168-179
        for i in range(4):
            self.asset_map[i + 168] = load_texture(f'GP_Tree_{i + 1}.png')
        # End

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

    def save_game(self):
        print('Saved!')  # TODO: SaveGame

    def collect_money(self, key):
        count = self.cdata[key]['count']
        self.money_balance += count
        self.cdata.pop(key)

        print(f'Money balance: {self.money_balance}')

    def collect_card(self, key):
        k, v = self.cdata[key]['gp_var_key'], self.cdata[key]['gp_var_value']
        self.gp_var[k] = v
        self.cdata.pop(key)

    def collect_skateboard(self, key):
        number = self.cdata[key]['number']
        self.skateboards.add(number)
        self.cdata.pop(key)

    def interact_chest(self, key):
        items = self.cdata[key]['items']
        self.chest_opened += 1
        print(f'Chest opened: {self.chest_opened}')  # TODO: Inventory system
        self.cdata.pop(key)

    def make_level(self, level, level_name):
        for y, row in enumerate(level):
            for x, item in enumerate(row):
                if item < 0:
                    continue
                if 0 <= item <= 95:
                    Tile(self.groups, self.asset_map[item], (x, y))
                elif 96 <= item <= 99:
                    obj_name = ['card', 'chest', 'money', 'skateboard'][item - 96]
                    key = f'{level_name}_{obj_name}_{x}_{y}'
                    if key not in self.cdata:
                        continue

                    if item == 96:
                        Card(self.groups, self.asset_map[item], (x, y), key)
                    elif item == 97:
                        Chest(self.groups, self.asset_map[item], (x, y), key)
                    elif item == 98:
                        Money(self.groups, self.asset_map[item], (x, y), key)
                    elif item == 99:
                        Skateboard(self.groups, self.asset_map[item], (x, y), key)
                elif item == 100 or item == 101:  # Pic in 100
                    Fountain(self.groups, self.asset_map[100], (x, y), item == 100, "turnOnFt1")
                elif item == 102 or item == 103:
                    Ladder(self.groups, self.asset_map[item], (x, y))
                elif 108 <= item <= 119:
                    if item not in [108, 110, 112, 114]:
                        continue
                    Bench(self.groups, self.asset_map[item], (x, y))
                elif 120 <= item <= 179 and item != 156:
                    Object(self.groups, self.asset_map[item], (x, y), False)
                elif item == 156:
                    Object(self.groups, self.asset_map[item], (x, y), True)

    def run(self):
        self.start_screen()

        background = pygame.transform.scale(load_texture('S_BG3.png'), SIZE)

        level_name = 'mapT'

        m, cdata = load_map(level_name)
        for i, j in cdata.items():
            self.cdata[i] = j
        self.make_level(m, level_name)

        player = Player(self.groups, 10, 50)
        camera = Camera()

        running = True
        while running:
            self.screen.fill('#FFFFFF')
            self.screen.blit(background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            player.update()

            camera.update(player)
            for sprite in self.groups.all_sprites:
                camera.apply(sprite)

            self.groups.updatable_group.update()

            self.groups.all_sprites.draw(self.screen)

            for i in Widget.CONTAINER.values():
                i.draw(self.screen)

            self.clock.tick(FPS)
            pygame.display.flip()
        pygame.quit()


if __name__ == '__main__':
    main = Main()
    main.run()
