from PIL import Image, ImageDraw
import math
import encoder
import random


def draw_regular_polygon(img, vertex_num, position, radius, offset_angle=0.0, color=(255, 255, 255, 255)):
    draw = ImageDraw.Draw(img)
    pos_x, pos_y = position
    vertexes = []
    for i in range(vertex_num):
        angle = 2 * math.pi / vertex_num * i + offset_angle
        vertex_x = pos_x + math.cos(angle) * radius
        vertex_y = pos_y + math.sin(angle) * radius
        vertex = (vertex_x, vertex_y)
        vertexes.append(vertex)
    draw.polygon(vertexes, fill=color)
    return img


def draw_triangle(img, position, orientation, side, color=(255, 255, 255, 255)):
    pos_x, pos_y = position
    height = 3 ** 0.5 / 2 * side
    if orientation == 'U':
        vertexes = [
            (pos_x, pos_y - height / 2),
            (pos_x - side / 2, pos_y + height / 2),
            (pos_x + side / 2, pos_y + height / 2)
        ]
    else:
        vertexes = [
            (pos_x, pos_y + height / 2),
            (pos_x - side / 2, pos_y - height / 2),
            (pos_x + side / 2, pos_y - height / 2)
        ]
    draw = ImageDraw.Draw(img)
    draw.polygon(vertexes, fill=color)
    return img


def get_body(size=500):
    body = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    body = draw_regular_polygon(body, 6, (size / 2, size / 2), size / 2, 0)
    body = draw_regular_polygon(body, 6, (size / 2, size / 2), size / 2 - size / 150, 0, (0, 0, 0, 255))
    return body


def get_cell_position_data(cell_index, cells_per_side):
    total_cells = 6 * cells_per_side ** 2
    if cell_index > total_cells / 2:
        cell_index -= total_cells / 2
        row = cells_per_side
        cells_last_row = cells_per_side * 2 + 1 + 2 * (cells_per_side - 1)
        while cell_index > 0:
            row += 1
            cell_index -= cells_last_row
            cells_last_row -= 2
        position = cell_index + cells_last_row + 2
        orientation = 'D' if position % 2 != 0 else 'U'
    else:
        row = 0
        cells_last_row = cells_per_side * 2 + 1
        while cell_index > 0:
            row += 1
            cell_index -= cells_last_row
            cells_last_row += 2
        position = cell_index + cells_last_row - 2
        orientation = 'U' if position % 2 != 0 else 'D'
    return row, position, orientation


def get_row_offset(row, cells_per_side, radius):
    cell_side = radius / cells_per_side
    if row > cells_per_side:
        row -= cells_per_side
        offset = cell_side * 0.5 * row - cell_side/2
    else:
        offset = cell_side * 0.5 * (cells_per_side - row)
    return offset


def write_data(img, data, radius, color_map=None):
    if not color_map:
        color_map = {
            0: (255, 255, 255, 255),
            1: (53, 79, 96, 255),
            2: (188, 14, 76, 255),
            3: (255, 197, 1, 255)
        }
    width, height = img.size
    center_x, center_y = width / 2, height / 2
    cells_per_side = 7
    cell_side = radius / cells_per_side
    cell_height = 3**0.5/2 * cell_side
    total_cells = 6 * cells_per_side ** 2
    for cell_index in range(1, total_cells + 1):
        row, position, orientation = get_cell_position_data(cell_index, cells_per_side)
        offset = get_row_offset(row, cells_per_side, radius)
        pos_x = center_x - radius + cell_side/2 * position + offset
        pos_y = center_y - radius * 3**0.5/2 + cell_height/2 + (row - 1) * cell_height
        img = draw_triangle(img, (pos_x, pos_y), orientation, cell_side, color_map[random.randint(0, 3)])
    return img


def build_code(data, size=500, path=None, show=False):
    body = get_body(size)
    code = write_data(body, data, size / 2 - size / 75)
    # code = code.rotate(90)
    code.show()


if __name__ == '__main__':
    data_to_code = encoder.code('https://youtu.be/dQw4w9WgXcQ')
    build_code(data_to_code, size=1000, path='Resources/Code.png', show=True)
