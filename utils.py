import numpy as np


def get_representation(representation):
    arr = representation.split("\n")
    maxlen = len(max(arr, key=len))

    return np.array([list(x + (' ' * (maxlen - len(x)))) for x in arr])


layout_1 = [
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
    '                                         00000000                                                            ',
    '                                         33333333                                                            ',
    '                                         22222222                                                            ',
    '                                         11111111                                                            ',
    '                                                                                                             ',
    '                       33333333                            33333333                                          ',
    '                             11111111                11111111                                                ',
    '                                   11111111    11111111                                                      ',
    '                                         11111111                                                            ',
]


def get_bricks(Brick):
    bricks = []

    for y in range(len(layout_1)):
        x = 0

        while x < len(layout_1[y]):
            if layout_1[y][x] == ' ':
                x += 1
                continue

            if layout_1[y][x] == '0':
                strength = -1
            else:
                strength = int(layout_1[y][x])

            bricks.append(Brick(position=np.array([y, x]), strength=strength))

            x += 4

    return bricks
