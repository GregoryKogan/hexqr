import cv2 as cv
import numpy as np
import math
import encoder


def show_image(img, size=700):
    if len(img.shape) == 3:
        height, width, _ = img.shape
    else:
        height, width = img.shape
    k = size / max(width, height)
    img_s = cv.resize(img, (int(width * k), int(height * k)))
    cv.imshow('Output', img_s)
    cv.waitKey(0)


def transform_for_contour_detection(image):
    image_copy = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image_copy = cv.blur(image_copy, (5, 5))
    image_copy = cv.equalizeHist(image_copy)
    _, image_copy = cv.threshold(image_copy, 180, 220, cv.THRESH_BINARY)
    return image_copy


def transform_for_small_contour_detection(image):
    image_copy = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image_copy = cv.blur(image_copy, (5, 5))
    _, image_copy = cv.threshold(image_copy, 180, 220, cv.THRESH_BINARY)
    image_copy = cv.Canny(image_copy, 30, 200)
    return image_copy


def find_main_shape(image, vertex_num):
    contours, _ = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    shapes = []
    for contour in contours:
        approx = cv.approxPolyDP(contour, 0.01 * cv.arcLength(contour, True), True)
        if len(approx) == vertex_num:
            shapes.append(approx)
    shapes.sort(key=cv.contourArea, reverse=True)
    main_shape = shapes[0]
    return main_shape


def find_shapes(image, vertex_num):
    contours, _ = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    shapes = []
    for contour in contours:
        approx = cv.approxPolyDP(contour, 0.01 * cv.arcLength(contour, True), True)
        if len(approx) == vertex_num:
            shapes.append(approx)
    shapes.sort(key=cv.contourArea, reverse=True)
    return shapes


def convert_contour_to_point_list(contour):
    contour = list(contour)
    for i in range(len(contour)):
        contour[i] = list(contour[i])
        contour[i][0] = list(contour[i][0])
        contour[i] = [contour[i][0][0], contour[i][0][1]]
    return contour


def get_4_points(hexagon):
    hexagon = convert_contour_to_point_list(hexagon)
    hexagon.pop(5)
    hexagon.pop(2)
    return hexagon


def get_target_points(center_x, center_y, radius):
    target_points = [[center_x + math.cos(0) * radius,
                      center_y - math.sin(0) * radius], [center_x + math.cos(math.pi / 3) * radius,
                                                         center_y - math.sin(math.pi / 3) * radius],
                     [center_x + math.cos(math.pi) * radius,
                      center_y - math.sin(math.pi) * radius], [center_x + math.cos(math.pi / 3 * 4) * radius,
                                                               center_y - math.sin(math.pi / 3 * 4) * radius]]
    return target_points


def convert_4_points_to_np_array(input_list):
    result = np.array([input_list[0],
                       input_list[1],
                       input_list[2],
                       input_list[3]]).astype(np.float32)
    return result


def warp(image, main_hex):
    source_points = get_4_points(main_hex)

    width = min(image.shape[0], image.shape[1])
    radius = width / 2
    center_x = image.shape[0] / 2
    center_y = image.shape[1] / 2
    target_points = get_target_points(center_x, center_y, radius)

    source_points = convert_4_points_to_np_array(source_points)
    target_points = convert_4_points_to_np_array(target_points)

    warp_matrix = cv.getPerspectiveTransform(source_points, target_points)
    warped_image = cv.warpPerspective(image, warp_matrix, (image.shape[1], image.shape[0]))
    return warped_image


def distance(point_1, point_2):
    x1 = point_1[0]
    y1 = point_1[1]
    x2 = point_2[0]
    y2 = point_2[1]
    dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    return dist


def get_side_length(triangle):
    points = convert_contour_to_point_list(triangle)
    side1 = distance(points[0], points[1])
    side2 = distance(points[1], points[2])
    side3 = distance(points[2], points[0])
    return (side1 + side2 + side3) / 3


def count_average(data):
    sum_of_all = 0
    for element in data:
        sum_of_all += element
    return sum_of_all / len(data)


def count_average_deviation(data):
    average_value = count_average(data)
    sum_of_deviations = 0
    for element in data:
        deviation = abs(average_value - element)
        sum_of_deviations += deviation
    return sum_of_deviations / len(data)


