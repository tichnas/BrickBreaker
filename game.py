import time
import random
import numpy as np
from screen import Screen
import config
from key_input import KeyInput
from object import Paddle, Ball, Brick, ExpandPaddle, ShrinkPaddle, BallMultiply, ThruBall, FastBall, PaddleGrab, PaddleShooter, Life, Score, Time, Boss, Bomb
from utils import get_representation, get_bricks


class Game:
    def __init__(self):
        self.__time_limits = [10, 20]

        # clear screen + hide cursor
        print("\033[?25l\033[2J", end='')

        self.__screen = Screen()

        self.__frame = 0
        self.__level = 0
        self.__level_start_time = 0
        self.__last_shoot = 0
        self.__last_bomb = 0

        self.__lives = []
        for i in range(1, config.LIVES):
            self.__lives.append(Life(position=np.array([0, config.WIDTH - i])))

        self.__score = Score()

        self.__time = Time()

        self.__paddle = Paddle()

        self.__powers = []

        self.__powered_balls = 0
        self.__paddle_grab = 0
        self.__paddle_shooting = 0

        self.__balls = [Ball(activated=False, position=np.array(
            [self.__paddle.get_position()[0]-1, self.__paddle.get_mid_x()]))]

        self.__bricks = get_bricks(Brick)

        self.__boss = None
        self.__bomb = None

    def start(self):
        key_input = KeyInput()

        while True:
            self.__frame += 1
            time.sleep(1/config.FRAME_RATE)

            self.__time.set_time(self.__frame)

            if key_input.input_given():
                if not self.manage_keys(key_input.get()):
                    break
            else:
                key_input.clear()

            self.clear()

            for ball in self.__balls:
                ball.move(self.__paddle)

            for brick in self.__bricks:
                brick.randomize_strength()
                brick.decrease_timer()

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

                    if isinstance(power, PaddleGrab):
                        power.deactivate(self.paddle_ungrab)

                    if isinstance(power, PaddleShooter):
                        power.deactivate(self.paddle_shoot_off)

            if self.__paddle_shooting and not self.__paddle.is_shooting():
                self.__paddle.set_shooting(True)

            if not self.__paddle_shooting and self.__paddle.is_shooting():
                self.__paddle.set_shooting(False)

            self.detect_collisions()

            if self.check_lose() or self.check_finish():
                break

            self.__screen.draw(self.__score, self.__frame)

            self.__screen.draw(self.__time, self.__frame)

            for life in self.__lives:
                self.__screen.draw(life, self.__frame)

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

            if self.__boss:
                self.__boss.set_mid_x(self.__paddle.get_mid_x())
                self.__screen.draw(self.__boss, self.__frame)

                if not self.__bomb and (self.__frame - self.__last_bomb > 2 * config.FRAME_RATE):
                    self.__bomb = Bomb(position=[self.__boss.get_position()[0] + self.__boss.get_dimensions()[
                                       0], self.__paddle.get_mid_x()])
                elif self.__bomb:
                    self.__bomb.move()
                    if self.__bomb.is_destroyed():
                        self.__last_bomb = self.__frame
                        self.__bomb = None
                    else:
                        self.__screen.draw(self.__bomb, self.__frame)

                brick_y = self.__boss.get_position(
                )[0] + self.__boss.get_dimensions()[0] + 1
                produce_bricks = (self.__boss.get_health() +
                                  self.__boss.powers_used() == 1)

                for ball in self.__balls:
                    if ball.get_position()[0] < brick_y + 2:
                        produce_bricks = False
                        break
                if produce_bricks:
                    self.__boss.use_power()

                    for x in range(0, config.WIDTH - 4, 4):
                        self.__bricks.append(
                            Brick(position=np.array([brick_y, x]), strength=1))

            self.__screen.show()

    def manage_keys(self, ch):
        if ch == 'q':
            return False

        if ch == 'a' or ch == 'd':
            self.__paddle.key_press(ch)

        if ch == ' ':
            to_shoot = (self.__paddle_shooting > 0) and (self.__frame - self.__last_shoot >
                                                         config.FRAME_RATE)

            for ball in self.__balls:
                if not ball.is_activated():
                    ball.activate()
                    to_shoot = False
                    break

            if to_shoot:
                self.__last_shoot = self.__frame
                paddle_position = self.__paddle.get_position()
                position_y = paddle_position[0] - 1
                position_left = paddle_position[1]
                position_right = paddle_position[1] + \
                    self.__paddle.get_dimensions()[1] - 1

                self.__balls.append(
                    Ball(position=[position_y, position_left], speed=[-0.5, 0], temporary=True, representation=get_representation('^')))
                self.__balls.append(
                    Ball(position=[position_y, position_right], speed=[-0.5, 0], temporary=True, representation=get_representation('^')))

        if ch == 'n':
            self.check_finish(True)

        return True

    def detect_collisions(self):
        # Ball with wall
        out_balls = []
        for ball in self.__balls:
            [collide_y, collide_x] = ball.is_intersection(
                [0, 0], [config.HEIGHT, config.WIDTH])
            if collide_x:
                ball.reverse_x()
            if collide_y:
                ball.reverse_y()

            if ball.is_temporary() and (collide_x or collide_y):
                out_balls.append(ball)

            if ball.get_position()[0] >= config.HEIGHT - 2:
                out_balls.append(ball)
        for ball in out_balls:
            self.__balls.remove(ball)

        # Powers with wall
        for power in self.__powers:
            if not power.is_activated():
                [collide_y, collide_x] = power.is_intersection(
                    [0, 0], [config.HEIGHT, config.WIDTH])
                if collide_x:
                    power.reverse_x()
                if collide_y:
                    power.reverse_y()

        # Ball with Boss
        if self.__boss:
            for ball in self.__balls:
                [collide_y, collide_x] = ball.is_intersection(
                    self.__boss.get_position(), self.__boss.get_dimensions())

                if collide_x:
                    ball.reverse_x()
                if collide_y:
                    ball.reverse_y()

                if collide_x or collide_y:
                    if self.__boss.hit():
                        self.__boss = None

        # Ball with bricks
        out_balls = []
        for ball in self.__balls:
            initial_speed = ball.get_speed()

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
                    if ball.is_temporary():
                        out_balls.append(ball)

                    if self.__powered_balls > 0:
                        brick.power_hit()
                    else:
                        brick.collide()
                        ball.shift(np.array([ball.get_speed()[0], 0]))

                    if brick.is_destroyed():
                        self.__score.increase_score(10)
                        if random.randint(1, 100) <= 30 and self.__level < len(self.__time_limits) - 1:
                            self.generate_power(
                                brick.get_position(), initial_speed)

                    if self.__time.get_time(self.__frame) - self.__level_start_time > self.__time_limits[self.__level]:
                        ball.shift([1, 0])
                        for b in self.__bricks:
                            b.fall()

        for ball in out_balls:
            self.__balls.remove(ball)

        # Ball with paddle
        for ball in self.__balls:
            [collide_y, collide_x] = ball.is_intersection(
                self.__paddle.get_position(), self.__paddle.get_dimensions())

            if collide_x or collide_y:
                ball.reverse_y()
                ball_x = ball.get_position()[1]
                paddle_mid_x = self.__paddle.get_mid_x()
                ball.change_speed_x(0.1 * (ball_x - paddle_mid_x))

                if self.__paddle_grab > 0:
                    ball.deactivate()

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

                if isinstance(power, PaddleGrab):
                    power.activate(self.__frame, self.paddle_grab)

                if isinstance(power, PaddleShooter):
                    power.activate(self.__frame, self.paddle_shoot_on)

        # explode bricks & start timer for intersecting bricks
        for brick in self.__bricks:
            if (not brick.is_destroyed()) and brick.check_timer():
                brick.power_hit()
                self.__score.increase_score(7)

                for b in self.__bricks:
                    if (not b.is_destroyed()) and (not b.timer_exists()):
                        [collide_y, collide_x] = brick.is_intersection(
                            b.get_position(), b.get_dimensions())
                        if collide_y or collide_x:
                            b.set_timer(config.FRAME_RATE/5)

    def check_finish(self, cheat=False):
        finish = True

        for brick in self.__bricks:
            if not brick.is_destroyed() and brick.get_strength() > -1:
                finish = False
                break

        if self.__boss:
            finish = False

        if finish or cheat:
            self.__level += 1
            self.__balls = [Ball(activated=False, position=np.array(
                [self.__paddle.get_position()[0]-1, self.__paddle.get_mid_x()]))]
            new_bricks = get_bricks(Brick, self.__level)

            if not new_bricks:
                print('Game Finish!\nYour Score: ' +
                      str(self.__score.get_score()))
                return True

            self.__bricks = new_bricks
            self.__powered_balls = 0
            self.__paddle_grab = 0
            self.__level_start_time = self.__time.get_time(self.__frame)

            for power in self.__powers:
                if isinstance(power, ExpandPaddle) or isinstance(power, ShrinkPaddle):
                    power.deactivate(self.__paddle)

                if isinstance(power, ThruBall):
                    power.deactivate(self.unpower_balls)

                if isinstance(power, FastBall):
                    power.deactivate(self.__balls)

                if isinstance(power, PaddleGrab):
                    power.deactivate(self.paddle_ungrab)

            if self.__level == len(self.__time_limits) - 1:
                self.__boss = Boss()

            self.__powers = []

        return False

    def check_lose(self):
        game_over = False
        bomb_collide = False

        if self.__bomb:
            [collide_y, collide_x] = self.__paddle.is_intersection(
                self.__bomb.get_position(), self.__bomb.get_dimensions())
            bomb_collide = collide_x or collide_y

        if len(self.__balls) == 0 or bomb_collide:
            if len(self.__lives) > 0:
                self.__balls = [Ball(activated=False, position=np.array(
                    [self.__paddle.get_position()[0]-1, self.__paddle.get_mid_x()]))]
                self.__powers = []
                self.__powered_balls = 0
                self.__paddle_grab = 0
                self.__bomb = None
                self.__lives.pop()
            else:
                game_over = True

        for brick in self.__bricks:
            if brick.get_position()[0] == config.HEIGHT - 2:
                game_over = True
                break

        if game_over:
            self.__screen.destroy()
            print('Game Over!\nYour Score: ' +
                  str(self.__score.get_score()))
            return True

        return False

    def clear(self):
        self.__screen.clear()
        # place cursor at top left
        print("\033[0;0H")

    def generate_power(self, position, speed):
        powers = [ExpandPaddle, ShrinkPaddle,
                  BallMultiply, ThruBall, FastBall, PaddleGrab, PaddleShooter]
        index = random.randint(0, len(powers)-1)

        self.__powers.append(powers[index](position=position, speed=speed))

    def power_balls(self):
        self.__powered_balls += 1

    def unpower_balls(self):
        self.__powered_balls -= 1

    def paddle_grab(self):
        self.__paddle_grab += 1

    def paddle_ungrab(self):
        self.__paddle_grab -= 1

    def paddle_shoot_on(self):
        self.__paddle_shooting += 1

    def paddle_shoot_off(self):
        self.__paddle_shooting -= 1
