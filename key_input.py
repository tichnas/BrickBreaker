import termios
import sys
import atexit
from select import select


class KeyInput:
    def __init__(self):
        self.__fd = sys.stdin.fileno()
        self.__new_term = termios.tcgetattr(self.__fd)
        self.__old_term = termios.tcgetattr(self.__fd)

        # New terminal setting unbuffered
        self.__new_term[3] = (self.__new_term[3] & ~
                              termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.__fd, termios.TCSAFLUSH, self.__new_term)

        # Support normal-terminal reset at exit
        atexit.register(self.reset)

    def reset(self):
        termios.tcsetattr(self.__fd, termios.TCSAFLUSH, self.__old_term)

    @staticmethod
    def get():
        return sys.stdin.read(1)

    @staticmethod
    def input_given():
        return select([sys.stdin], [], [], 0)[0] != []

    @staticmethod
    def clear():
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