def count_cell_width(image):
    transformed_image = transform_for_small_contour_detection(image)
    triangles = find_shapes(transformed_image, 3)
    cell_width_values = []
    for triangle in triangles:
        side_length = get_side_length(triangle)
        cell_width_values.append(side_length)
    average_value = count_average(cell_width_values)
    average_deviation = count_average_deviation(cell_width_values)
    correct_cell_width_values = []
    for element in cell_width_values:
        if abs(average_value - element) < average_deviation:
            correct_cell_width_values.append(element)
    average_cell_width = count_average(correct_cell_width_values)
    radius = image.shape[0] / 2
    n = radius / (average_cell_width * 1.1)
    n = round(n)
    cell_width = radius / n
    return cell_width


def count_6_points(center_x, center_y, radius):
    points = []
    for i in range(6):
        angle = math.pi / 3 * i
        x = center_x + math.cos(angle) * radius
        y = center_y - math.sin(angle) * radius
        points.append([x, y])
    return points


def color_from_area(image, y, x):
    r, g, b = image[int(y), int(x)]
    return r, g, b


def count_average_color(colors):
    r = 0
    g = 0
    b = 0
    for color in colors:
        r += color[0]
        g += color[1]
        b += color[2]
    r /= len(colors)
    g /= len(colors)
    b /= len(colors)
    return r, g, b


def color_distance(color_1, color_2):
    dist = abs(int(color_1[0]) - int(color_2[0]))
    dist += abs(int(color_1[1]) - int(color_2[1]))
    dist += abs(int(color_1[2]) - int(color_2[2]))
    return dist


def find_odd_color(colors):
    average = count_average_color(colors)
    colors_copy = colors.copy()
    colors_copy.sort(reverse=True, key=lambda x: color_distance(x, average))
    return colors_copy[0]


def rotate_image_by_angle(image, angle):
    import imutils
    rotated = imutils.rotate(image, angle)
    return rotated


def rotate(image):
    cell_width = count_cell_width(image)
    pick_radius = image.shape[0] / 2 - cell_width / 2
    pick_points = count_6_points(image.shape[0] / 2, image.shape[1] / 2, pick_radius)
    pick_point_colors = []
    for point in pick_points:
        pick_point_colors.append(color_from_area(image, point[1], point[0]))
        cv.circle(image, (int(point[0]), int(point[1])), 10, (0, 0, 255), 3)
    odd_point = find_odd_color(pick_point_colors)
    odd_point_index = pick_point_colors.index(odd_point)

    angle = 60 * odd_point_index * (-1) + 120
    image = rotate_image_by_angle(image, angle)
    return image, cell_width


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

    return current_row, current_pos


def get_height_of_equilateral_triangle(side):
    return 3**0.5 / 2 * side


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


def get_bit(color, color_map):
    bit = 0
    min_distance = color_distance(color, color_map[0])
    for i in range(1, len(color_map)):
        dist = color_distance(color, color_map[i])
        if dist < min_distance:
            bit = i
            min_distance = dist
    return bit


def extract_data(image, cell_width):
    radius = image.shape[0] / 2
    n = round(radius / (cell_width * 0.95))
    radius *= 0.99
    avoid_indexes = get_avoid_indexes(n)
    data_point_colors = []
    for index in range(1, n * n * 6 + 1):
        if index not in avoid_indexes:
            row, position = position_by_index(index, n)
            coordinate_x, coordinate_y = coordinates_by_position(row, position, n, radius, radius * 2)
            data_point_colors.append(color_from_area(image, round(coordinate_y), round(coordinate_x)))
            cv.circle(image, (int(coordinate_x), int(coordinate_y)), 7, (255, 0, 0, 255), 3)
    color_map = {
        0: data_point_colors[0],
        1: data_point_colors[1],
        2: data_point_colors[2],
        3: data_point_colors[3]
    }
    data = []
    for color in data_point_colors:
        bit = get_bit(color, color_map)
        data.append(str(bit))
    result = ''.join(data)
    return image, result


def cut_data(data):
    for i in range(5, len(data) - 3):
        if data[i] == data[i + 1] == data[i + 2] == data[i + 3] == '3':
            data = data[:i + 4:]
            return data


def scan(path):
    image = cv.imread(path)
    show_image(image)
    transformed_image = transform_for_contour_detection(image)
    main_hex = find_main_shape(transformed_image, 6)
    warped_image = warp(image, main_hex)
    show_image(warped_image)
    rotated_image, cell_width = rotate(warped_image)
    show_image(rotated_image)
    extracted_image, data = extract_data(rotated_image, cell_width)
    show_image(extracted_image)
    data = cut_data(data)
    return data


if __name__ == '__main__':
    coded_data = scan('Resources/HexDetect-1.jpg')
    print(encoder.decode(coded_data))
