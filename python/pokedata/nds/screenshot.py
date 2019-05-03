import os
import struct
from PIL import Image, ImageChops

__party_bg_color__ = (77, 190, 117)
__party_shadow_color__ = (0, 0, 0)

__pokemon_type_01_pos__ = (81, 43)
__pokemon_type_02_pos__ = (115, 43)
__move_01_type_pos__ = (19, 20)
__move_02_type_pos__ = (19, 52)
__move_03_type_pos__ = (19, 84)
__move_04_type_pos__ = (19, 116)

__type_colors__ = {
    (174, 190, 36): 'bug',
    (117, 93, 77): 'dark',
    (125, 101, 231): 'dragon',
    (255, 199, 52): 'electric',
    (166, 85, 60): 'fighting',
    (247, 85, 52): 'fire',
    (158, 174, 247): 'flying',
    (101, 101, 182): 'ghost',
    (125, 207, 85): 'grass',
    (215, 182, 93): 'ground',
    (93, 207, 231): 'ice',
    (174, 166, 150): 'normal',
    (182, 93, 166): 'poison',
    (255, 117, 166): 'psychic',
    (190, 166, 93): 'rock',
    (174, 174, 199): 'steel',
    (60, 158, 255): 'water',
}


def argb_to_rgb(data):
    result = []
    for i in range(0, len(data), 4):
        r, g, b = data[i + 1], data[i + 2], data[i + 3]
        result.append((r, g, b))
    return result


def load_gd_image(filepath):
    with open(filepath, 'rb') as fp:
        header_data = fp.read(11)
        image_data = fp.read()

    magic, width, height, one, fill = struct.unpack('>HHHBI', header_data)
    if magic != 65534 or one != 1 or fill != 0xffffffff or len(image_data) != width * height * 4:
        return None

    im = Image.frombytes('RGBA', (width, height), image_data, 'raw')
    _, r, g, b = im.split()
    return Image.merge('RGB', (r, g, b))


def key(image, keycolor, newcolor=(0, 0, 0, 0)):
    r, g, b = keycolor
    solid = (r, g, b, 255)
    pix = image.load()
    num_set = 0
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            if pix[x,y] == solid:
                pix[x,y] = newcolor
                num_set += 1
    return image if num_set < (image.size[0] * image.size[1]) else None


def trim(image, pad=0):
    pix = image.load()
    min_x, max_x, min_y, max_y = None, None, None, None
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            if pix[x,y][3] > 0:
                if min_x is None or x < min_x:
                    min_x = x
                if max_x is None or x > max_x:
                    max_x = x
                if min_y is None or y < min_y:
                    min_y = y
                if max_y is None or y > max_y:
                    max_y = y
    return image.crop((min_x - pad, min_y - pad, max_x + 1 + pad, max_y + 1 + pad))


def extract_sprite(filepath):
    im = load_gd_image(filepath)
    if not im:
        return None

    im = im.convert('RGBA')
    im = key(im, __party_bg_color__)
    if not im:
        return None
    im = key(im, __party_shadow_color__)
    if not im:
        return None

    im = trim(im, pad=2)

    sil = im.getchannel('A').convert('1')
    shadow = ImageChops.logical_or(sil, ImageChops.offset(sil, 2, 2))
    shadow = ImageChops.logical_or(shadow, ImageChops.offset(sil, 0, -1))
    shadow = ImageChops.logical_or(shadow, ImageChops.offset(sil, -1, -1))
    shadow = ImageChops.logical_or(shadow, ImageChops.offset(sil, -1, 0))
    shadow = ImageChops.logical_or(shadow, ImageChops.offset(sil, -1, 1))
    shadow = ImageChops.logical_or(shadow, ImageChops.offset(sil, 0, 1))
    shadow = ImageChops.logical_or(shadow, ImageChops.offset(sil, 1, 1))
    shadow = ImageChops.logical_or(shadow, ImageChops.offset(sil, 1, 0))
    shadow = ImageChops.logical_or(shadow, ImageChops.offset(sil, 1, -1))

    result = ImageChops.composite(Image.new('RGBA', im.size, (0, 0, 0, 210)), Image.new('RGBA', im.size, (0, 0, 0, 0)), shadow)
    result = ImageChops.add(result, im)
    return result


def get_pokemon_types(filepath):
    im = load_gd_image(filepath)
    if not im:
        return None, None
    return __type_colors__.get(im.getpixel(__pokemon_type_01_pos__)), __type_colors__.get(im.getpixel(__pokemon_type_02_pos__))


def get_move_types(filepath):
    im = load_gd_image(filepath)
    if not im:
        return []
    return [
        __type_colors__.get(im.getpixel(__move_01_type_pos__)),
        __type_colors__.get(im.getpixel(__move_02_type_pos__)),
        __type_colors__.get(im.getpixel(__move_03_type_pos__)),
        __type_colors__.get(im.getpixel(__move_04_type_pos__)),
    ]
