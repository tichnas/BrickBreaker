import numpy as np
import colorama as col
import math
import config
from utils import get_representation


class Object:
    def __init__(self, **kwargs):
        self.__representation = kwargs.get('representation', np.array([[' ']]))
        self.__position = kwargs.get('position', np.array([0, 0]))
        self.__color = kwargs.get('color', np.array([['', '']]))
        self.__height, self.__width = self.__representation.shape

    def set_position(self, position):
        position_x = position[1]
        position_y = position[0]

        position_x = min(position_x, config.WIDTH - self.__width)
        position_x = max(position_x, 0)

        position_y = min(position_y, config.HEIGHT - self.__height)
        position_y = max(position_y, 0)

        self.__position = np.array([position_y, position_x])

    def get_position(self):
        return self.__position

    def get_dimensions(self):
        return self.__height, self.__width

    def get_representation(self, frame):
        return self.__representation, self.__color

    def set_color(self, color):
        self.__color = color

    def set_representation(self, representation):
        self.__representation = representation
        self.__height, self.__width = self.__representation.shape


class MovingObject(Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__speed = kwargs.get('speed', np.array([0, 0]))

    def shift(self, value=np.array([0, 0])):
        old_position = self.get_position()
        new_position = np.add(old_position, value)
        self.set_position(new_position)

    def get_speed(self):
        return self.__speed

    def set_speed(self, speed):
        self.__speed = speed

    def is_intersection(self, position, dimensions):
        my_position = self.get_position()
        my_dimensions = self.get_dimensions()

        left = position[1]
        right = position[1] + dimensions[1] - 1
        top = position[0]
        bottom = position[0] + dimensions[0] - 1

        my_left = my_position[1]
        my_right = my_position[1] + my_dimensions[1] - 1
        my_top = my_position[0]
        my_bottom = my_position[0] + my_dimensions[0] - 1

        outside = (my_right + 1 < left or my_left >
                   right + 1 or my_top > bottom + 1 or my_bottom + 1 < top)

        if outside:
            return [False, False]

        collision_x = abs(my_left - right) <= 1 or abs(my_right -
                                                       left) <= 1 or abs(my_left - left) <= 1 or abs(my_right - right) <= 1
        collision_y = abs(my_top - bottom) <= 1 or abs(my_bottom -
                                                       top) <= 1 or abs(my_top - top) <= 1 or abs(my_bottom - bottom) <= 1

        return [collision_y, collision_x]


class Paddle(MovingObject):
    def __init__(self,  **kwargs):
        kwargs.setdefault('speed', np.array([0, 1]))
        kwargs.setdefault('position', np.array([config.HEIGHT-2, 10]))
        kwargs.setdefault('representation', get_representation('====='))

        super().__init__(**kwargs)

    def key_press(self, ch):
        if ch == "a":
            speed_x = self.get_speed()[1]
            self.shift(np.array(np.array([0, -speed_x])))
        elif ch == "d":
            speed_x = self.get_speed()[1]
            self.shift(np.array(np.array([0, speed_x])))

    def get_mid_x(self):
        x = self.get_position()[1]
        width = self.get_dimensions()[1]
        return x + (width - 1) / 2

    def expand(self):
        width = self.get_dimensions()[1]
        self.set_representation(get_representation("=" * (width + 2)))

    def shrink(self):
        width = self.get_dimensions()[1]
        self.set_representation(get_representation("=" * (width - 2)))


class Ball(MovingObject):
    def __init__(self,  **kwargs):
        kwargs.setdefault('speed', np.array([-0.5, 0.5]))
        kwargs.setdefault('representation', get_representation('*'))

        super().__init__(**kwargs)

        self.__activated = kwargs.get('activated', True)
        self.__powered = kwargs.get('powered', False)

    def activate(self):
        self.__activated = True

    def is_activated(self):
        return self.__activated

    def move(self, paddle: Paddle):
        if self.__activated:
            speed = self.get_speed()
            self.shift(speed)
        else:
            position_y = self.get_position()[0]
            position_x = paddle.get_mid_x()
            self.set_position(np.array([position_y, position_x]))

    def is_intersection(self, position, dimensions):
        if self.__activated:
            return super().is_intersection(position, dimensions)
        else:
            return [False, False]

    def reverse_x(self):
        [speed_y, speed_x] = self.get_speed()
        self.set_speed(np.array([speed_y, -speed_x]))

    def reverse_y(self):
        [speed_y, speed_x] = self.get_speed()
        self.set_speed(np.array([-speed_y, speed_x]))

    def change_speed_x(self, change):
        [speed_y, speed_x] = self.get_speed()
        self.set_speed(np.array([speed_y, speed_x + change]))


class Brick(Object):
    def __init__(self,  **kwargs):
        kwargs.setdefault('representation', get_representation('....'))

        super().__init__(**kwargs)

        self.__strength = kwargs.get('strength', 1)
        self.__destroyed = False
        self.update_color()

    def is_destroyed(self):
        return self.__destroyed

    def update_color(self):
        colors = [
            [[col.Back.MAGENTA, col.Fore.MAGENTA]],
            [[col.Back.CYAN, col.Fore.CYAN]],
            [[col.Back.YELLOW, col.Fore.YELLOW]],
            [[col.Back.RED, col.Fore.RED]],
        ]
        self.set_color(colors[max(0, self.__strength)])

    def collide(self):
        if self.__strength == -1:
            return

        self.__strength -= 1

        if self.__strength == 0:
            self.__destroyed = True
        else:
            self.update_color()

    def power_hit(self):
        print('destroy')
        self.__destroyed = True


class PowerUp(MovingObject):
    def __init__(self,  **kwargs):
        kwargs.setdefault('speed', np.array([2, 0]))

        super().__init__(**kwargs)

        self.__start = None

    def move(self):
        speed = self.get_speed()
        self.shift(speed)

    def is_destroyed(self):
        return self.get_position()[0] == config.HEIGHT - 1

    def activate(self, frame):
        self.__start = frame

    def is_activated(self):
        if self.__start:
            return True
        return False

    def finish(self):
        print('Override this')

    def check_finished(self, frame):
        if not self.__start:
            return False

        if frame - self.__start >= config.POWER_DURATION * config.FRAME_RATE:
            return True

        return False


class ExpandPaddle(PowerUp):
    def __init__(self, **kwargs):
        kwargs.setdefault('representation', get_representation('P'))
        kwargs.setdefault('color', np.array([['', col.Fore.GREEN]]))

        super().__init__(**kwargs)

    def activate(self, frame, paddle: Paddle):
        paddle.expand()
        super().activate(frame)

    def deactivate(self, paddle: Paddle):
        paddle.shrink()


class ShrinkPaddle(PowerUp):
    def __init__(self, **kwargs):
        kwargs.setdefault('representation', get_representation('P'))
        kwargs.setdefault('color', np.array([['', col.Fore.RED]]))

        super().__init__(**kwargs)

    def activate(self, frame, paddle: Paddle):
        paddle.shrink()
        super().activate(frame)

    def deactivate(self, paddle: Paddle):
        paddle.expand()


class BallMultiply(PowerUp):
    def __init__(self, **kwargs):
        kwargs.setdefault('representation', get_representation('M'))
        kwargs.setdefault('color', np.array([['', col.Fore.GREEN]]))

        super().__init__(**kwargs)

    def activate(self, frame,  balls):
        extraBalls = []

        for ball in balls:
            position = ball.get_position()
            speed = np.negative(ball.get_speed())
            extraBalls.append(Ball(position=position,
                                   speed=speed))

        for ball in extraBalls:
            balls.append(ball)

        super().activate(frame)


class ThruBall(PowerUp):
    def __init__(self, **kwargs):
        kwargs.setdefault('representation', get_representation('T'))
        kwargs.setdefault('color', np.array([['', col.Fore.GREEN]]))

        super().__init__(**kwargs)

    def activate(self, frame,  power_balls):
        power_balls()
        super().activate(frame)

    def deactivate(self, unpower_balls):
        unpower_balls()


class FastBall(PowerUp):
    def __init__(self, **kwargs):
        kwargs.setdefault('representation', get_representation('F'))
        kwargs.setdefault('color', np.array([['', col.Fore.RED]]))

        super().__init__(**kwargs)

    def activate(self, frame,  balls):
        for ball in balls:
            ball.set_speed(ball.get_speed() * 1.1)

        super().activate(frame)

    def deactivate(self, balls):
        for ball in balls:
            ball.set_speed(ball.get_speed() / 1.1)
