"""Play the irregular Classic Sonic sprite sheet with pico2d."""

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


def main():
    import pico2d

    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    pico2d.close_canvas()


if __name__ == '__main__':
    main()
