from pico2d import *

canvasW = 800
canvasH = 600
centerX = canvasW / 2
centerY = canvasH / 2
open_canvas(canvasW, canvasH)

character = load_image('character.png')
grass = load_image('grass.png')


def move_circle():
    theta = math.radians(degree)
    x = centerX + radius * math.cos(theta)
    y = centerY + radius * math.sin(theta)

def move_rectangle():
    print('rectangle')

def move_triangle():
    print('triangle')


while(1):
    clear_canvas()

    character.draw(centerX, centerY)
    grass.draw(centerX, centerY-60)
    radius = 200

    move_circle()
    move_rectangle()
    move_triangle()

    update_canvas()
    delay(0.01)
    pass


delay(10)
close_canvas()