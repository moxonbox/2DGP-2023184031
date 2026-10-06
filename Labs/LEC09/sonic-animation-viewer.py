"""Play the irregular Classic Sonic sprite sheet with pico2d."""

from pathlib import Path
from math import isfinite
import time
import sys

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
DEFAULT_FPS = 12
RENDER_FPS = 60
WAIT_SECONDS = 1.0
STALL_SECONDS = 0.5
IMAGE_PATH = Path(__file__).resolve().with_name('sonic-sprite.png')

# Frames: left, top, width, height, anchor_x, anchor_y (top-left origin).
ACTIONS = [
    {'id': 'action_01', 'fps': 6, 'frames': [
        (1, 39, 29, 39, 14.5, 39),
        (31, 40, 26, 38, 13, 38),
        (58, 39, 29, 39, 14.5, 39),
        (87, 40, 29, 38, 14.5, 38),
        (118, 40, 30, 38, 15, 38),
        (150, 40, 30, 38, 15, 38),
        (182, 40, 28, 38, 14, 38),
    ]},
    {'id': 'action_02', 'fps': 6, 'frames': [
        (210, 39, 30, 38, 15, 38),
        (240, 39, 29, 38, 14.5, 38),
    ]},
    {'id': 'action_03', 'frames': [
        (270, 45, 24, 32, 12, 32),
    ]},
    {'id': 'action_04', 'frames': [
        (302, 51, 29, 26, 14.5, 26),
    ]},
    {'id': 'action_05', 'frames': [
        (8, 80, 26, 37, 13, 37),
        (37, 80, 27, 37, 13.5, 37),
        (65, 80, 31, 38, 15.5, 38),
        (97, 80, 37, 37, 18.5, 37),
        (135, 80, 32, 35, 16, 35),
        (170, 79, 32, 38, 16, 38),
        (206, 79, 26, 38, 13, 38),
        (238, 80, 24, 37, 12, 37),
        (263, 80, 30, 37, 15, 37),
        (295, 80, 36, 37, 18, 37),
        (334, 80, 32, 36, 16, 36),
        (370, 79, 29, 38, 14.5, 38),
    ]},
    {'id': 'action_06', 'fps': 16, 'frames': [
        (1, 124, 33, 40, 16.5, 40),
        (39, 124, 35, 39, 17.5, 39),
        (89, 125, 35, 38, 17.5, 38),
        (130, 121, 34, 42, 17, 42),
        (181, 122, 34, 41, 17, 41),
        (228, 122, 33, 40, 16.5, 40),
    ]},
    {'id': 'action_07', 'fps': 16, 'frames': [
        (1, 169, 29, 30, 14.5, 15),
        (35, 167, 29, 31, 14.5, 15.5),
        (67, 169, 30, 29, 15, 14.5),
        (98, 169, 31, 29, 15.5, 14.5),
        (131, 168, 29, 30, 14.5, 15),
        (162, 168, 29, 31, 14.5, 15.5),
        (193, 170, 30, 29, 15, 14.5),
        (230, 170, 31, 29, 15.5, 14.5),
        (268, 170, 30, 30, 15, 15),
    ]},
    {'id': 'action_08', 'fps': 16, 'frames': [
        (1, 206, 30, 27, 15, 13.5),
        (36, 206, 29, 27, 14.5, 13.5),
        (70, 206, 29, 27, 14.5, 13.5),
        (105, 206, 29, 27, 14.5, 13.5),
        (139, 206, 29, 27, 14.5, 13.5),
        (174, 206, 29, 27, 14.5, 13.5),
    ]},
    {'id': 'action_09', 'frames': [
        (1, 239, 29, 35, 14.5, 35),
        (36, 239, 30, 35, 15, 35),
        (74, 239, 31, 35, 15.5, 35),
        (111, 238, 31, 36, 15.5, 36),
        (149, 239, 30, 35, 15, 35),
        (186, 238, 31, 36, 15.5, 36),
    ]},
    {'id': 'action_10', 'fps': 16, 'frames': [
        (1, 283, 29, 35, 14.5, 35),
        (36, 283, 30, 35, 15, 35),
        (72, 286, 39, 31, 19.5, 31),
        (123, 285, 39, 32, 19.5, 32),
        (172, 286, 39, 31, 19.5, 31),
        (218, 285, 38, 32, 19, 32),
    ]},
    {'id': 'action_11', 'fps': 10, 'frames': [
        (1, 326, 24, 45, 12, 22.5),
        (31, 327, 29, 44, 14.5, 22),
        (65, 327, 20, 44, 10, 22),
        (90, 327, 25, 43, 12.5, 21.5),
        (119, 327, 25, 43, 12.5, 21.5),
        (149, 327, 20, 44, 10, 22),
    ]},
    {'id': 'action_12', 'fps': 8, 'frames': [
        (184, 341, 40, 28, 20, 14),
        (232, 341, 39, 27, 19.5, 13.5),
    ]},
    {'id': 'action_13', 'fps': 10, 'frames': [
        (1, 379, 27, 38, 13.5, 38),
        (31, 379, 31, 36, 15.5, 36),
        (64, 379, 31, 36, 15.5, 36),
        (99, 377, 33, 38, 16.5, 38),
        (136, 379, 32, 36, 16, 36),
        (176, 379, 33, 36, 16.5, 36),
        (217, 379, 33, 36, 16.5, 36),
        (254, 378, 33, 36, 16.5, 36),
    ]},
    {'id': 'action_14', 'fps': 8, 'frames': [
        (6, 429, 34, 40, 17, 20),
        (49, 426, 34, 43, 17, 21.5),
    ]},
    {'id': 'action_15', 'fps': 6, 'frames': [
        (96, 427, 23, 39, 11.5, 39),
        (125, 427, 23, 39, 11.5, 39),
    ]},
]


