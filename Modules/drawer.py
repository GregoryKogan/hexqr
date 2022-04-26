import encoder
from PIL import Image, ImageDraw
import math
import random


# Returns square black RGBA image of given width
def get_square_image(width):
    return Image.new('RGBA', (width, width), color=(0, 0, 0, 0))


# Draws hexagon on given image of given radius and color
def draw_hexagon(img, radius=None, color=(255, 255, 255, 255)):
    if not radius:
        radius = min(img.size) / 2
        
    vertexes = []
    width, height = img.size
    x_c = width / 2
    y_c = height / 2
    for point_i in range(6):
        angle = math.pi / 3 * point_i
        x_i = x_c + math.cos(angle) * radius
        y_i = y_c - math.sin(angle) * radius
        vertexes.append((x_i, y_i))
    draw = ImageDraw.Draw(img)
    draw.polygon(vertexes, fill=color)
    return img


# Returns row, position and orientation of a triangle with given index in a hexagon with given size
def position_by_index(index, n):
    cells_at_current_row = n * 2 + 1
    current_pos = 1
    current_row = 1
    current_index = 1
    while current_index < index:
        current_index += 1
        current_pos += 1
        if current_pos > cells_at_current_row:
            current_pos = 1
            current_row += 1
            if current_row <= n:
                cells_at_current_row += 2
            elif current_row != n + 1:
                cells_at_current_row -= 2

    if (
        current_row <= n
        and current_pos % 2 == 0
        or current_row > n
        and current_pos % 2 != 0
    ):
        orientation = 'D'
    else:
        orientation = 'U'
    return current_row, current_pos, orientation


# Returns index of a triangle with given position in a hexagon with given size
def index_by_position(row, position, n):
    cells_at_current_row = n * 2 + 1
    current_pos = 1
    current_row = 1
    current_index = 1
    if current_row == row and current_pos == position:
        return current_index
    while current_index < n*n*6:
        current_index += 1
        current_pos += 1
        if current_pos > cells_at_current_row:
            current_pos = 1
            current_row += 1
            if current_row <= n:
                cells_at_current_row += 2
            elif current_row != n + 1:
                cells_at_current_row -= 2
        if current_row == row and current_pos == position:
            return current_index
    return None


# Get height of equilateral triangle with given side length
def get_height_of_equilateral_triangle(side):
    return 3**0.5 / 2 * side


# Get triangle coordinates in image by its position inside hexagon
def coordinates_by_position(row, position, n, radius, width):
    triangle_width = radius / n
    triangle_height = get_height_of_equilateral_triangle(triangle_width)
    square_width = radius * 2

    vertical_gap = (2 - 3**0.5) / 4 * square_width
    vertical_gap += (width - square_width) / 2
    y_coordinate = vertical_gap + triangle_height / 2 + (row - 1) * triangle_height

    if row <= n:
        row = n - row + 1
    if row > n:
        row = row - n

    max_gap = square_width / 4
    const_gap = (width - square_width) / 2
    horizontal_gap = (max_gap / (2 * n)) * 2 * (row - 1) + const_gap
    x_coordinate = horizontal_gap + triangle_width / 2 * position

    return x_coordinate, y_coordinate


def draw_equilateral_triangle(image, position, width, orientation, color=(255, 255, 255, 255)):
    height = 3 ** 0.5 / 2 * width
    pos_x, pos_y = position
    if orientation == 'U':
        vertexes = [
            (pos_x, pos_y - height / 2),
            (pos_x - width / 2, pos_y + height / 2),
            (pos_x + width / 2, pos_y + height / 2)
        ]
    else:
        vertexes = [
            (pos_x, pos_y + height / 2),
            (pos_x - width / 2, pos_y - height / 2),
            (pos_x + width / 2, pos_y - height / 2)
        ]
    draw = ImageDraw.Draw(image)
    draw.polygon(vertexes, fill=color)
    return image


def count_n_for_data(data_length):
    final_length = data_length + 18 + 10
    return next((n for n in range(1, 25) if n * n * 6 >= final_length), None)


def get_avoid_indexes(n):
    avoid_positions = [
        (1, 1),
        (1, 2),
        (1, 2 * n),
        (1, 2 * n + 1),
        (n, 1),
        (n + 1, 1),
        (n, 4 * n - 1),
        (n + 1, 4 * n - 1),
        (2 * n, 1),
        (2 * n, 2),
        (2 * n, 2 * n),
        (2 * n, 2 * n + 1),
        (n, 2 * n - 1),
        (n, 2 * n),
        (n, 2 * n + 1),
        (n + 1, 2 * n - 1),
        (n + 1, 2 * n),
        (n + 1, 2 * n + 1)
    ]
    avoid_indexes = []
    for position in avoid_positions:
        index = index_by_position(position[0], position[1], n)
        avoid_indexes.append(index)
    return avoid_indexes


def write_data(image, radius, data, color_map=None):
    if not color_map:
        color_map = {
            0: (255, 255, 255, 255),
            1: (53, 79, 96, 255),
            2: (188, 14, 76, 255),
            3: (255, 197, 1, 255)
        }
    width = min(image.size)
    n = count_n_for_data(len(data))
    triangle_width = radius / n
    
    avoid_indexes = get_avoid_indexes(n)

    bits_done = 0
    for index in range(1, n * n * 6 + 1):
        if index not in avoid_indexes:
            if bits_done < len(data):
                bit = int(data[bits_done])
                bits_done += 1
            else:
                bit = index % 4
            row, position, orientation = position_by_index(index, n)
            coordinate_x, coordinate_y = coordinates_by_position(row, position, n, radius, width)
            image = draw_equilateral_triangle(image, (coordinate_x, coordinate_y), triangle_width, orientation,
                                              color=color_map[bit])
    return image


