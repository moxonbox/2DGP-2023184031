"""LEC 08: pico2d sprite animation viewer."""

from ctypes import byref, c_int
from pathlib import Path
from time import perf_counter

from pico2d import pico2d

FRAME_SIZE = 128
FRAMES_PER_SECOND = 10
REPETITIONS = 5
PAUSE_SECONDS = 1.0


def grid_frames(row, count):
    """Return top-left rectangles for a row of the regular samurai sheet."""
    return tuple((column * FRAME_SIZE, row * FRAME_SIZE, FRAME_SIZE, FRAME_SIZE)
                 for column in range(count))


# (name, image filename, ((left, top, width, height), ...))
# Each action owns its frames; their sizes and counts can differ.
ANIMATIONS = (
    ("걷기", "SamuraiSheet.png", grid_frames(1, 8)),
    ("뛰기", "SamuraiSheet.png", grid_frames(2, 8)),
    ("점프", "SamuraiSheet.png", grid_frames(3, 12)),
    ("공격", "SamuraiSheet.png", grid_frames(4, 6)),
)


def load_sprites():
    return {filename: pico2d.load_image(str(Path(__file__).with_name(filename)))
            for filename in sorted({filename for _, filename, _ in ANIMATIONS})}


def frame_rectangle(action, frame, sheet_height):
    """Convert a frame's top-left rectangle to pico2d's bottom-left coordinates."""
    left, top, width, height = ANIMATIONS[action][2][frame]
    return left, sheet_height - top - height, width, height


def animation_at(elapsed):
    """Return the action, frame and pause state at an elapsed time."""
    durations = tuple(len(frames) * REPETITIONS / FRAMES_PER_SECOND + PAUSE_SECONDS
                      for _, _, frames in ANIMATIONS)
    elapsed %= sum(durations)
    for action, duration in enumerate(durations):
        if elapsed < duration:
            frame_count = len(ANIMATIONS[action][2])
            play_seconds = duration - PAUSE_SECONDS
            frame = min(int(elapsed * FRAMES_PER_SECOND),
                        frame_count * REPETITIONS - 1)
            return action, frame % frame_count, elapsed >= play_seconds
        elapsed -= duration


def draw_frame(sheet, action, frame, width, height):
    frames = ANIMATIONS[action][2]
    # Share one scale across an action so different frame sizes do not pulsate.
    scale = min(width / max(rect[2] for rect in frames),
                height / max(rect[3] for rect in frames)) / 2
    rectangle = frame_rectangle(action, frame, sheet.h)
    sheet.clip_draw(*rectangle, width / 2, height / 2,
                    rectangle[2] * scale, rectangle[3] * scale)


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
        sheets = load_sprites()
        started = perf_counter()
        while handle_events():
            width, height = get_viewport()
            action, frame, paused = animation_at(perf_counter() - started)
            state = "정지 (1초)" if paused else "재생 중"
            title = f"애니메이션 뷰어 - {ANIMATIONS[action][0]} - {state}"
            pico2d.SDL_SetWindowTitle(pico2d.window, title.encode("utf-8"))
            pico2d.clear_canvas()
            draw_frame(sheets[ANIMATIONS[action][1]], action, frame, width, height)
            pico2d.update_canvas()
            # Keep processing input during the one-second animation pause.
            pico2d.delay(0.01)
    finally:
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
