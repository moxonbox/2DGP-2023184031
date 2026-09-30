"""LEC 08: pico2d sprite animation viewer."""

from pathlib import Path

from pico2d import pico2d

FRAME_SIZE = 128
# (name, row from the top, frame count)
ANIMATIONS = (
    ("Walk", 1, 8),
)


def load_sprite():
    return pico2d.load_image(str(Path(__file__).with_name("SamuraiSheet.png")))


def main():
    pico2d.open_canvas(800, 600)
    pico2d.close_canvas()


if __name__ == "__main__":
    main()
