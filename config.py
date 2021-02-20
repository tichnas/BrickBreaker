import os

screen_height, screen_width = [
    int(x) for x in os.popen("stty size", "r").read().split()]

WIDTH = screen_width - 10
HEIGHT = screen_height - 5

FRAME_RATE = 30

POWER_DURATION = 15  # in seconds

LIVES = 3
