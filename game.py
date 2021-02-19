import time
import random
import numpy as np
from screen import Screen
import config
from key_input import KeyInput
from object import Paddle, Ball, Brick, ExpandPaddle, ShrinkPaddle, BallMultiply, ThruBall, FastBall
from utils import get_representation


class Game:
    def __init__(self):
        # clear screen + hide cursor
        print("\033[?25l\033[2J", end='')

        random.seed(time.time())

        self.__screen = Screen()

        self.__frame = 0

        self.__paddle = Paddle()

        self.__powers = []

        self.__powered_balls = 0

        self.__balls = [Ball(activated=False, position=np.array(
            [self.__paddle.get_position()[0]-1, self.__paddle.get_mid_x()]))]

        self.__bricks = [
            Brick(position=[5, 5], strength=-1),
            Brick(position=[5, 10], strength=1),
            Brick(position=[7, 10], strength=1),
            Brick(position=[9, 10], strength=1),
            Brick(position=[11, 10], strength=1),
            Brick(position=[3, 10], strength=2),
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

            for ball in self.__balls:
                ball.move(self.__paddle)

            for power in self.__powers:
                if not power.is_activated():
                    power.move()
                    if power.is_destroyed():
                        self.__powers.remove(power)
                elif power.check_finished(self.__frame):
                    self.__powers.remove(power)

                    if isinstance(power, ExpandPaddle) or isinstance(power, ShrinkPaddle):
                        power.deactivate(self.__paddle)

                    if isinstance(power, ThruBall):
                        power.deactivate(self.unpower_balls)

                    if isinstance(power, FastBall):
                        power.deactivate(self.__balls)

            self.detect_collisions()

            self.__screen.draw(self.__paddle, self.__frame)

            for ball in self.__balls:
                self.__screen.draw(ball, self.__frame)

            for power in self.__powers:
                if not power.is_activated():
                    self.__screen.draw(power, self.__frame)

            for brick in self.__bricks:
                if brick.is_destroyed():
                    continue
                self.__screen.draw(brick, self.__frame)

            self.__screen.show()

    def manage_keys(self, ch):
        if ch == 'q':
            return False

        if ch == 'a' or ch == 'd':
            self.__paddle.key_press(ch)

        if ch == ' ':
            for ball in self.__balls:
                if not ball.is_activated():
                    ball.activate()
                    break

        return True

    def detect_collisions(self):
        # Ball with wall
        for ball in self.__balls:
            [collide_y, collide_x] = ball.is_intersection(
                [0, 0], [config.HEIGHT, config.WIDTH])
            if collide_x:
                ball.reverse_x()
            if collide_y:
                ball.reverse_y()

        # Ball with bricks
        for ball in self.__balls:
            for brick in self.__bricks:
                if brick.is_destroyed():
                    continue

                [collide_y, collide_x] = ball.is_intersection(
                    brick.get_position(), brick.get_dimensions())

                if self.__powered_balls == 0:
                    if collide_x:
                        ball.reverse_x()
                    if collide_y:
                        ball.reverse_y()

                if collide_x or collide_y:
                    if self.__powered_balls > 0:
                        brick.power_hit()
                    else:
                        brick.collide()

                    if brick.is_destroyed() and random.randint(1, 100) <= 75:
                        self.generate_power(brick.get_position())

        # Ball with paddle
        for ball in self.__balls:
            [collide_y, collide_x] = ball.is_intersection(
                self.__paddle.get_position(), self.__paddle.get_dimensions())

            if collide_x or collide_y:
                ball.reverse_y()
                ball_x = ball.get_position()[1]
                paddle_mid_x = self.__paddle.get_mid_x()
                ball.change_speed_x(0.1 * (ball_x - paddle_mid_x))

        # Paddle with powers
        for power in self.__powers:
            if power.is_activated():
                continue

            [collide_y, collide_x] = self.__paddle.is_intersection(
                power.get_position(), power.get_dimensions())

            if collide_y or collide_x:
                if isinstance(power, ExpandPaddle) or isinstance(power, ShrinkPaddle):
                    power.activate(self.__frame, self.__paddle)

                if isinstance(power, BallMultiply) or isinstance(power, FastBall):
                    power.activate(self.__frame, self.__balls)

                if isinstance(power, ThruBall):
                    power.activate(self.__frame, self.power_balls)

    def clear(self):
        self.__screen.clear()
        # place cursor at top left
        print("\033[0;0H")

    def generate_power(self, position):
        powers = [ExpandPaddle, ShrinkPaddle, BallMultiply, ThruBall, FastBall]
        index = random.randint(0, len(powers)-1)
        index = 3

        self.__powers.append(powers[index](position=position))

    def power_balls(self):
        self.__powered_balls += 1

    def unpower_balls(self):
        self.__powered_balls -= 1
