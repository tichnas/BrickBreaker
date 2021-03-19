import numpy as np


def get_representation(representation):
    arr = representation.split("\n")
    maxlen = len(max(arr, key=len))

    return np.array([list(x + (' ' * (maxlen - len(x)))) for x in arr])


layouts = [
    [
        '',
        '                                    3333333333333333                                                         ',
        '                        222222222222                222222222222                                             ',
        '            111111111111                                        111111111111                                 ',
        '    00000000                                                                00000000                         ',
    ],
    [
        '                                    3333333333333333                                                         ',
        '                        222222222222                222222222222                                             ',
        '            111111111111                                        111111111111                                 ',
        '    00000000                                                                00000000                         ',
        '                                                                                                             ',
        '                      1111                                           1111                                    ',
        '                  111100001111                                   111100001111                                ',
        '                  111100001111                                   111100001111                                ',
        '                      1111                                           1111                                    ',
        '                                                                                                             ',
        '                                                                                                             ',
        '                                         55555555                                                            ',
        '                                         33333333                                                            ',
        '                                         22222222                                                            ',
        '                                         11111111                                                            ',
        '                                                                                                             ',
        '                       33333333                            33333333                                          ',
        '                             11111111                11111111                                                ',
        '                                   44444444    44444444                                                      ',
        '                                         44444444                                                            ',
    ],
    [
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '        0000            0000            0000            0000            0000            0000',
        '        0000            0000            0000            0000            0000            0000',
        '        0000            0000            0000            0000            0000            0000',
        '        0000            0000            0000            0000            0000            0000',
        '        0000            0000            0000            0000            0000            0000',
        '        0000            0000            0000            0000            0000            0000',
    ],
]


def get_bricks(Brick, level=0):
    if level >= len(layouts):
        return None

    bricks = []

    layout = layouts[level]

    for y in range(len(layout)):
        x = 0

        while x < len(layout[y]):
            ch = layout[y][x]
            if ch == ' ':
                x += 1
                continue

            if ch == '0':
                strength = -1
            else:
                strength = int(ch)

            bricks.append(
                Brick(position=np.array([y+2, x]), strength=strength))

            x += 4

    return bricks
