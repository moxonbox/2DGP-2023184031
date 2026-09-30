"""Run with Python; add --smoke to check the installed pico2d/SDL renderer."""

from ctypes import byref
from math import isclose
from types import SimpleNamespace
from unittest.mock import Mock, patch
import sys

import animation_viewer as viewer


def check_animation():
    # Check every frame of five repetitions, then both edges of each pause.
    cases = ((0, 0, 8), (1, 5, 8), (2, 10, 12), (3, 17, 6),
             (4, 21, 9), (5, 26.5, 6), (6, 30.5, 8), (7, 35.5, 2))
    assert len(viewer.ANIMATIONS) == len(cases)
    for action, start, count in cases:
        assert len(viewer.ANIMATIONS[action][2]) == count
        for repeat in range(5):
            for frame in range(count):
                elapsed = start + (repeat * count + frame + 0.5) / 10
                assert viewer.animation_at(elapsed) == (action, frame, False)
        pause = start + count * 5 / 10
        assert viewer.animation_at(pause - 0.001) == (action, count - 1, False)
        assert viewer.animation_at(pause) == (action, count - 1, True)
        assert viewer.animation_at(pause + 0.999) == (action, count - 1, True)
        assert viewer.animation_at(pause + 1) == ((action + 1) % len(cases), 0, False)
    # Large elapsed times must wrap directly, without replaying stale frames.
    assert viewer.animation_at(37.5 * 1000) == (0, 0, False)
    assert viewer.animation_at(37.5 * 1000 + 37) == (7, 1, True)

    sheet = SimpleNamespace(h=1280, clip_draw=Mock())
    for width, height, size in ((800, 600, 300), (1200, 400, 200),
                                (400, 1000, 200), (1, 1, 0.5)):
        viewer.draw_frame(sheet, 3, 5, width, height)
        sheet.clip_draw.assert_called_with(640, 640, 128, 128,
                                           width / 2, height / 2, size, size)
    dimensions = {"SamuraiSheet.png": (1536, 1280), "sonic-sprite.png": (399, 525)}
    for action, (_, filename, frames) in enumerate(viewer.ANIMATIONS):
        sheet_width, sheet_height = dimensions[filename]
        for frame in range(len(frames)):
            left, bottom, width, height = viewer.frame_rectangle(action, frame, sheet_height)
            assert 0 <= left < left + width <= sheet_width
            assert 0 <= bottom < bottom + height <= sheet_height
    assert viewer.frame_rectangle(4, 0, 525) == (1, 326, 29, 30)

    # Irregular frames keep their aspect ratio and a shared scale within an action.
    sheet.h = 525
    previous_scale = None
    for frame, (_, _, source_width, source_height) in enumerate(viewer.ANIMATIONS[6][2]):
        viewer.draw_frame(sheet, 6, frame, 800, 600)
        _, _, _, _, x, y, width, height = sheet.clip_draw.call_args.args
        assert (x, y) == (400, 300)
        assert 0 < width <= 400 and 0 < height <= 300
        scale = width / source_width
        assert isclose(scale, height / source_height)
        assert previous_scale is None or isclose(scale, previous_scale)
        previous_scale = scale

    pico2d = viewer.pico2d
    for events, running in (([], True),
                            ([SimpleNamespace(type=pico2d.SDL_QUIT)], False),
                            ([SimpleNamespace(type=pico2d.SDL_KEYDOWN,
                                              key=pico2d.SDLK_ESCAPE)], False),
                            ([SimpleNamespace(type=pico2d.SDL_KEYDOWN,
                                              key=pico2d.SDLK_SPACE)], True)):
        with patch.object(pico2d, "get_events", return_value=events):
            assert viewer.handle_events() is running
    print("PASS: 8 actions, unequal frame counts, five repeats, pauses, irregular sizing, exit")


def check_renderer():
    pico2d = viewer.pico2d
    pico2d.open_canvas(800, 600)
    try:
        pico2d.SDL_HideWindow(pico2d.window)
        pico2d.SDL_SetWindowResizable(pico2d.window, pico2d.SDL_TRUE)
        assert pico2d.SDL_GetWindowFlags(pico2d.window) & pico2d.SDL_WINDOW_RESIZABLE
        sheets = viewer.load_sprites()
        sheet = sheets["SamuraiSheet.png"]
        assert (sheet.w, sheet.h) == (1536, 1280)
        assert (sheets["sonic-sprite.png"].w, sheets["sonic-sprite.png"].h) == (399, 525)
        for width, height in ((800, 600), (1200, 400), (400, 1000)):
            pico2d.SDL_SetWindowSize(pico2d.window, width, height)
            pico2d.get_events()
            assert viewer.get_viewport() == (width, height)
            assert (pico2d.get_canvas_width(), pico2d.get_canvas_height()) == (width, height)
            for action, (_, filename, frames) in enumerate(viewer.ANIMATIONS):
                for frame in range(len(frames)):
                    pico2d.clear_canvas()
                    viewer.draw_frame(sheets[filename], action, frame, width, height)
                    pico2d.update_canvas()
        event = pico2d.SDL_Event()
        event.type = pico2d.SDL_QUIT
        assert pico2d.SDL_PushEvent(byref(event)) == 1
        assert not viewer.handle_events()
    finally:
        pico2d.close_canvas()
    print("PASS: PNG loading, native resizing, all sprite frames, SDL quit event")


if __name__ == "__main__":
    check_animation()
    if "--smoke" in sys.argv:
        check_renderer()
