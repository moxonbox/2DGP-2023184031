from pico2d import *

open_canvas()

grass = load_image('grass.png')
boy = load_image('animation_sheet.png')


def animation(sel):
    frame = 0
    for x in range(5, 750, 5):
        clear_canvas()
        grass.draw(400, 30)
        boy.clip_composite_draw(
            frame * 100, sel, # L, bottom
            100, 100,       # W, H
            math.pi/8, 'h',         # Rotation, Flip
            x, 90,          # destination X, Y
            200, 200        # Scale
        )
        update_canvas()

        frame = (frame + 1) % 8
        delay(0.05)




while(1):
    sel += 1
    animation(sel)



close_canvas()