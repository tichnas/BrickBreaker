import colorama as col
import sys
import numpy as np
import config


class Screen:
    def __init__(self):
        self.width, self.height = config.WIDTH, config.HEIGHT
        self.color = np.full((self.height, self.width, 2), "", dtype=object)
        self.display = np.full((self.height, self.width), " ")

    def clear(self):
        self.display[:] = " "
        self.color[:, :, 0] = col.Back.LIGHTBLUE_EX
        self.color[:, :, 1] = col.Fore.BLACK

    def draw(self, obj, frame):
        x, y = obj.get_position()
        h, w = obj.get_dimensions()

        display, color = obj.get_representation(frame)

        display = display[:, max(0, -x):min(self.width - x, w)]
        color = color[:, max(0, -x):min(self.width - x, w)]

        self.display[y:y+h, max(0, x):min(x+w, self.width)] = display
        self.color[y:y+h, max(0, x):min(x+w, self.width)] = color

    def show(self):
        output = ""
        for i in range(self.height):
            for j in range(self.width):
                output += "".join(self.color[i][j]) + self.display[i][j]
            output += '\n'

        sys.stdout.write(output)
