"""Default: headless tests. --gui: optional native pico2d/SDL checks."""

import io
import math
from pathlib import Path
import runpy
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

viewer = runpy.run_path(str(Path(__file__).with_name('sonic-animation-viewer.py')))
ACTIONS = viewer['ACTIONS']
Player = viewer['Player']
validate = viewer['validate_actions']
layout = viewer['action_layout']
FRAME = (0, 0, 10, 20, 5, 20)


def fake_pico(events=()):
    image = SimpleNamespace(w=399, h=525, clip_draw=Mock())
    return SimpleNamespace(
        open_canvas=Mock(), close_canvas=Mock(), window=object(), renderer=object(),
        load_image=Mock(return_value=image), clear_canvas=Mock(), update_canvas=Mock(), hide_lattice=Mock(),
        get_events=Mock(return_value=list(events)), SDL_GetWindowFlags=Mock(return_value=0),
        SDL_SetWindowTitle=Mock(),
        SDL_WINDOW_MINIMIZED=4, SDL_QUIT=1, SDL_KEYDOWN=2, SDLK_ESCAPE=27,
    )


class ViewerTests(unittest.TestCase):
    def test_all_data_and_invalid_values(self):
        validate(ACTIONS, 399, 525)
        self.assertEqual([len(a['frames']) for a in ACTIONS], [11, 12, 6, 9, 6, 6, 6, 6, 2, 8, 2, 2])
        self.assertEqual(sum(len(a['frames']) for a in ACTIONS), 76)
        self.assertEqual([i for i,a in enumerate(ACTIONS, 1) if a.get('move')], [2, 3, 4, 5, 6, 7])
        for fps in (0, -1, 61, math.inf, math.nan, True, '12'):
            with self.subTest(fps=fps), self.assertRaisesRegex(ValueError, 'action_01'):
                validate([{'id': 'action_01', 'fps': fps, 'frames': [FRAME]}], 399, 525)
        for move in (1, None, 'yes'):
            with self.subTest(move=move), self.assertRaisesRegex(ValueError, 'move'):
                validate([{'id': 'action_01', 'move': move, 'frames': [FRAME]}], 399, 525)
        for speed in (0, -1, True, '120', math.inf, math.nan):
            with self.subTest(speed=speed), self.assertRaisesRegex(ValueError, 'speed'):
                validate([{'id': 'action_01', 'speed': speed, 'frames': [FRAME]}], 399, 525)
        bad_frames = [(-1, 0, 10, 20, 5, 20), (390, 0, 10, 20, 5, 20),
                      (0, 520, 10, 20, 5, 20), (0, 0, 0, 20, 0, 20),
                      (0.5, 0, 10, 20, 5, 20), (0, 0, 10, 20, math.nan, 20),
                      (0, 0, 10, 20, 11, 20), (0, 0, 10, 20, 5, 21), (0, 0),
                      None, 42, '123456', {'x': 1}]
        for frame in bad_frames:
            with self.subTest(frame=frame), self.assertRaisesRegex(ValueError, 'action_01 프레임 1'):
                validate([{'id': 'action_01', 'frames': [frame]}], 399, 525)
        for data in ([], [{'id': 'empty', 'frames': []}],
                     [{'id': 'same', 'frames': [FRAME]}] * 2):
            with self.assertRaises(ValueError):
                validate(data, 399, 525)

    def test_bounds_scale_center_and_source_coordinates(self):
        pico = fake_pico()
        for action in ACTIONS:
            projected = []
            scale, ox, oy = layout(action)
            for frame in action['frames']:
                left, top, width, height, ax, ay = frame
                viewer['draw_frame'](pico, pico.load_image.return_value, frame, (scale, ox, oy))
                args = pico.load_image.return_value.clip_draw.call_args.args
                self.assertEqual(args[:4], (left, 525 - top - height, width, height))
                x, y, w, h = args[4:]
                self.assertAlmostEqual(w / h, width / height)
                projected.append((x - w/2, x + w/2, y - h/2, y + h/2))
            xmin = min(f[0] for f in projected)
            xmax = max(f[1] for f in projected)
            ymin = min(f[2] for f in projected)
            ymax = max(f[3] for f in projected)
            self.assertAlmostEqual(max(xmax - xmin, ymax - ymin), 200)
            self.assertAlmostEqual((xmin + xmax)/2, 400)
            self.assertAlmostEqual((ymin + ymax)/2, 300)
        for top in (0, 505):
            frame = (0, top, 10, 20, 5, 20)
            viewer['draw_frame'](pico, pico.load_image.return_value, frame, (1, 400, 300))
            self.assertEqual(pico.load_image.return_value.clip_draw.call_args.args[1], 505 - top)

    def test_fps_last_frame_wait_and_wrap(self):
        actions = [{'id': 'single', 'frames': [FRAME]},
                   {'id': 'multiple', 'fps': 10, 'frames': [FRAME] * 3}]
        player = Player(actions)
        for loop in range(3):
            player.update(1/12 - 0.001)
            self.assertFalse(player.waiting)
            player.update(0.001)
            self.assertEqual(player.completed_loops, loop + 1)
            self.assertEqual(player.waiting, loop == 2)
        player.update(0.5)
        player.update(0.499)
        self.assertEqual(player.action_index, 0)
        player.update(0.001)
        self.assertEqual((player.action_index, player.frame_index, player.waiting), (1, 0, False))
        for loop in range(3):
            player.update(0.1)
            player.update(0.1)
            self.assertEqual(player.frame_index, 2)
            self.assertFalse(player.waiting)
            player.update(0.099)
            self.assertFalse(player.waiting)
            player.update(0.001)
            self.assertEqual(player.completed_loops, loop + 1)
            self.assertEqual(player.waiting, loop == 2)
        player.update(0.5)
        player.update(0.5)
        self.assertEqual((player.action_index, player.frame_index, player.waiting), (0, 0, False))

    def test_slow_render_stall_and_pause_preserve_frames(self):
        player = Player([{'id': 'test', 'fps': 12, 'frames': [FRAME] * 4}])
        player.update(0.4)
        self.assertEqual(player.frame_index, 1)
        self.assertGreater(player.elapsed, 0.3)  # Normal elapsed time is not clamped.
        player.update(0)
        self.assertEqual(player.frame_index, 2)
        state = (player.frame_index, player.elapsed, player.waiting)
        player.update(0.500001)
        self.assertEqual((player.frame_index, player.elapsed, player.waiting), state)
        player.paused = True
        player.update(0.2)
        self.assertEqual((player.frame_index, player.elapsed, player.waiting), state)
        player.paused = False
        player.update(0)
        self.assertEqual(player.frame_index, 3)
        self.assertEqual(player.elapsed, 0)
        player.update(1/12)
        self.assertEqual(player.completed_loops, 1)
        self.assertFalse(player.waiting)
        for _ in range(8):
            player.update(1/12)
        self.assertTrue(player.waiting)
        player.update(0.6)
        self.assertEqual(player.elapsed, 0)
        player.paused = True
        player.update(0.5)
        self.assertEqual(player.elapsed, 0)
        player.paused = False
        player.update(0.5)  # Threshold itself is an ordinary update.
        self.assertEqual(player.elapsed, 0.5)
        for dt in (-1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                player.update(dt)

    def test_two_complete_cycles_show_every_frame(self):
        player = Player(ACTIONS)
        seen = [(0, 0)]
        cycles = 0
        for _ in range(10000):
            before = player.action_index
            old = (player.action_index, player.frame_index, player.completed_loops)
            player.update(1/60)
            position = (player.action_index, player.frame_index)
            if (not player.moving and not player.waiting
                    and (player.action_index, player.frame_index, player.completed_loops) != old):
                seen.append(position)
            if before == len(ACTIONS) - 1 and player.action_index == 0:
                cycles += 1
                if cycles == 2:
                    break
        expected = [(i, j) for i, action in enumerate(ACTIONS) for _ in range(3)
                    for j in range(len(action['frames']))]
        self.assertEqual(cycles, 2)
        self.assertEqual(seen, expected * 2 + [(0, 0)])

    def test_three_loops_then_one_way_motion_and_wait(self):
        actions = [{'id': 'moving', 'move': True, 'frames': [FRAME]},
                   {'id': 'still', 'frames': [FRAME]}]
        player = Player(actions)
        for loop in range(3):
            self.assertEqual(player.horizontal_offset, 0)
            player.update(1/12)
            self.assertEqual(player.completed_loops, loop + 1)
            self.assertEqual(player.moving, loop == 2)
            self.assertFalse(player.waiting)
        limit = player.motion_limits[0]
        self.assertEqual(player.horizontal_offset, -limit)
        state = (player.frame_index, player.elapsed, player.horizontal_offset)
        player.paused = True
        player.update(0.2)
        player.paused = False
        player.update(0.501)
        self.assertEqual((player.frame_index, player.elapsed, player.horizontal_offset), state)
        for step in range(7):  # 700px at 200px/s: 3.5 active seconds.
            old_offset = player.horizontal_offset
            player.update(0.5)
            self.assertGreater(player.horizontal_offset, old_offset)
            self.assertLessEqual(player.horizontal_offset, limit)
            self.assertEqual(player.waiting, step == 6)
            self.assertEqual(player.completed_loops, 3)
        self.assertEqual(player.horizontal_offset, limit)
        self.assertFalse(player.moving)
        player.update(0.5)
        player.update(0.499)
        self.assertEqual(player.action_index, 0)
        player.update(0.001)
        self.assertEqual((player.action_index, player.horizontal_offset, player.completed_loops), (1, 0, 0))
        moving = Player([{'id': 'animated', 'move': True, 'frames': [FRAME] * 3}])
        for _ in range(9):
            moving.update(1/12)
        self.assertTrue(moving.moving)
        self.assertEqual(moving.frame_index, 0)
        for expected_frame in (1, 2, 0):
            old_offset = moving.horizontal_offset
            moving.update(1/12)
            self.assertEqual(moving.frame_index, expected_frame)
            self.assertAlmostEqual(moving.horizontal_offset-old_offset, 200/12)
            self.assertEqual(moving.completed_loops, 3)

    def test_all_motion_endpoints_keep_sprite_inside_viewport(self):
        player = Player(ACTIONS)
        pico = fake_pico()
        for index, action in enumerate(ACTIONS):
            if not action.get('move'):
                continue
            limit = player.motion_limits[index]
            for offset in (-limit, limit):
                edges = []
                for frame in action['frames']:
                    viewer['draw_frame'](pico, pico.load_image.return_value, frame,
                                         player.layouts[index], offset)
                    x, y, w, h = pico.load_image.return_value.clip_draw.call_args.args[4:]
                    self.assertGreaterEqual(x-w/2, -1e-9)
                    self.assertLessEqual(x+w/2, 800+1e-9)
                    edges.append((x-w/2, x+w/2))
                if offset < 0:
                    self.assertAlmostEqual(min(edge[0] for edge in edges), 0)
                else:
                    self.assertAlmostEqual(max(edge[1] for edge in edges), 800)

    def test_timing_error_at_different_render_rates(self):
        # Full final-frame intervals take priority; rounding may add at most
        # two render ticks per loop when render FPS is above animation FPS.
        for source in ACTIONS:
            action = dict(source, move=False)
            expected = 3 * len(action['frames']) / action.get('fps', 12)
            for render_fps in (30, 60, 144):
                with self.subTest(action=action['id'], render_fps=render_fps):
                    player = Player([action])
                    ticks = 0
                    while not player.waiting and ticks < 10000:
                        player.update(1/render_fps)
                        ticks += 1
                    self.assertTrue(player.waiting)
                    actual = ticks / render_fps
                    self.assertGreaterEqual(actual + 1e-9, expected)
                    self.assertLessEqual(actual - expected, 6/render_fps + 1e-9)

    def test_action_speed_and_playback_title(self):
        for action in ACTIONS:
            if not action.get('move'):
                continue
            player = Player([action])
            player.completed_loops = 3
            player.moving = True
            player.horizontal_offset = -player.motion_limits[0]
            start = player.horizontal_offset
            player.update(0.1)
            self.assertAlmostEqual(player.horizontal_offset-start, action.get('speed', 200) * 0.1)
        player = Player([{'id': 'test', 'frames': [FRAME]}])
        self.assertIn('test | 1/3 | 재생', viewer['playback_title'](player))
        player.completed_loops = 3
        player.moving = True
        self.assertIn('3/3 | 이동', viewer['playback_title'](player))
        player.moving = False
        player.waiting = True
        player.paused = True
        self.assertIn('3/3 | 대기 (일시정지)', viewer['playback_title'](player))

    def test_exit_and_cleanup_on_errors(self):
        for event in (SimpleNamespace(type=1), SimpleNamespace(type=2, key=27)):
            pico = fake_pico([event])
            viewer['run_viewer'](pico)
            pico.close_canvas.assert_called_once()
        pico = fake_pico()
        pico.load_image.side_effect = OSError('missing')
        with self.assertRaisesRegex(OSError, 'missing-sheet.png'):
            viewer['run_viewer'](pico, Path('missing-sheet.png'))
        pico.close_canvas.assert_called_once()
        pico = fake_pico()
        pico.open_canvas.side_effect = RuntimeError('open failure')
        with self.assertRaisesRegex(RuntimeError, 'open failure'):
            viewer['run_viewer'](pico)
        pico.close_canvas.assert_called_once()
        pico = fake_pico()
        pico.get_events.side_effect = RuntimeError('event failure')
        with self.assertRaisesRegex(RuntimeError, 'event failure'):
            viewer['run_viewer'](pico)
        pico.close_canvas.assert_called_once()
        with patch.dict('sys.modules', {'pico2d': None}), patch('sys.stderr', new_callable=io.StringIO) as error:
            self.assertEqual(viewer['main'](), 1)
            self.assertIn('pico2d', error.getvalue())

    def test_minimize_restore_in_render_loop(self):
        pico = fake_pico()
        pico.SDL_GetWindowFlags.side_effect = [0, 4, 4, 0]
        pico.get_events.side_effect = [[], [], [], [], [SimpleNamespace(type=1)]]
        with patch('time.sleep'):
            viewer['run_viewer'](pico)
        self.assertEqual(pico.update_canvas.call_count, 2)
        self.assertEqual(pico.SDL_SetWindowTitle.call_count, 4)
        self.assertIn('일시정지'.encode('utf-8'), pico.SDL_SetWindowTitle.call_args_list[1].args[1])
        pico.close_canvas.assert_called_once()


def run_gui_checks():
    """Use the real event/render loop; takes roughly two minutes on Windows."""
    import ctypes
    import pico2d.pico2d as pico

    globals_ = viewer['run_viewer'].__globals__
    original_player = globals_['Player']
    original_draw = globals_['draw_frame']
    original_events = pico.get_events
    trace = {'cycles': 0, 'seen': [(0, 0)], 'moves': [], 'waits': [],
             'pause_phase': 0, 'max_dt': 1/60, 'title_phases': set(), 'exit_events': []}
    started = time.perf_counter()

    class TrackedPlayer(original_player):
        def __init__(self, actions):
            super().__init__(actions)
            trace['player'] = self

        def update(self, dt):
            old = (self.action_index, self.frame_index, self.completed_loops)
            was_moving, was_waiting = self.moving, self.waiting
            old_offset = self.horizontal_offset
            super().update(dt)
            if dt <= viewer['STALL_SECONDS']:
                trace['max_dt'] = max(trace['max_dt'], dt)
            if (not self.moving and not self.waiting
                    and (self.action_index, self.frame_index, self.completed_loops) != old):
                trace['seen'].append((self.action_index, self.frame_index))
            if not was_moving and self.moving:
                assert self.completed_loops == 3
                assert self.horizontal_offset == -self.motion_limits[self.action_index]
            if was_moving:
                assert self.horizontal_offset >= old_offset
                if not self.paused and dt <= viewer['STALL_SECONDS']:
                    expected = min(self.motion_limits[self.action_index],
                                   old_offset + self.action.get('speed', 200) * dt)
                    assert abs(self.horizontal_offset - expected) < 1e-7
            if not was_waiting and self.waiting:
                assert self.completed_loops == 3
                trace['wait_start'] = time.perf_counter()
                if was_moving:
                    assert self.horizontal_offset == self.motion_limits[self.action_index]
                    trace['moves'].append(self.action_index + 1)
            if old[0] != self.action_index:
                trace['waits'].append(time.perf_counter() - trace['wait_start'])
            if old[0] == len(self.actions)-1 and self.action_index == 0:
                trace['cycles'] += 1
                print(f"SDL 전체 반복 {trace['cycles']}/2 완료", flush=True)

    def push_exit(kind):
        event = pico.SDL_Event()
        event.type = kind
        if kind == pico.SDL_KEYDOWN:
            event.key.keysym.sym = pico.SDLK_ESCAPE
            event.key.repeat = 0
        assert pico.SDL_PushEvent(ctypes.byref(event)) == 1

    def events():
        player = trace['player']
        if trace['pause_phase'] == 0 and player.moving:
            trace['paused_state'] = (player.frame_index, player.elapsed, player.horizontal_offset)
            pico.SDL_MinimizeWindow(pico.window)
            trace['pause_time'] = time.perf_counter()
            trace['pause_phase'] = 1
        elif trace['pause_phase'] == 1 and time.perf_counter()-trace['pause_time'] > 0.25:
            assert player.paused
            assert (player.frame_index, player.elapsed, player.horizontal_offset) == trace['paused_state']
            pico.SDL_RestoreWindow(pico.window)
            trace['pause_phase'] = 2
        elif trace['pause_phase'] == 2 and not player.paused:
            assert (player.frame_index, player.elapsed, player.horizontal_offset) == trace['paused_state']
            trace['pause_phase'] = 3
        if trace['cycles'] == 2:
            push_exit(pico.SDL_KEYDOWN)
        if time.perf_counter()-started > 180:
            raise RuntimeError('SDL 검증 제한 시간 180초 초과')
        result = original_events()
        for event in result:
            if (event.type == pico.SDL_QUIT
                    or event.type == pico.SDL_KEYDOWN and event.key == pico.SDLK_ESCAPE):
                trace['exit_events'].append((event.type, trace['cycles']))
        return result

    def draw(*args):
        player = trace['player']
        assert pico.SDL_GetWindowTitle(pico.window).decode('utf-8') == viewer['playback_title'](player)
        trace['title_phases'].add('대기' if player.waiting else '이동' if player.moving else '재생')
        original_draw(*args)

    try:
        globals_['Player'], globals_['draw_frame'], pico.get_events = TrackedPlayer, draw, events
        assert viewer['main']() == 0
        assert trace['cycles'] == 2, f"SDL 조기 종료: {trace['exit_events']}, 전체 반복 {trace['cycles']}/2"
        expected = [(i, j) for i, a in enumerate(ACTIONS) for _ in range(3)
                    for j in range(len(a['frames']))]
        assert trace['seen'] == expected * 2 + [(0, 0)]
        assert trace['moves'] == [2, 3, 4, 5, 6, 7] * 2
        assert trace['pause_phase'] == 3
        assert trace['title_phases'] == {'재생', '이동', '대기'}
        assert min(trace['waits']) >= 0.999
        assert max(trace['waits']) <= 1 + trace['max_dt'] + 0.003
        print(f"SDL 검증 통과: 456프레임, 편도 12회, 제목/속도/최소화/복원/Esc; "
              f"대기 {min(trace['waits']):.4f}~{max(trace['waits']):.4f}초", flush=True)

        class MovingPlayer(original_player):
            def __init__(self, actions):
                super().__init__(actions)
                self.action_index = 1
                self.start_action()
                for _ in range(36):
                    self.update(1/12)
                assert self.moving

        def close_events():
            push_exit(pico.SDL_QUIT)
            return original_events()

        globals_['Player'], globals_['draw_frame'], pico.get_events = MovingPlayer, original_draw, close_events
        assert viewer['main']() == 0
        print('SDL 이동 상태 창 닫기 통과', flush=True)
    finally:
        globals_['Player'], globals_['draw_frame'], pico.get_events = original_player, original_draw, original_events


if __name__ == '__main__':
    if sys.argv[1:] == ['--gui']:
        run_gui_checks()
    else:
        unittest.main()
