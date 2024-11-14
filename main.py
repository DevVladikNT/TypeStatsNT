import json
import os
import time

import keyboard

VERSION = '0.0.2'


def stats_func(e: keyboard.KeyboardEvent) -> None:
    if e.name is not None:
        key_stats[e.scan_code] = key_stats.get(e.scan_code, 0) + 1
        make_pair_stats(e)


def make_pair_stats(e: keyboard.KeyboardEvent) -> None:
    global last
    chars_arr = [
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
        30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
    ]
    if last != e.scan_code and e.scan_code in chars_arr:
        if last:
            key_pairs[f'{last}_{e.scan_code}'] = key_pairs.get(f'{last}_{e.scan_code}', 0) + 1
        last = e.scan_code


def debug_func(e: keyboard.KeyboardEvent) -> None:
    print(f'[{e.name}] > [{key_map.get(str(e.scan_code), "unknown")}] {e.scan_code}')


def compare_versions() -> None:
    global config
    last_ver = config.get('ver', '0.0.0')
    old_parts = last_ver.split('.')
    new_parts = VERSION.split('.')
    for i in range(3):
        if new_parts[i] > old_parts[i]:
            update()
            return


def update() -> None:
    config['ver'] = VERSION
    # todo for future updates
    with open('data/config.json', 'w') as config_file:
        config_file.write(json.dumps(config))


def format_counter(count: int) -> str:
    if 0 <= count < 1e3:
        result = str(count)
    elif 1e3 <= count < 1e6:
        result = f'{(count/1e3):.2f} k'
    elif 1e6 <= count < 1e9:
        result = f'{(count / 1e6):.2f} m'
    else:
        result = f'{(count / 1e9):.2f} b'
    return result


if __name__ == '__main__':
    print(f'TypeStatsNT v{VERSION} by VladikNT')
    key_stats = {}
    key_pairs = {}
    last = None
    with open('maps/map.json', 'r') as file:
        key_map = json.loads(file.read())
    if os.path.isfile('data/stats.json'):
        with open('data/stats.json', 'r') as file:
            key_stats = json.loads(file.read())
    if os.path.isfile('data/pairs.json'):
        with open('data/pairs.json', 'r') as file:
            key_pairs = json.loads(file.read())

    if not os.path.isfile('data/config.json'):
        config = {'ver': VERSION}
        print('Welcome! I hope you will find it useful :D\n'
              'Do you use RU keyboard? y/n')
        key = keyboard.read_key()
        print()
        config['ru'] = 1 if keyboard.key_to_scan_codes(key)[0] == 21 else 0
        with open('data/config.json', 'w') as config_file:
            config_file.write(json.dumps(config))
    else:
        try:
            with open('data/config.json', 'r') as file:
                config = json.loads(file.read())
            compare_versions()
        except json.JSONDecodeError:
            os.remove('data/config.json')
            print('Corrupted config!\nExiting...')
            time.sleep(1)
            exit()

    if config['ru'] == 1:
        with open('maps/map_ru.json', 'r', encoding='utf-8') as file:
            key_map_ru = json.loads(file.read())
        for key in key_map_ru.keys():
            key_map[key] += key_map_ru[key]

    menu = [
        '[1] Collect data',
        '[2] Most used keys',
        '[3] Deep letters analysis',
        '[4] Check your keyboard',
        '[9] Clear settings and exit',
        '[0] Clear data',
        'Press any other key to exit',
    ]
    while True:
        print('\n'.join(menu), '\n')

        time.sleep(0.1)
        key = keyboard.read_key(True)
        if key == '1':
            print('Just use your PC as usual...\n(But don\'t close this program)')
            keyboard.on_release(stats_func)
            while True:
                time.sleep(60)
                with open('data/stats.json', 'w') as file:
                    file.write(json.dumps(key_stats))
                with open('data/pairs.json', 'w') as file:
                    file.write(json.dumps(key_pairs))
        elif key == '2':
            top_size = 10 if len(key_stats.keys()) > 10 else len(key_stats.keys())
            if top_size == 0:
                print('No data detected.')
            else:
                stats_sorted = dict(sorted(key_stats.items(), key=lambda item: item[1], reverse=True))
                print(f'Total keys = {format_counter(sum(key_stats.values()))}')
                print(f'Top-{top_size}:')
                for sign in list(stats_sorted.keys())[:top_size]:
                    sign_rate = stats_sorted[sign] / sum(stats_sorted.values())
                    print(f'{sign_rate*100:.2f}%\t[{key_map[str(sign)]}]')
        elif key == '3':
            keys_to_ignore = ['26', '27', '39', '40'] if config['ru'] == 0 else []
            key_usage_count = {}
            nearest_neighbors = {}
            for key in key_pairs.keys():
                keys = key.split('_')
                if (keys[0] in keys_to_ignore) or (keys[1] in keys_to_ignore):
                    continue
                key_usage_count[keys[0]] = key_usage_count.get(keys[0], 0) + key_pairs[key]
                key_usage_count[keys[1]] = key_usage_count.get(keys[1], 0) + key_pairs[key]
                neighbors = nearest_neighbors.get(keys[0], {})
                neighbors[keys[1]] = neighbors.get(keys[1], 0) + key_pairs[key]
                nearest_neighbors[keys[0]] = neighbors

            print('All characters rate:')
            key_usage_count = dict(sorted(key_usage_count.items(), key=lambda item: item[1], reverse=True))
            for key in key_usage_count.keys():
                key_rate = key_usage_count[key] / sum(key_usage_count.values())
                print(f'{key_rate * 100:.2f}% [{key_map[str(key)]}]   >>>', end='   ')
                nearest_neighbors[key] = dict(
                    sorted(nearest_neighbors[key].items(), key=lambda item: item[1], reverse=True))
                for neighbor in nearest_neighbors[key].keys():
                    neighbor_rate = nearest_neighbors[key][neighbor] / sum(nearest_neighbors[key].values())
                    print(f'{neighbor_rate * 100:.2f}% [{key_map[str(neighbor)]}]', end=', ')
                print()
        elif key == '4':
            print('Press Ctrl + Backspace to exit')
            keyboard.on_press(debug_func)
            keyboard.wait('ctrl+backspace')
            time.sleep(0.5)
        elif key == '9':
            try:
                os.remove('data/config.json')
                print('Success!\nExiting...')
            except FileNotFoundError:
                print('No config file detected.\nExiting...')
            time.sleep(1)
            exit()
        elif key == '0':
            try:
                os.remove('data/stats.json')
                os.remove('data/pairs.json')
                print('Data has been cleared!')
            except FileNotFoundError:
                print('No data detected.')
        else:
            exit()
