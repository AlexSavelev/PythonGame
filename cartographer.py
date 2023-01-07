import json
import os
import csv

if __name__ == '__main__':
    map_name = input()

    base_filename = os.path.join('data/maps', map_name + '.csv')
    with open(base_filename, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        m = [[int(i) for i in row] for row in reader]

    try:
        with open(f'data/maps/{map_name}_cdata.json') as f:
            old_data = json.load(f)
    except FileNotFoundError:
        old_data = {}

    data = {}

    for x in range(len(m[0])):
        for y in range(len(m)):
            t = m[y][x]

            item_key = ''
            item_value = ''
            if not 96 <= t <= 99:
                continue
            if t == 96:  # Card
                item_key = f'{map_name}_card_{x}_{y}'
                item_value = {'gp_var_key': '', 'gp_var_value': 0}
            elif t == 97:  # Chest
                item_key = f'{map_name}_chest_{x}_{y}'
                item_value = {'open_condition': 'true', 'items': []}
            elif t == 98:  # Money
                item_key = f'{map_name}_money_{x}_{y}'
                item_value = {'count': 0}
            elif t == 99:  # Skateboard
                item_key = f'{map_name}_skateboard_{x}_{y}'
                item_value = {'number': 0}

            if item_key in old_data:
                data[item_key] = old_data[item_key]
            else:
                data[item_key] = item_value

    with open(f'data/maps/{map_name}_cdata.json', 'w') as f:
        f.write(json.dumps(data, indent=4))
