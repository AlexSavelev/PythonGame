import os
import pygame
import requests.exceptions
import yadisk
import json
import csv
from time import sleep

from config import *


def split_on_tiles(image, tile_w, tile_h):
    cols, rows = image.get_width() // tile_w, image.get_height() // tile_h
    return [image.subsurface(pygame.Rect((tile_w * j, tile_h * i), (tile_w, tile_h)))
            for i in range(rows) for j in range(cols)]


def split_on_tiles_with_intervals(image, tile_w, tile_h, interval):
    cols, rows = image.get_width() // (tile_w + interval), image.get_height() // (tile_h + interval)
    cols = cols + 1 if (cols + 1) * tile_w + cols * interval >= image.get_width() else cols
    rows = rows + 1 if (rows + 1) * tile_h + rows * interval >= image.get_height() else rows
    return [image.subsurface(pygame.Rect(((tile_w + interval) * j, (tile_h + interval) * i),
                                         (tile_w, tile_h)))
            for i in range(rows) for j in range(cols)]


def load_texture(name, colorkey=None):
    fullname = os.path.join('data/textures', name)
    if not os.path.isfile(fullname):
        print('File is not exist')
        exit(0)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_map(filename):
    base_filename = os.path.join('data/maps', filename + '.csv')
    cdata_filename = os.path.join('data/maps', filename + '_cdata.json')
    if not os.path.isfile(base_filename) or not os.path.isfile(cdata_filename):
        print('File is not exist')
        exit(0)

    with open(base_filename, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        result = [[int(i) for i in row] for row in reader]
    with open(cdata_filename) as f:
        cdata = json.load(f)

    return result, cdata


def update_game():
    try:
        y = yadisk.YaDisk(token=YADISK_API_KEY)
        if not y.check_token():
            yield -1.0
    except yadisk.exceptions.YaDiskError:
        yield -1.0
        return
    except requests.exceptions.RequestException:
        yield -1.0
        return

    def load_version_list(path):
        # Load version_list.txt from YaDisk
        try:
            y.download(os.path.join(YADISK_GAME_PATH, VERSION_LIST_FNAME), path)
        except yadisk.exceptions.YaDiskError:
            return -1
        return 0

    def get_assets_to_update():
        def compare_version(a, b):
            for ai, bi in zip(a, b):
                if ai < bi:
                    return -1
                if ai > bi:
                    return 1
            return 0

        path = os.path.join('data/temp', VERSION_LIST_FNAME)
        if load_version_list(path) != 0:
            return -1, [], '0.0.1'

        with open(path) as t:
            data = json.load(t)

        with open(os.path.join('data', CURRENT_VERSION_FNAME), encoding='utf-8') as t:
            installed_version = t.readline().rstrip('\n')

        versions = sorted([k for k in data], key=lambda x: [int(m) for m in x.split('.')])
        while versions:
            if compare_version(installed_version, versions[0]) == -1:
                break
            versions.pop(0)

        result = []
        for j in versions:
            result.extend(data[j])

        if not versions:
            versions.append(installed_version)
        return 0, list(set(result)), versions[-1]

    code, assets, version = get_assets_to_update()

    yield 0.0
    for i, asset in enumerate(assets):
        sleep(YADISK_LOADER_INTERVAL_SLEEP)
        try:
            y.download(os.path.join(YADISK_GAME_PATH, asset), os.path.join('data', asset))
        except yadisk.exceptions.YaDiskError:
            yield -1.0
        yield round(100 * (i + 1) / len(assets), 1)
    sleep(YADISK_LOADER_INTERVAL_SLEEP)

    with open(os.path.join('data', CURRENT_VERSION_FNAME), 'w', encoding='utf-8') as f:
        f.write(version)

    yield 1000000.0
