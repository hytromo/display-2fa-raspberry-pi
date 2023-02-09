import LCD_1in44
import LCD_Config
from datetime import datetime
from os import path, environ
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Images will become thumbnails with the same aspect ratio as the original
IMAGE_WIDTH = 28
IMAGE_HEIGHT = 24
CENTER_IMAGE_IN_FIRST_N_PIXELS = 35

FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
FONT_SIZE = 22

PROGRESSBAR_COLOR = "WHITE"
PROGRESSBAR_WIDTH = 2

# Blur effect
CODE_ROTATION_EFFECT_ENABLED = True
# the more the smoother, but more cpu intensive and a bit slower
CODE_ROTATION_EFFECT_LOOPS = 25

# 0, 90, 180, 270 depending on how your RPi stands
DISPLAY_ROTATION_DEGREES = 90

LCD = LCD_1in44.LCD()
LCD.LCD_Init(LCD_1in44.SCAN_DIR_DFT)


canvas_with_images = Image.new("RGB", (LCD.width, LCD.height), "BLACK")


def include_in_canvas_and_return(rel_path, index):
    global canvas_with_images
    final_path = path.join(path.dirname(path.abspath(__file__)), rel_path)
    img = Image.open(final_path)
    img.thumbnail(
        [IMAGE_WIDTH, IMAGE_HEIGHT], Image.AFFINE)
    canvas_with_images.paste(
        img, (int((CENTER_IMAGE_IN_FIRST_N_PIXELS - img.width) / 2), int(index * LCD.height / 4 + (LCD.height / 4 - img.height) / 2)))
    return img


display_definitions = {
    'AWS': {
        'image': include_in_canvas_and_return('logos/aws.png', 0),
        'code': environ.get('AWS_2FA_SECRET'),
        'color': '#ed9f2a'
    },
    'Google': {
        'image': include_in_canvas_and_return('logos/google.webp', 1),
        'code': environ.get('GOOGLE_2FA_SECRET'),
        'color': '#c85138'
    },
    'GitHub': {
        'image': include_in_canvas_and_return('logos/github.png', 2),
        'code': environ.get('GITHUB_2FA_SECRET'),
        'color': '#ffffff'
    },
    'Bitwarden': {
        'image': include_in_canvas_and_return('logos/bitwarden.png', 3),
        'code': environ.get('BITWARDEN_2FA_SECRET'),
        'color': '#345dd9'
    }
}


font = ImageFont.truetype(FONT_PATH, size=FONT_SIZE)
font_offset = font.getoffset('123456')


def display_message_centered_at_index(draw, message, index, color):
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    w += font_offset[0]
    h += font_offset[1]
    draw.text(((LCD.width-w+CENTER_IMAGE_IN_FIRST_N_PIXELS)/2, (LCD.height/4-h)/2 +
              index*(LCD.height/4)), message, font=font, fill=color)


def output_of(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8").strip()


def display_key(draw, code, index, color):
    twofa = output_of(['oathtool', '-b', '--totp', code])
    display_message_centered_at_index(draw, twofa, index, color)


def refresh_image(canvas):
    if DISPLAY_ROTATION_DEGREES == 0:
        LCD.LCD_ShowImage(canvas, 0, 0)
    else:
        LCD.LCD_ShowImage(canvas.rotate(DISPLAY_ROTATION_DEGREES), 0, 0)


def pick_between_gradient(color1, color2, weight):
    w2 = weight
    w1 = 1.0 - w2
    (c1r, c1g, c1b) = tuple(int(color1[i:i+2], 16) for i in (0, 2, 4))
    (c2r, c2g, c2b) = tuple(int(color2[i:i+2], 16) for i in (0, 2, 4))
    (resultR, resultG, resultB) = (
        int(float(c1r)*w1+float(c2r)*w2),
        int(float(c1g)*w1+float(c2g)*w2),
        int(float(c1b)*w1+float(c2b)*w2),
    )
    return '#%02x%02x%02x' % (resultR, resultG, resultB)


def main():
    def update_codes_loop(draw, canvas):
        for index, key in enumerate(display_definitions):
            display_key(
                draw, display_definitions[key]['code'], index, display_definitions[key]['color'])

        if CODE_ROTATION_EFFECT_ENABLED:
            canvas_orig = canvas
            for i in range(CODE_ROTATION_EFFECT_LOOPS):
                enhance = ImageEnhance.Brightness(canvas_orig.copy())
                canvas = enhance.enhance(1/(CODE_ROTATION_EFFECT_LOOPS - 1)*i)
                canvas = canvas.filter(
                    ImageFilter.GaussianBlur(radius=2.7 - i*0.3/(CODE_ROTATION_EFFECT_LOOPS/10)))
                refresh_image(canvas)

                LCD_Config.Driver_Delay_ms(500/CODE_ROTATION_EFFECT_LOOPS)

        refresh_image(canvas)

    while True:
        canvas = canvas_with_images.copy()
        draw = ImageDraw.Draw(canvas)

        update_codes_loop(draw, canvas)

        # progress bar
        while True:
            now = datetime.now()
            second_raw = now.second + now.microsecond / 1e6
            second = second_raw if second_raw <= 30 else second_raw - 30
            loaded_fraction = second / 30
            percentage = min(loaded_fraction, 1)
            draw.line([(LCD.width-1, LCD.height), (LCD.width-1, (1-percentage) *
                                                   LCD.height)], fill=PROGRESSBAR_COLOR, width=2)

            refresh_image(canvas)

            if loaded_fraction > 0.995:
                # let's draw it black now because this white line messes a bit with the blur
                draw.line([(LCD.width-1, LCD.height), (LCD.width-1,
                                                       0)], fill="black", width=PROGRESSBAR_WIDTH)
                refresh_image(canvas)

                if CODE_ROTATION_EFFECT_ENABLED:
                    canvas_orig = canvas
                    for i in range(CODE_ROTATION_EFFECT_LOOPS):
                        enhance = ImageEnhance.Brightness(canvas_orig.copy())
                        canvas = enhance.enhance(
                            1-1/(CODE_ROTATION_EFFECT_LOOPS-1)*i)
                        canvas = canvas.filter(
                            ImageFilter.GaussianBlur(radius=i*0.3/(CODE_ROTATION_EFFECT_LOOPS/10)))
                        refresh_image(canvas)
                        LCD_Config.Driver_Delay_ms(
                            500/CODE_ROTATION_EFFECT_LOOPS)
                else:
                    # make sure that we have the new codes ready
                    LCD_Config.Driver_Delay_ms(200)

                break  # update codes


if __name__ == '__main__':
    main()
