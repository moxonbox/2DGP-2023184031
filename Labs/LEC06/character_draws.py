from pico2d import *

canvasW = 800
canvasH = 600
centerX = canvasW / 2
centerY = canvasH / 2
open_canvas(canvasW, canvasH)

character = load_image('character.png')
grass = load_image('grass.png')

# ============================= 함수 정의

def draw_boy(x, y):
    clear_canvas()
    grass.draw(centerX, centerY-60)
    character.draw(x, y)
    update_canvas()
    delay(0.01)

def move_circle():
    for degree in range(360):
        radius = 200
        theta = math.radians(degree)
        x = centerX + radius * math.cos(theta)
        y = centerY + radius * math.sin(theta)
        draw_boy(x, y)
    pass

def move_top():
    for x in range(50, 751, 5):
        draw_boy(x, 550)

def move_right():
    for y in range(550, 49, -5):
        draw_boy(750, y)

def move_bottom():
    for x in range(750, 49, -5):
        draw_boy(x, 50)

def move_left():
    for y in range(50, 551, 5):
        draw_boy(50, y)

def move_rectangle():
    move_top()
    move_right()
    move_bottom()
    move_left()

def move_triangle():
    print('triangle')

# ============================= 실행 루프

while(1):

    move_circle()
    move_rectangle()
    move_triangle()
    
    pass

delay(10)
close_canvas()