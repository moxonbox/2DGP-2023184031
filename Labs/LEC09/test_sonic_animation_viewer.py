"""Run with Python; no pico2d, SDL window, or external test package required."""

import io
import math
from pathlib import Path
import runpy
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
        SDL_WINDOW_MINIMIZED=4, SDL_QUIT=1, SDL_KEYDOWN=2, SDLK_ESCAPE=27,
    )


class ViewerTests(unittest.TestCase):
    def test_all_data_and_invalid_values(self):
        validate(ACTIONS, 399, 525)
        self.assertEqual((len(ACTIONS), sum(len(a['frames']) for a in ACTIONS)), (15, 76))
        for fps in (0, -1, 61, math.inf, math.nan, True, '12'):
            with self.subTest(fps=fps), self.assertRaisesRegex(ValueError, 'action_01'):
                validate([{'id': 'action_01', 'fps': fps, 'frames': [FRAME]}], 399, 525)
        bad_frames = [(-1, 0, 10, 20, 5, 20), (390, 0, 10, 20, 5, 20),
                      (0, 520, 10, 20, 5, 20), (0, 0, 0, 20, 0, 20),
                      (0.5, 0, 10, 20, 5, 20), (0, 0, 10, 20, math.nan, 20),
                      (0, 0, 10, 20, 11, 20), (0, 0, 10, 20, 5, 21), (0, 0)]
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
        player.update(1/12 - 0.001)
        self.assertFalse(player.waiting)
        player.update(0.001)
        self.assertTrue(player.waiting)
        player.update(0.5)
        player.update(0.499)
        self.assertEqual(player.action_index, 0)
        player.update(0.001)
        self.assertEqual((player.action_index, player.frame_index, player.waiting), (1, 0, False))
        player.update(0.1)
        player.update(0.1)
        self.assertEqual(player.frame_index, 2)
        self.assertFalse(player.waiting)
        player.update(0.099)
        self.assertFalse(player.waiting)
        player.update(0.001)
        self.assertTrue(player.waiting)
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
            player.update(1/60)
            position = (player.action_index, player.frame_index)
            if position != seen[-1]:
                seen.append(position)
            if before == len(ACTIONS) - 1 and player.action_index == 0:
                cycles += 1
                if cycles == 2:
                    break
        expected = [(i, j) for i, action in enumerate(ACTIONS)
                    for j in range(len(action['frames']))]
        self.assertEqual(cycles, 2)
        self.assertEqual(seen, expected * 2 + [(0, 0)])

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
        pico.close_canvas.assert_called_once()


if __name__ == '__main__':
    unittest.main()
