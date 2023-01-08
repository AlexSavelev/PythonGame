GAME_NAME = 'RPG'
GAME_RULES = ["Правила игры", "",
              "Если в правилах несколько строк,",
              "приходится выводить их построчно"]

FPS = 60
SIZE = WIDTH, HEIGHT = 1280, 720

VERSION_LIST_FNAME = 'version_list.json'
CURRENT_VERSION_FNAME = 'version.txt'

YADISK_API_KEY = 'y0_AgAAAABnoxidAAj4PQAAAADYyd99SHCLDBo9QXqVuNT-xsflAREnhos'
YADISK_GAME_PATH = 'Game/'
YADISK_LOADER_INTERVAL_SLEEP = 0.1

COLOR_MINT = '#10A19D'
COLOR_BLUE = '#540375'
COLOR_ORANGE = '#FF7000'
COLOR_YELLOW = '#FFBF00'

TILE_WIDTH = TILE_HEIGHT = 32

PLAYER_V_X = 15
PLAYER_V_Y = 11
PLAYER_CLIMB_V_Y = 20
G = 10


def generate_object_name(obj, parent, index=0):
    return f'{obj.__class__.__name__}_{id(parent)}_{index}'
