"""Run with Python; add --smoke to check the installed pico2d/SDL renderer."""

from ctypes import byref
from types import SimpleNamespace
from unittest.mock import Mock, patch
import sys

import animation_viewer as viewer


def check_animation():
    # Check every frame of five repetitions, then both edges of each pause.
    for action, start, count in ((0, 0, 8), (1, 5, 8), (2, 10, 12), (3, 17, 6)):
        for repeat in range(5):
            for frame in range(count):
                elapsed = start + (repeat * count + frame + 0.5) / 10
                assert viewer.animation_at(elapsed) == (action, frame, False)
        pause = start + count * 5 / 10
        assert viewer.animation_at(pause - 0.001) == (action, count - 1, False)
        assert viewer.animation_at(pause) == (action, count - 1, True)
        assert viewer.animation_at(pause + 0.999) == (action, count - 1, True)
        assert viewer.animation_at(pause + 1) == ((action + 1) % 4, 0, False)
    # Large elapsed times must wrap directly, without replaying stale frames.
    assert viewer.animation_at(21 * 1000) == (0, 0, False)
    assert viewer.animation_at(21 * 1000 + 20.5) == (3, 5, True)

    sheet = SimpleNamespace(h=1280, clip_draw=Mock())
    for width, height, size in ((800, 600, 300), (1200, 400, 200),
                                (400, 1000, 200), (1, 1, 0.5)):
        viewer.draw_frame(sheet, 3, 5, width, height)
        sheet.clip_draw.assert_called_with(640, 640, 128, 128,
                                           width / 2, height / 2, size, size)
    for action, count in enumerate((8, 8, 12, 6)):
        for frame in range(count):
            left, bottom, width, height = viewer.frame_rectangle(action, frame, 1280)
            assert 0 <= left < left + width <= 1536
            assert 0 <= bottom < bottom + height <= 1280

    pico2d = viewer.pico2d
    for events, running in (([], True),
                            ([SimpleNamespace(type=pico2d.SDL_QUIT)], False),
                            ([SimpleNamespace(type=pico2d.SDL_KEYDOWN,
                                              key=pico2d.SDLK_ESCAPE)], False),
                            ([SimpleNamespace(type=pico2d.SDL_KEYDOWN,
                                              key=pico2d.SDLK_SPACE)], True)):
        with patch.object(pico2d, "get_events", return_value=events):
            assert viewer.handle_events() is running
    print("PASS: five repeats, pause boundaries, wraparound, clipping, sizing, exit")


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
