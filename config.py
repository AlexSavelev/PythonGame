GAME_NAME = 'PythonGame'
GAME_RULES = ['Правила игры', '',
              'Для перемещения используйте клавиши A и D,',
              'для прыжка нажмите на W или пробел.',
              'Собирайте карты, деньги, открывайте сундуки.',
              'Приятной игры!']

FPS = 60
SIZE = WIDTH, HEIGHT = 1280, 720

VERSION_LIST_FNAME = 'version_list.json'
CURRENT_VERSION_FNAME = 'version.txt'

SAVE_GAME_FNAME = 'save.dat'

YADISK_API_KEY = 'y0_AgAAAABnoxidAAj4PQAAAADYyd99SHCLDBo9QXqVuNT-xsflAREnhos'
YADISK_GAME_PATH = 'Game/'
YADISK_LOADER_INTERVAL_SLEEP = 0.1

COLOR_MINT = '#10A19D'
COLOR_BLUE = '#540375'
COLOR_ORANGE = '#FF7000'
COLOR_YELLOW = '#FFBF00'

TILE_WIDTH = TILE_HEIGHT = 32

PLAYER_V_X = 10
PLAYER_V_Y = 18
PLAYER_CLIMB_V_Y = 10
G = 30


SOUND_CHANNEL_DELTAS = 70


def generate_object_name(obj, parent, index=0):
    return f'{obj.__class__.__name__}_{id(parent)}_{index}'
