"""LEC 08: pico2d sprite animation viewer."""

from ctypes import byref, c_int
from pathlib import Path
from time import perf_counter

from pico2d import pico2d

FRAME_SIZE = 128
FRAMES_PER_SECOND = 10
REPETITIONS = 5
PAUSE_SECONDS = 1.0
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
    durations = tuple(count * REPETITIONS / FRAMES_PER_SECOND + PAUSE_SECONDS
                      for _, _, count in ANIMATIONS)
    elapsed %= sum(durations)
    for action, duration in enumerate(durations):
        if elapsed < duration:
            frame_count = ANIMATIONS[action][2]
            play_seconds = duration - PAUSE_SECONDS
            frame = min(int(elapsed * FRAMES_PER_SECOND),
                        frame_count * REPETITIONS - 1)
            return action, frame % frame_count, elapsed >= play_seconds
        elapsed -= duration


def draw_frame(sheet, action, frame, width, height):
    # Fit the square sprite frame inside half the viewport without stretching.
    size = min(width, height) / 2
    sheet.clip_draw(*frame_rectangle(action, frame, sheet.h),
                    width / 2, height / 2, size, size)


def handle_events():
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            return False
        if event.type == pico2d.SDL_KEYDOWN and event.key == pico2d.SDLK_ESCAPE:
            return False
    return True


def get_viewport():
    # pico2d.get_events() discards SDL window resize events, so read the size.
    width, height = c_int(), c_int()
    pico2d.SDL_GetWindowSize(pico2d.window, byref(width), byref(height))
    width, height = max(1, width.value), max(1, height.value)
    if (width, height) != (pico2d.get_canvas_width(), pico2d.get_canvas_height()):
        pico2d.resize_canvas(width, height)
    return width, height


def main():
    pico2d.open_canvas(800, 600)
    try:
        pico2d.SDL_SetWindowResizable(pico2d.window, pico2d.SDL_TRUE)
        sheet = load_sprite()
        started = perf_counter()
        while handle_events():
            width, height = get_viewport()
            action, frame, paused = animation_at(perf_counter() - started)
            pico2d.clear_canvas()
            draw_frame(sheet, action, frame, width, height)
            pico2d.update_canvas()
            # Keep processing input during the one-second animation pause.
            pico2d.delay(0.01)
    finally:
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
