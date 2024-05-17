import time
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import Image, ImageDraw, ImageFont

def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height

device = ssd1306(i2c(port=1, address=0x3c), width=128, height=64, rotate=0)

# set the contrast to minimum.
device.contrast(1)

# load the rpi logo.
logo = Image.open('icons/lightbulb-0.png')

# show some info.
print(f'device size {device.size}')
print(f'device mode {device.mode}')
print(f'logo size {logo.size}')
print(f'logo mode {logo.mode}')

# NB this will only send the data to the display after this "with" block is complete.
# NB the draw variable is-a PIL.ImageDraw.Draw (https://pillow.readthedocs.io/en/3.1.x/reference/ImageDraw.html).
# see https://github.com/rm-hull/luma.core/blob/master/luma/core/render.py
with canvas(device, dither=True) as draw:
    #draw.rectangle(device.bounding_box, outline='white', fill='black')
    draw.bitmap((0, 0), logo)
    message = 'Raspberry Pi'
    text_height = 10
    text_width = 10
#    draw.text((device.width - text_width, (device.height - text_width) // 2), message, fill='white')

# NB the display will be turn off after we exit this application.
time.sleep(5*60)