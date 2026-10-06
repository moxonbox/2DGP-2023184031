"""Play the irregular Classic Sonic sprite sheet with pico2d."""

from pathlib import Path

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
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
]


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


def main():
    import pico2d

    pico2d.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    image = pico2d.load_image(str(IMAGE_PATH))
    print(f'Sprite sheet: {image.w} x {image.h}')
    draw_frame(pico2d, image, ACTIONS[0]['frames'][0], action_layout(ACTIONS[0]))
    pico2d.close_canvas()


if __name__ == '__main__':
    main()
