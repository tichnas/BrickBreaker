import time
import numpy as np
from screen import Screen
import config
from key_input import KeyInput
from object import Paddle, Ball
from utils import get_representation


class Game:
    def __init__(self):
        # clear screen + hide cursor
        print("\033[?25l\033[2J", end='')

        self.__screen = Screen()

        self.__frame = 0

        self.__paddle = Paddle(speed=np.array(
            [0, 1]), representation=get_representation('====='), position=np.array([config.HEIGHT-1, 10]))

        self.__ball = Ball(speed=np.array([-0.7, 0.7]), representation=get_representation(
            '*'), position=np.array([config.HEIGHT - 3, 12]))

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

            self.__ball.move()

            self.detect_collisions()

            self.__screen.draw(self.__paddle, self.__frame)
            self.__screen.draw(self.__ball, self.__frame)

            self.__screen.show()

    def manage_keys(self, ch):
        if ch == 'q':
            return False

        self.__paddle.key_press(ch)

        return True

    def detect_collisions(self):
        # Ball with wall
        [collide_y, collide_x] = self.__ball.is_intersection(
            [0, 0], [config.HEIGHT, config.WIDTH])
        if collide_x:
            self.__ball.reverse_x()
        if collide_y:
            self.__ball.reverse_y()

    def clear(self):
        self.__screen.clear()
        # place cursor at top left
        print("\033[0;0H")