def count_brightness(color):
    return (color[0] + color[1] + color[2]) / 3


def get_brightest(colormap):
    brightest = colormap[0]
    for i in range(1, len(colormap)):
        if count_brightness(colormap[i]) > count_brightness(brightest):
            brightest = colormap[i]
    return brightest


def get_darkest(colormap):
    darkest = colormap[0]
    for i in range(1, len(colormap)):
        if count_brightness(colormap[i]) < count_brightness(darkest):
            darkest = colormap[i]
    return darkest


def count_center(vertexes):
    x_center = 0
    y_center = 0
    for vertex in vertexes:
        x_center += vertex[0]
        y_center += vertex[1]
    x_center /= len(vertexes)
    y_center /= len(vertexes)
    return x_center, y_center


def calculate_scale_shape(vertexes, scale):
    x_center, y_center = count_center(vertexes)
    new_vertexes = []
    for vertex in vertexes:
        final_x = (vertex[0] + scale * x_center) / (scale + 1)
        final_y = (vertex[1] + scale * y_center) / (scale + 1)
        new_vertexes.append((final_x, final_y))
    return new_vertexes


def draw_markers(image, data_length, radius, color_map=None):
    if not color_map:
        color_map = {
            0: (255, 255, 255, 255),
            1: (53, 79, 96, 255),
            2: (188, 14, 76, 255),
            3: (255, 197, 1, 255)
        }

    n = count_n_for_data(data_length)
    width = min(image.size)
    triangle_width = radius / n

    top_corner = [(1, 1), (1, 2)]
    for point in top_corner:
        index = index_by_position(point[0], point[1], n)
        row, position, orientation = position_by_index(index, n)
        coordinate_x, coordinate_y = coordinates_by_position(row, position, n, radius, width)
        image = draw_equilateral_triangle(image, (coordinate_x, coordinate_y), triangle_width, orientation,
                                          color=get_darkest(color_map))
    other_corners = [
        (1, 2 * n),
        (1, 2 * n + 1),
        (n, 1),
        (n + 1, 1),
        (n, 4 * n - 1),
        (n + 1, 4 * n - 1),
        (2 * n, 1),
        (2 * n, 2),
        (2 * n, 2 * n),
        (2 * n, 2 * n + 1)
    ]
    for point in other_corners:
        index = index_by_position(point[0], point[1], n)
        row, position, orientation = position_by_index(index, n)
        coordinate_x, coordinate_y = coordinates_by_position(row, position, n, radius, width)
        image = draw_equilateral_triangle(image, (coordinate_x, coordinate_y), triangle_width, orientation,
                                          color=get_brightest(color_map))

    center_hexagon_points = [
        (n, 2 * n - 1),
        (n, 2 * n),
        (n, 2 * n + 1),
        (n + 1, 2 * n - 1),
        (n + 1, 2 * n),
        (n + 1, 2 * n + 1)
    ]
    for point in center_hexagon_points:
        index = index_by_position(point[0], point[1], n)
        row, position, orientation = position_by_index(index, n)
        coordinate_x, coordinate_y = coordinates_by_position(row, position, n, radius, width)
        image = draw_equilateral_triangle(image, (coordinate_x, coordinate_y), triangle_width, orientation,
                                          color=get_darkest(color_map))

    height = 3 ** 0.5 / 2 * triangle_width
    top_point = list(coordinates_by_position(n, 2 * n - 1, n, radius, width))
    top_point[1] -= height / 2
    top_point = tuple(top_point)
    
    left_point = list(coordinates_by_position(n + 1, 2 * n - 1, n, radius, width))
    left_point[1] += height / 2
    left_point = tuple(left_point)

    right_point = list(coordinates_by_position(n, 2 * n + 1, n, radius, width))
    right_point[0] += triangle_width / 2
    right_point[1] += height / 2
    right_point = tuple(right_point)

    center_triangle_vertexes = [top_point, left_point, right_point]

    draw = ImageDraw.Draw(image)
    draw.polygon(center_triangle_vertexes, fill=(0, 0, 0, 255))
    draw.polygon(calculate_scale_shape(center_triangle_vertexes, 0.1), fill=(255, 255, 255, 255))
    draw.polygon(calculate_scale_shape(center_triangle_vertexes, 0.2), fill=(0, 0, 0, 255))
    return image


def build_code(data, size=1000, color_map=None, orientation=None):
    code_image = get_square_image(size)
    code_image = draw_hexagon(code_image, radius=min(code_image.size) / 2, color=(255, 255, 255, 255))
    code_image = draw_hexagon(code_image, radius=min(code_image.size) / 2 * 0.99, color=(0, 0, 0, 255))
    code_image = draw_markers(code_image, len(data), radius=min(code_image.size) / 2 * 0.97, color_map=color_map)
    code_image = write_data(code_image, data=data, radius=min(code_image.size) / 2 * 0.97, color_map=color_map)
    if orientation == 'CRYSTAL':
        code_image = code_image.resize((size * 5, size * 5))
        code_image = code_image.rotate(-30)
        code_image.thumbnail((size, size), Image.ANTIALIAS)
    return code_image
    

if __name__ == '__main__':
    data_to_code = encoder.code('https://youtu.be/dQw4w9WgXcQ')
    code = build_code(data_to_code, size=1000, orientation='CRYSTAL')
    code.show()
    code.save('Resources/HEXCode.png')
