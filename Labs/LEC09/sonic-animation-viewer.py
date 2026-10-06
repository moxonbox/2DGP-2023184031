"""Play the irregular Classic Sonic sprite sheet with pico2d."""

from pathlib import Path

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
IMAGE_PATH = Path(__file__).resolve().with_name('sonic-sprite.png')

# Frames: left, top, width, height, anchor_x, anchor_y (top-left origin).
ACTIONS = [
    {'id': 'action_01', 'fps': 6, 'frames': [
        (1, 39, 29, 39, 14.5, 39),
        (31, 40, 26, 38, 13, 38),
        (58, 39, 29, 39, 14.5, 39),
        (87, 40, 29, 38, 14.5, 38),
        (118, 40, 30, 38, 15, 38),
        (150, 40, 30, 38, 15, 38),
        (182, 40, 28, 38, 14, 38),
    ]},
]


def main():
    import pico2d

    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    image = pico2d.load_image(str(IMAGE_PATH))
    print(f'Sprite sheet: {image.w} x {image.h}')
    pico2d.close_canvas()


if __name__ == '__main__':
    main()
