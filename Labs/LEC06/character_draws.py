from pico2d import *

canvasW = 800
canvasH = 600
centerX = canvasW / 2
centerY = canvasH / 2
open_canvas(canvasW, canvasH)


def move_circle():
    print('circle')

def move_rectangle():
    print('rectangle')

def move_triangle():
    print('triangle')


while(1):

    move_circle()
    move_rectangle()
    move_triangle()

    pass


delay(10)
close_canvas()