import os
import time
import json

import keyboard

VERSION = '0.0.1'


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
    with open('map.json', 'r') as file:
        key_map = json.loads(file.read())
    if os.path.isfile('stats.json'):
        with open('stats.json', 'r') as file:
            key_stats = json.loads(file.read())
    if os.path.isfile('pairs.json'):
        with open('pairs.json', 'r') as file:
            key_pairs = json.loads(file.read())

    while True:
        menu = [
            '1 - Collect data',
            '2 - Most used keys',
            '3 - Check your keyboard',
            '0 - Clear data',
            'Press any other key to exit',
        ]
        print('\n'.join(menu), '\n')

        key = keyboard.read_key(True)
        if key == '1':
            print('Just use your PC as usual...')
            keyboard.on_release(stats_func)
            while True:
                time.sleep(10)
                with open('stats.json', 'w') as file:
                    file.write(json.dumps(key_stats))
                with open('pairs.json', 'w') as file:
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
                    print(f'{sign_rate*100:.2f}%\t{key_map[str(sign)]}')
        elif key == '3':
            print('Press Ctrl + Backspace to exit')
            keyboard.on_press(debug_func)
            keyboard.wait('ctrl+backspace')
            time.sleep(0.5)
        elif key == '0':
            try:
                os.remove('stats.json')
                os.remove('pairs.json')
                print('Data has been cleared!')
            except FileNotFoundError:
                print('No data detected.')
        else:
            exit()
        time.sleep(0.1)
