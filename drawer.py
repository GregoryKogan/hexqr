from PIL import Image, ImageDraw


color_map = {
    0: (255, 255, 255, 255),
    1: (255, 0, 0, 255),
    2: (0, 255, 0, 255),
    3: (0, 255, 255, 255)
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
    print(row, position, orientation)
    return row, position, orientation


def write_data(img, data):
    cells = len(data)
    cells_per_side = int(cells ** 0.5)
    if cells ** 0.5 != cells_per_side:
        cells_per_side = ((cells_per_side + 1) ** 2) ** 0.5
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


def build_code(data, size=500):
    background = get_body(size)
    img = write_data(background, data)

    img.show()
    img.save('Code.png')


if __name__ == '__main__':
    build_code('10210200103012331312121102001121123313110201', size=1000)
