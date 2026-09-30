"""LEC 08: pico2d sprite animation viewer."""

from pathlib import Path

from pico2d import pico2d

FRAME_SIZE = 128
FRAMES_PER_SECOND = 10
# (name, row from the top, frame count)
ANIMATIONS = (
    ("Walk", 1, 8),
    ("Run", 2, 8),
    ("Jump", 3, 12),
    ("Attack", 4, 6),
)


def load_sprite():
    return pico2d.load_image(str(Path(__file__).with_name("SamuraiSheet.png")))


def frame_rectangle(action, frame, sheet_height):
    """Convert a top-down sheet row to pico2d's bottom-left coordinates."""
    row = ANIMATIONS[action][1]
    return (frame * FRAME_SIZE, sheet_height - (row + 1) * FRAME_SIZE,
            FRAME_SIZE, FRAME_SIZE)


def animation_at(elapsed):
    """Return the action, frame and pause state at an elapsed time."""
    frame_count = ANIMATIONS[0][2]
    return 0, int(elapsed * FRAMES_PER_SECOND) % frame_count, False


def draw_frame(sheet, action, frame, width, height):
    # Fit the square sprite frame inside half the viewport without stretching.
    size = min(width, height) / 2
    sheet.clip_draw(*frame_rectangle(action, frame, sheet.h),
                    width / 2, height / 2, size, size)


def main():
    pico2d.open_canvas(800, 600)
    sheet = load_sprite()
    pico2d.clear_canvas()
    draw_frame(sheet, 0, 0, 800, 600)
    pico2d.update_canvas()
    pico2d.close_canvas()


if __name__ == "__main__":
    main()
