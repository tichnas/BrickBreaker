import time
import numpy as np
from screen import Screen
import config
from key_input import KeyInput
from object import Paddle
from utils import get_representation


class Game:
    def __init__(self):
        # clear screen + hide cursor
        print("\033[?25l\033[2J", end='')

        self.__screen = Screen()

        self.__frame = 0

        self.__paddle = Paddle(speed=np.array(
            [0, 1]), representation=get_representation('====='), position=np.array([config.HEIGHT-1, 10]))

    def start(self):
        key_input = KeyInput()

        while True:
            self.__frame += 1
            time.sleep(1/config.FRAME_RATE)

            if key_input.input_given():
                if not self.manage_keys(key_input.get()):
                    break
            else:
                key_input.clear()

            self.clear()

            self.__screen.draw(self.__paddle, self.__frame)

            self.__screen.show()

    def manage_keys(self, ch):
        if ch == 'q':
            return False

        self.__paddle.key_press(ch)

        return True

    def clear(self):
        self.__screen.clear()
        # place cursor at top left
        print("\033[0;0H")
