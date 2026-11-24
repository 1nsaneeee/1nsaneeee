"""Rebuild the animated banners from the original PNGs. Requires Pillow."""
from pathlib import Path

from PIL import Image, ImageChops


def build(source, name_box):
    base = Image.open(source).convert('RGB')
    name = base.crop(name_box)
    width, height = name.size
    # Only the front face of the lettering exceeds this red-channel threshold.
    face = name.getchannel('R').point(lambda red: 255 if red > 125 else 0)
    highlight = Image.blend(name, Image.new('RGB', name.size, '#fffde6'), .91)
    radius = width * .077
    ramp = Image.new('L', (256, 1))
    ramp.putdata([round(255 * max(0, 1 - abs(i - 127.5) / 127.5) ** 1.45) for i in range(256)])

    # A shared palette keeps the unlit pixels steady throughout the loop.
    palette = base.quantize(colors=184, method=Image.Quantize.MEDIANCUT)
    tones = []
    for color in ('#9acb91', '#afd998', '#bdf0a6', '#cbf6ac'):
        sample = Image.new('RGB', (1, 1), color)
        for i in range(18):
            tones.extend(Image.blend(sample, Image.new('RGB', (1, 1), '#fffde6'), i / 18).getpixel((0, 0)))
    palette.putpalette(palette.getpalette()[:184 * 3] + tones)
    background = base.quantize(palette=palette, dither=Image.Dither.NONE)
    frames = [background]
    for step in range(1, 39):
        center = width + radius * 1.5 - (width + radius * 3) * step / 39
        scale = 127.5 / radius
        mask = ramp.transform(name.size, Image.Transform.AFFINE,
                              (scale, .30 * scale, 127.5 - (center + .15 * height) * scale, 0, 0, 0),
                              resample=Image.Resampling.BILINEAR)
        overlay = Image.composite(highlight, name, ImageChops.multiply(mask, face))
        frame = background.copy()
        frame.paste(overlay.quantize(palette=palette, dither=Image.Dither.NONE), name_box[:2])
        frames.append(frame)
    frames.append(background)
    background.save(source.with_suffix('.gif'), save_all=True, append_images=frames[1:],
                    duration=[220] + [40] * 38 + [2540], loop=0, disposal=1, optimize=False)


if __name__ == '__main__':
    assets = Path(__file__).resolve().parent / 'assets'
    build(assets / 'zsh.png', (52, 163, 1256, 335))
    build(assets / 'zsh-mobile.png', (31, 148, 744, 251))
