from PIL import Image, ImageDraw
import random
import encoder


color_map = {
    0: (255, 255, 255, 255),
    1: (53, 79, 96, 255),
    2: (188, 14, 76, 255),
    3: (255, 197, 1, 255)
}


def get_body(size):
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    width, height = img.size
    tri_side = width
    tri_height = 3**0.5 / 2 * tri_side
    draw.polygon([(width / 2, height / 2 - tri_height / 2),
                  (0, height / 2 + tri_height / 2),
                  (width, height / 2 + tri_height / 2)],
                 fill=(0, 0, 0, 255))
    return img


def get_position(index):
    row = 0
    cells_last_row = 1
    while index > 0:
        row += 1
        index -= cells_last_row
        cells_last_row += 2
    position = index + cells_last_row - 2
    orientation = 'U' if position % 2 != 0 else 'D'
    position -= ((cells_last_row - 2) // 2 + 1)
    return row, position, orientation


def insert_to_string(line, symbol, index):
    return line[:index] + symbol + line[index:]


def generate_random_data(length):
    generated_data = ''
    for _ in range(length):
        byte = random.randint(0, 3)
        generated_data += str(byte)
    return generated_data


def write_data(size, data):
    data = data + '3333'
    last_row, _, _ = get_position(len(data) + 3)
    data = insert_to_string(data, '1', 0)
    data = insert_to_string(data, '023', 1)
    data = insert_to_string(data, '0', (last_row - 1) ** 2)
    data = data + generate_random_data(last_row ** 2 - len(data) - 1)
    data += '0'
    cells = len(data)
    cells_per_side = int(cells ** 0.5)
    if cells ** 0.5 != cells_per_side:
        cells_per_side = ((cells_per_side + 1) ** 2) ** 0.5
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    width, height = img.size
    tri_side = width
    tri_height = 3**0.5 / 2 * tri_side
    cell_side = tri_side / cells_per_side
    cell_height = tri_height / cells_per_side
    for index, data_bit in enumerate(data, start=1):
        data_color = color_map[int(data_bit)]
        row, position, orientation = get_position(index)
        center_y = (row - 1) * cell_height + cell_height / 2 + (height / 2 - tri_height / 2)
        center_x = position * cell_side / 2 + width / 2
        if orientation == 'U':
            draw.polygon([(center_x, center_y - cell_height / 2),
                          (center_x - cell_side / 2, center_y + cell_height / 2),
                          (center_x + cell_side / 2, center_y + cell_height / 2)],
                         fill=data_color)
        else:
            draw.polygon([(center_x - cell_side / 2, center_y - cell_height / 2),
                          (center_x + cell_side / 2, center_y - cell_height / 2),
                          (center_x, center_y + cell_height / 2)],
                         fill=data_color)
    return img


def build_code(data, size=500, outline=0.98, path=None, show=False):
    data = write_data(int(size * outline), data)
    background = get_body(size)
    bounds = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    bounds_width, bounds_height = bounds.size
    data_width, data_height = data.size
    offset = ((bounds_width - data_width) // 2, (bounds_height - data_height) * 2 // 3)
    bounds.paste(data, offset)
    code_img = Image.alpha_composite(background, bounds)
    if show:
        code_img.show()
    if path:
        try:
            code_img.save(path)
        except Exception:
            print(f"Can't save code to directory: '{path}'")
            raise ValueError
    else:
        return code_img


if __name__ == '__main__':
    data_to_code = encoder.code('https://youtu.be/dQw4w9WgXcQ')
    build_code(data_to_code, size=1000, path='Code.png', show=True)
