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
        super().__init__(**kwargs)

    def key_press(self, ch):
        if ch == "a":
            speed_x = self.get_speed()[1]
            self.shift(np.array(np.array([0, -speed_x])))
        elif ch == "d":
            speed_x = self.get_speed()[1]
            self.shift(np.array(np.array([0, speed_x])))


class Ball(MovingObject):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)

    def move(self):
        speed = self.get_speed()
        self.shift(speed)

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
        representation = kwargs.get(
            'representation', get_representation('....'))

        super().__init__(**kwargs, representation=representation)

        self.__strength = kwargs.get('strength', 1)
        self.__inactive = False
        self.update_color()

    def is_destroyed(self):
        return self.__inactive

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
            self.__inactive = True
        else:
            self.update_color()