def validate_actions(actions, sheet_width, sheet_height):
    if not actions:
        raise ValueError('동작 목록이 비어 있습니다.')
    ids = set()
    for action in actions:
        action_id = action.get('id')
        if not isinstance(action_id, str) or not action_id or action_id in ids:
            raise ValueError(f'잘못되거나 중복된 동작 ID: {action_id}')
        ids.add(action_id)
        fps = action.get('fps', DEFAULT_FPS)
        if (not isinstance(fps, (int, float)) or isinstance(fps, bool)
                or not isfinite(fps) or not 0 < fps <= RENDER_FPS):
            raise ValueError(f'{action_id}: FPS는 0 초과 {RENDER_FPS} 이하이어야 합니다.')
        if not action.get('frames'):
            raise ValueError(f'{action_id}: 프레임 목록이 비어 있습니다.')
        for number, frame in enumerate(action['frames'], 1):
            error = f'{action_id} 프레임 {number}: 잘못된 좌표 또는 정렬점'
            if len(frame) != 6:
                raise ValueError(error)
            left, top, width, height, ax, ay = frame
            if not all(type(v) is int for v in frame[:4]):
                raise ValueError(error)
            if (left < 0 or top < 0 or width <= 0 or height <= 0
                    or left + width > sheet_width or top + height > sheet_height):
                raise ValueError(error)
            if (not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                        and isfinite(v) for v in (ax, ay))
                    or not 0 <= ax <= width or not 0 <= ay <= height):
                raise ValueError(error)


class Player:
    """Small playback state; update takes elapsed seconds for headless checks."""

    def __init__(self, actions):
        self.actions = actions
        self.action_index = 0
        self.frame_index = 0
        self.elapsed = 0.0
        self.waiting = False
        self.paused = False

    @property
    def action(self):
        return self.actions[self.action_index]

    @property
    def frame(self):
        return self.action['frames'][self.frame_index]

    def update(self, dt):
        if not isfinite(dt) or dt < 0:
            raise ValueError('경과 시간은 유한한 0 이상 값이어야 합니다.')
        if self.paused or dt > STALL_SECONDS:
            return
        self.elapsed += dt
        if self.waiting:
            if self.elapsed + 1e-12 >= WAIT_SECONDS:
                self.action_index = (self.action_index + 1) % len(self.actions)
                self.frame_index = 0
                self.elapsed = 0.0
                self.waiting = False
            return
        interval = 1 / self.action.get('fps', DEFAULT_FPS)
        if self.elapsed + 1e-12 >= interval:
            self.elapsed = max(0.0, self.elapsed - interval)
            if self.frame_index < len(self.action['frames']) - 1:
                self.frame_index += 1
                # The final frame gets a complete interval before the extra wait.
                if self.frame_index == len(self.action['frames']) - 1:
                    self.elapsed = 0.0
            else:
                self.waiting = True
                self.elapsed = 0.0


def action_layout(action):
    frames = action['frames']
    xmin = min(-f[4] for f in frames)
    xmax = max(f[2] - f[4] for f in frames)
    ymin = min(f[5] - f[3] for f in frames)
    ymax = max(f[5] for f in frames)
    scale = min(CANVAS_WIDTH, CANVAS_HEIGHT) / (3 * max(xmax - xmin, ymax - ymin))
    return (scale, CANVAS_WIDTH / 2 - (xmin + xmax) / 2 * scale,
            CANVAS_HEIGHT / 2 - (ymin + ymax) / 2 * scale)


def draw_frame(pico2d, image, frame, layout):
    left, top, width, height, anchor_x, anchor_y = frame
    scale, origin_x, origin_y = layout
    bottom = image.h - top - height
    pico2d.clear_canvas()
    image.clip_draw(left, bottom, width, height,
                    origin_x + (width / 2 - anchor_x) * scale,
                    origin_y + (anchor_y - height / 2) * scale,
                    width * scale, height * scale)
    pico2d.update_canvas()


def run_viewer(pico2d, image_path=IMAGE_PATH):
    try:
        pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
        if not pico2d.window or not pico2d.renderer:
            raise RuntimeError('캔버스를 생성하지 못했습니다.')
        try:
            image = pico2d.load_image(str(image_path))
        except OSError as error:
            raise OSError(f'스프라이트 이미지를 읽을 수 없습니다: {image_path}') from error
        validate_actions(ACTIONS, image.w, image.h)
        player = Player(ACTIONS)
        layouts = [action_layout(action) for action in ACTIONS]
        previous = time.perf_counter()
        while True:
            loop_start = time.perf_counter()
            for event in pico2d.get_events():
                if (event.type == pico2d.SDL_QUIT
                        or event.type == pico2d.SDL_KEYDOWN and event.key == pico2d.SDLK_ESCAPE):
                    return
            now = time.perf_counter()
            paused = bool(pico2d.SDL_GetWindowFlags(pico2d.window) & pico2d.SDL_WINDOW_MINIMIZED)
            dt = 0.0 if paused != player.paused else now - previous
            player.paused = paused
            player.update(dt)
            previous = now
            if not player.paused:
                draw_frame(pico2d, image, player.frame, layouts[player.action_index])
            time.sleep(max(0.0, 1 / RENDER_FPS - (time.perf_counter() - loop_start)))
    finally:
        pico2d.close_canvas()


def main():
    try:
        # The package re-exports functions, but window/renderer live in this module.
        import pico2d.pico2d as pico2d
    except ImportError:
        print('pico2d가 필요합니다. 현재 Python 환경에 pico2d를 설치하세요.', file=sys.stderr)
        return 1
    try:
        run_viewer(pico2d)
    except (OSError, ValueError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
