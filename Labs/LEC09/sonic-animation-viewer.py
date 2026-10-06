"""Play the irregular Classic Sonic sprite sheet with pico2d."""

from pathlib import Path

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
IMAGE_PATH = Path(__file__).resolve().with_name('sonic-sprite.png')


def main():
    import pico2d

    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    image = pico2d.load_image(str(IMAGE_PATH))
    print(f'Sprite sheet: {image.w} x {image.h}')
    pico2d.close_canvas()


if __name__ == '__main__':
    main()
