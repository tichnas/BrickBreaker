import time
import numpy as np
from screen import Screen
import config
from key_input import KeyInput
from object import Paddle, Ball, Brick
from utils import get_representation


class Game:
    def __init__(self):
        # clear screen + hide cursor
        print("\033[?25l\033[2J", end='')

        self.__screen = Screen()

        self.__frame = 0

        self.__paddle = Paddle(speed=np.array(
            [0, 1]), representation=get_representation('====='), position=np.array([config.HEIGHT-1, 10]))

        self.__ball = Ball(speed=np.array([-0.5, 0.5]), representation=get_representation(
            '*'), position=np.array([config.HEIGHT - 3, 12]))

        self.__bricks = [
            Brick(position=[5, 5], strength=-1),
            Brick(position=[5, 10], strength=1),
            Brick(position=[5, 15], strength=2),
            Brick(position=[5, 20], strength=3),
        ]

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

            for brick in self.__bricks:
                if brick.is_destroyed():
                    continue
                self.__screen.draw(brick, self.__frame)

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

        # Ball with bricks
        for brick in self.__bricks:
            if brick.is_destroyed():
                continue

            [collide_y, collide_x] = self.__ball.is_intersection(
                brick.get_position(), brick.get_dimensions())

            if collide_x:
                self.__ball.reverse_x()
            if collide_y:
                self.__ball.reverse_y()
            if collide_x or collide_y:
                brick.collide()

    def clear(self):
        self.__screen.clear()
        # place cursor at top left
        print("\033[0;0H")
