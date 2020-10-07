import cv2
import numpy as np


def show_image(img, size=700):
    if len(img.shape) == 3:
        height, width, _ = img.shape
    else:
        height, width = img.shape
    k = size / max(width, height)
    img_s = cv2.resize(img, (int(width * k), int(height * k)))
    cv2.imshow('Output', img_s)
    cv2.waitKey(0)


def get_coordinates_after_perspective_transform(point, matrix):
    px = (matrix[0][0] * point[0] + matrix[0][1] * point[1] + matrix[0][2]) / (
            matrix[2][0] * point[0] + matrix[2][1] * point[1] + matrix[2][2])
    py = (matrix[1][0] * point[0] + matrix[1][1] * point[1] + matrix[1][2]) / (
            matrix[2][0] * point[0] + matrix[2][1] * point[1] + matrix[2][2])
    result = (int(px), int(py))
    return result


def get_incline_coefficient(x1, y1, x2, y2):
    if x2 - x1 != 0:
        coefficient = (y2 - y1) / (x2 - x1)
    else:
        coefficient = 0
    return coefficient


def get_triangle_incline_coefficients(triangle):
    vertex_1 = triangle[0][0]
    vertex_2 = triangle[1][0]
    vertex_3 = triangle[2][0]
    k1 = get_incline_coefficient(vertex_1[0], vertex_1[1], vertex_2[0], vertex_2[1])
    k2 = get_incline_coefficient(vertex_2[0], vertex_2[1], vertex_3[0], vertex_3[1])
    k3 = get_incline_coefficient(vertex_3[0], vertex_3[1], vertex_1[0], vertex_1[1])
    return k1, k2, k3


def get_similar_line(triangle, incline_coefficient, epsilon=10):
    vertex_1 = triangle[0][0]
    vertex_2 = triangle[1][0]
    vertex_3 = triangle[2][0]
    k1 = get_incline_coefficient(vertex_1[0], vertex_1[1], vertex_2[0], vertex_2[1])
    k2 = get_incline_coefficient(vertex_2[0], vertex_2[1], vertex_3[0], vertex_3[1])
    k3 = get_incline_coefficient(vertex_3[0], vertex_3[1], vertex_1[0], vertex_1[1])
    similar_line = None
    if abs(incline_coefficient - k1) / abs(incline_coefficient) * 100 < epsilon:
        similar_line = [vertex_1[0], vertex_1[1], vertex_2[0], vertex_2[1]]
    elif abs(incline_coefficient - k2) / abs(incline_coefficient) * 100 < epsilon:
        similar_line = [vertex_2[0], vertex_2[1], vertex_3[0], vertex_3[1]]
    elif abs(incline_coefficient - k3) / abs(incline_coefficient) * 100 < epsilon:
        similar_line = [vertex_3[0], vertex_3[1], vertex_1[0], vertex_1[1]]
    return similar_line


def intersection_point(line_1, line_2):
    x1, y1, x2, y2 = line_1[0], line_1[1], line_1[2], line_1[3]
    x3, y3, x4, y4 = line_2[0], line_2[1], line_2[2], line_2[3]
    px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / ((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4))
    py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / ((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4))
    return px, py


def distance_from_point_to_line(line, point):
    x0, y0 = point
    x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
    distance = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1) / ((y2 - y1)**2 + (x2 - x1)**2)**0.5
    return distance


def sign(value):
    if value > 0:
        return 1
    elif value < 1:
        return -1
    else:
        return 0


def side_check(line, point):
    x0, y0 = point
    x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
    position = sign((x2 - x1) * (y0 - y1) - (y2 - y1) * (x0 - x1))
    return position


def get_middle(line):
    x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    return mid_x, mid_y


def get_furthest_line(main_line, lines):
    furthest_line = None
    max_dist = -1
    for line in lines:
        midpoint = get_middle(line)
        distance = distance_from_point_to_line(main_line, midpoint)
        if distance > max_dist:
            max_dist = distance
            furthest_line = line
    return furthest_line


def get_closest_point(line, point):
    x0, y0 = point
    x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
    a_to_p = [x0 - x1, y0 - y1]
    a_to_b = [x2 - x1, y2 - y1]
    atb2 = a_to_b[0] ** 2 + a_to_b[1] ** 2
    atp_dot_atb = a_to_p[0] * a_to_b[0] + a_to_p[1] * a_to_b[1]
    t = atp_dot_atb / atb2
    return x1 + a_to_b[0]*t, y1 + a_to_b[1]*t


