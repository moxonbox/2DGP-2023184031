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
    ("GPT 로봇 대기", "gpt_robot_sheet.png", (
        (61, 10, 135, 166), (246, 22, 133, 155),
        (426, 22, 128, 155), (619, 14, 133, 163),
    )),
    ("GPT 로봇 걷기", "gpt_robot_sheet.png", (
        (59, 188, 141, 156), (263, 187, 145, 159), (475, 185, 143, 162),
        (677, 184, 135, 162), (869, 184, 143, 163), (1066, 186, 143, 161),
    )),
    ("GPT 로봇 뛰기", "gpt_robot_sheet.png", (
        (71, 355, 168, 156), (300, 357, 170, 158), (516, 354, 176, 152),
        (748, 353, 169, 162), (959, 355, 169, 160),
    )),
    ("걷기", "SamuraiSheet.png", grid_frames(1, 8)),
    ("뛰기", "SamuraiSheet.png", grid_frames(2, 8)),
    ("점프", "SamuraiSheet.png", grid_frames(3, 12)),
    ("공격", "SamuraiSheet.png", grid_frames(4, 6)),
    ("소닉 회전 점프", "sonic-sprite.png", (
        (1, 169, 29, 30), (35, 167, 29, 31), (67, 169, 30, 29),
        (98, 169, 31, 29), (131, 168, 29, 30), (162, 168, 29, 31),
        (193, 170, 30, 29), (230, 170, 31, 29), (268, 170, 30, 30),
    )),
    ("소닉 구르기", "sonic-sprite.png", (
        (1, 206, 30, 27), (36, 206, 29, 27), (70, 206, 29, 27),
        (105, 206, 29, 27), (139, 206, 29, 27), (174, 206, 29, 27),
    )),
    ("소닉 공중 회전", "sonic-sprite.png", (
        (1, 379, 27, 38), (31, 379, 31, 36), (64, 379, 31, 36),
        (99, 377, 33, 38), (136, 379, 32, 36), (176, 379, 33, 36),
        (217, 379, 33, 36), (254, 378, 33, 36),
    )),
    ("소닉 승리", "sonic-sprite.png", (
        (96, 427, 23, 39), (125, 427, 23, 39),
    )),
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
