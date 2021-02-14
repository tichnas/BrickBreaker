import time
from screen import Screen
import config
from key_input import KeyInput


class Game:
    def __init__(self):
        # clear screen + hide cursor
        print("\033[?25l\033[2J", end='')

        self.__screen = Screen()

        self.__frame = 0

    def start(self):
        key_input = KeyInput()

        while True:
            print(self.__frame)
            self.__frame += 1
            time.sleep(1/config.FRAME_RATE)

            if key_input.input_given():
                if not self.manage_keys(key_input.get()):
                    break
            else:
                key_input.clear()

            self.clear()

            self.__screen.show()

    def manage_keys(self, ch):
        if ch == 'q':
            return False

        return True

    def clear(self):
        self.__screen.clear()
        # place cursor at top left
        print("\033[0;0H")
