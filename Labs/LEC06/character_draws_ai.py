import math
from pathlib import Path
from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
CENTER_X = CANVAS_WIDTH // 2
CENTER_Y = CANVAS_HEIGHT // 2


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


def draw_boy(x, y):
    if not handle_events():
        return False

    clear_canvas()
    grass.draw(CENTER_X, 30)
    character.draw(x, y)
    update_canvas()
    delay(0.01)
    return True


def move_along_line(x0, y0, x1, y1):
    """두 점 사이를 프레임당 최대 5픽셀씩 이동한다."""
    distance = math.hypot(x1 - x0, y1 - y0)
    steps = max(1, math.ceil(distance / 5))

    for step in range(steps + 1):
        t = step / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        if not draw_boy(x, y):
            return False
    return True


def move_circle():
    """화면 중심에서 반지름 200인 원을 한 바퀴 이동한다."""
    for degree in range(361):
        theta = math.radians(degree)
        x = CENTER_X + 200 * math.cos(theta)
        y = CENTER_Y + 200 * math.sin(theta)
        if not draw_boy(x, y):
            return False
    return True


def move_top():
    return move_along_line(50, 550, 750, 550)


def move_right():
    return move_along_line(750, 550, 750, 50)


def move_bottom():
    return move_along_line(750, 50, 50, 50)


def move_left():
    return move_along_line(50, 50, 50, 550)


def move_rectangle():
    """위, 오른쪽, 아래, 왼쪽 변을 순서대로 이동한다."""
    return move_top() and move_right() and move_bottom() and move_left()


def move_triangle():
    """삼각형의 세 변을 이동하고 시작점으로 돌아온다."""
    return (
        move_along_line(100, 100, 700, 100)
        and move_along_line(700, 100, 400, 500)
        and move_along_line(400, 500, 100, 100)
    )


def main():
    global character, grass

    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        image_directory = Path(__file__).resolve().parent
        character = load_image(str(image_directory / 'character.png'))
        grass = load_image(str(image_directory / 'grass.png'))

        # 각 경로를 한 바퀴씩 이동한 뒤 처음부터 반복한다.
        while move_circle() and move_rectangle() and move_triangle():
            pass
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