def get_perspective_point(main_triangle, triangles):
    main_vertex_1 = main_triangle[0][0]
    main_vertex_2 = main_triangle[1][0]
    main_line = [main_vertex_1[0], main_vertex_1[1], main_vertex_2[0], main_vertex_2[1]]
    main_incline = get_incline_coefficient(main_line[0], main_line[1], main_line[2], main_line[3])
    similar_lines = []
    for triangle in triangles:
        similar_line = get_similar_line(triangle, main_incline)
        if similar_line:
            similar_lines.append(similar_line)
    furthest_line = get_furthest_line(main_line, similar_lines)
    intersection_with_furthest = intersection_point(main_line, furthest_line)
    furthest_middle = get_middle(furthest_line)
    closest_side_point = get_closest_point(main_line, furthest_middle)
    center_line = [furthest_middle[0], furthest_middle[1], closest_side_point[0], closest_side_point[1]]
    correct_side = side_check(center_line, intersection_with_furthest)
    intersection_points = []
    for line in similar_lines:
        intersection = intersection_point(line, main_line)
        side = side_check(center_line, intersection)
        if side == correct_side:
            intersection_points.append(intersection)
    average_intersection = [0, 0]
    for intersection in intersection_points:
        average_intersection[0] += intersection[0]
        average_intersection[1] += intersection[1]
    average_intersection[0] /= len(intersection_points)
    average_intersection[1] /= len(intersection_points)
    return tuple(average_intersection)


def warp(img, main_triangle, triangles):
    perspective_point = get_perspective_point(main_triangle, triangles)
    main_vertex_1 = main_triangle[0][0]
    main_vertex_2 = main_triangle[1][0]
    main_vertex_3 = main_triangle[2][0]
    # cv2.putText(img, '1', (main_vertex_1[0], main_vertex_1[1]), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
    # cv2.putText(img, '2', (main_vertex_2[0], main_vertex_2[1]), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
    # cv2.putText(img, '3', (main_vertex_3[0], main_vertex_3[1]), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
    middle_point = get_middle([main_vertex_2[0], main_vertex_2[1], main_vertex_3[0], main_vertex_3[1]])
    intersection = intersection_point([perspective_point[0], perspective_point[1], middle_point[0], middle_point[1]],
                                      [main_vertex_1[0], main_vertex_1[1], main_vertex_3[0], main_vertex_3[1]])

    size = img.shape[1]
    tri_side = size
    tri_height = 3 ** 0.5 / 2 * tri_side
    pos_x, pos_y = size / 2, size / 2

    target = np.array([[0, pos_y + tri_height / 2],
                       [tri_side, pos_y + tri_height / 2],
                       [tri_side / 4, pos_y],
                       [tri_side / 4 * 3, pos_y]]).astype(np.float32)

    source_points = np.array([[main_vertex_1[0], main_vertex_1[1]],
                              [main_vertex_2[0], main_vertex_2[1]],
                              [intersection[0], intersection[1]],
                              [middle_point[0], middle_point[1]]]).astype(np.float32)

    warp_mat = cv2.getPerspectiveTransform(source_points, target)
    perspective_correction = cv2.warpPerspective(img, warp_mat, (img.shape[1], img.shape[0]))
    vertex_3_new = get_coordinates_after_perspective_transform(tuple(main_vertex_3), warp_mat)
    source_points = np.array([[0, pos_y + tri_height / 2],
                              [tri_side, pos_y + tri_height / 2],
                              [vertex_3_new[0], vertex_3_new[1]]]).astype(np.float32)
    target = np.array([[0, pos_y + tri_height / 2],
                       [tri_side, pos_y + tri_height / 2],
                       [tri_side / 2, pos_y - tri_height / 2]]).astype(np.float32)
    warp_mat = cv2.getAffineTransform(source_points, target)
    affine_correction = cv2.warpAffine(perspective_correction, warp_mat, (img.shape[1], img.shape[0]))
    return affine_correction


def scan(img):
    side = min(img.shape[:2:])
    img = img[img.shape[0] // 2 - side // 2: img.shape[0] // 2 + side // 2,
              img.shape[1] // 2 - side // 2: img.shape[1] // 2 + side // 2]
    # show_image(img)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # show_image(img_gray)
    img_blur = cv2.blur(img_gray, (5, 5))
    # show_image(img_blur)
    img_light = cv2.equalizeHist(img_blur)
    # show_image(img_light)
    ret, thresh = cv2.threshold(img_light, 180, 220, cv2.THRESH_BINARY)
    # show_image(thresh)
    img_edged = cv2.Canny(thresh, 30, 200)
    # show_image(img_edged)
    contours, hierarchy = cv2.findContours(img_edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    triangles = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        if len(approx) == 3:
            triangles.append(approx)
    triangles.sort(key=cv2.contourArea, reverse=True)
    main_triangle = triangles[0]
    img_blur = cv2.blur(img_gray, (6, 6))
    # show_image(img_blur)
    ret, thresh = cv2.threshold(img_blur, 180, 220, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    triangles = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        if len(approx) == 3 and cv2.contourArea(approx) < cv2.contourArea(main_triangle) / 3:
            triangles.append(approx)
    triangles.sort(key=cv2.contourArea, reverse=True)
    img_copy = img.copy()
    cv2.drawContours(img_copy, [main_triangle], -1, (0, 255, 0), 3)
    # show_image(img)
    cv2.drawContours(img_copy, triangles, -1, (0, 255, 0), 3)
    show_image(img_copy)
    img_warped = warp(img, main_triangle, triangles)
    show_image(img_warped)
    return img_warped


if __name__ == '__main__':
    source_image = cv2.imread('Resources/Code-Photo-1.jpg')
    res = scan(source_image)
    res = scan(res)
    res = scan(res)
