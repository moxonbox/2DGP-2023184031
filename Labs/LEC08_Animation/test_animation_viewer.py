"""Run with Python; add --smoke to check the installed pico2d/SDL renderer."""

from ctypes import byref
from math import isclose
from pathlib import Path
from struct import unpack
from types import SimpleNamespace
from unittest.mock import Mock, patch
import sys

import animation_viewer as viewer


def png_size(filename):
    with Path(__file__).with_name(filename).open("rb") as image:
        header = image.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    return unpack(">II", header[16:24])


def check_animation():
    # Check every frame of five repetitions, then both edges of each pause.
    start = 0
    assert len({len(frames) for _, _, frames in viewer.ANIMATIONS}) > 1
    for action, (_, _, frames) in enumerate(viewer.ANIMATIONS):
        count = len(frames)
        assert count > 0
        for repeat in range(5):
            for frame in range(count):
                elapsed = start + (repeat * count + frame + 0.5) / 10
                assert viewer.animation_at(elapsed) == (action, frame, False)
        pause = start + count * 5 / 10
        assert viewer.animation_at(pause - 0.001) == (action, count - 1, False)
        assert viewer.animation_at(pause) == (action, count - 1, True)
        assert viewer.animation_at(pause + 0.999) == (action, count - 1, True)
        assert viewer.animation_at(pause + 1) == ((action + 1) % len(viewer.ANIMATIONS), 0, False)
        start = pause + 1
    # Large elapsed times must wrap directly, without replaying stale frames.
    assert viewer.animation_at(start * 1000) == (0, 0, False)
    assert viewer.animation_at(start * 1001 - 0.5) == (action, count - 1, True)

    dimensions = {filename: png_size(filename) for _, filename, _ in viewer.ANIMATIONS}
    for action, (_, filename, frames) in enumerate(viewer.ANIMATIONS):
        sheet_width, sheet_height = dimensions[filename]
        for frame in range(len(frames)):
            left, bottom, width, height = viewer.frame_rectangle(action, frame, sheet_height)
            assert 0 <= left < left + width <= sheet_width
            assert 0 <= bottom < bottom + height <= sheet_height
    sonic = next(i for i, action in enumerate(viewer.ANIMATIONS) if action[0] == "소닉 회전 점프")
    assert viewer.frame_rectangle(sonic, 0, 525) == (1, 326, 29, 30)

    # Every action keeps one scale, its aspect ratio, center and half-viewport bounds.
    for action, (_, filename, frames) in enumerate(viewer.ANIMATIONS):
        sheet = SimpleNamespace(h=dimensions[filename][1], clip_draw=Mock())
        for viewport_width, viewport_height in ((800, 600), (1200, 400), (400, 1000), (1, 1)):
            previous_scale = None
            largest_width = largest_height = 0
            for frame, (_, _, source_width, source_height) in enumerate(frames):
                viewer.draw_frame(sheet, action, frame, viewport_width, viewport_height)
                _, _, _, _, x, y, width, height = sheet.clip_draw.call_args.args
                assert (x, y) == (viewport_width / 2, viewport_height / 2)
                assert 0 < width <= viewport_width / 2 + 1e-8
                assert 0 < height <= viewport_height / 2 + 1e-8
                scale = width / source_width
                assert isclose(scale, height / source_height)
                assert previous_scale is None or isclose(scale, previous_scale)
                previous_scale = scale
                largest_width, largest_height = max(largest_width, width), max(largest_height, height)
            assert isclose(largest_width, viewport_width / 2) or isclose(largest_height, viewport_height / 2)

    pico2d = viewer.pico2d
    for events, running in (([], True),
                            ([SimpleNamespace(type=pico2d.SDL_QUIT)], False),
                            ([SimpleNamespace(type=pico2d.SDL_KEYDOWN,
                                              key=pico2d.SDLK_ESCAPE)], False),
                            ([SimpleNamespace(type=pico2d.SDL_KEYDOWN,
                                              key=pico2d.SDLK_SPACE)], True)):
        with patch.object(pico2d, "get_events", return_value=events):
            assert viewer.handle_events() is running
    print(f"PASS: {len(viewer.ANIMATIONS)} actions, five repeats, pauses, irregular sizing, exit")


def check_renderer():
    pico2d = viewer.pico2d
    pico2d.open_canvas(800, 600)
    try:
        pico2d.SDL_HideWindow(pico2d.window)
        pico2d.SDL_SetWindowResizable(pico2d.window, pico2d.SDL_TRUE)
        assert pico2d.SDL_GetWindowFlags(pico2d.window) & pico2d.SDL_WINDOW_RESIZABLE
        sheets = viewer.load_sprites()
        for filename, sheet in sheets.items():
            assert (sheet.w, sheet.h) == png_size(filename)
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
