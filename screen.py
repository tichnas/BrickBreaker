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
        self.color[:, :, 0] = col.Back.WHITE
        self.color[:, :, 1] = col.Fore.BLACK

    def draw(self, obj, frame):
        y, x = obj.get_position()
        h, w = obj.get_dimensions()

        display, color = obj.get_representation(frame)

        self.display[y:y+h, x:x+w] = display
        self.color[y:y+h, x:x+w] = color

    def show(self):
        output = ""
        for i in range(self.height):
            for j in range(self.width):
                output += "".join(self.color[i][j]) + self.display[i][j]
            output += '\n'

        sys.stdout.write(output)
