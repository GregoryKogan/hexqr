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


def warp(img, triangle):
    size = img.shape[1]
    tri_side = size
    tri_height = 3 ** 0.5 / 2 * tri_side
    pos_x, pos_y = size / 2, size / 2

    target = np.array([[pos_x, pos_y - tri_height / 2],
                       [0, pos_y + tri_height / 2],
                       [size, pos_y + tri_height / 2]]).astype(np.float32)
    triangle_vertexes = [[triangle[0][0][0], triangle[0][0][1]],
                         [triangle[1][0][0], triangle[1][0][1]],
                         [triangle[2][0][0], triangle[2][0][1]]]
    triangle_vertexes_np = np.array([triangle_vertexes[0],
                                    triangle_vertexes[1],
                                    triangle_vertexes[2]]).astype(np.float32)
    print(triangle_vertexes)
    warp_mat = cv2.getAffineTransform(triangle_vertexes_np, target)
    result = cv2.warpAffine(img, warp_mat, (img.shape[1], img.shape[0]))
    return result


def scan(path):
    img = cv2.imread(path)
    side = min(img.shape[:2:])
    img = img[img.shape[0] // 2 - side // 2:
              img.shape[0] // 2 + side // 2,
              img.shape[1] // 2 - side // 2:
              img.shape[1] // 2 + side // 2]
    show_image(img)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    show_image(img_gray)
    img_blur = cv2.blur(img_gray, (5, 5))
    show_image(img_blur)
    img_blur = cv2.equalizeHist(img_blur)
    show_image(img_blur)
    ret, thresh = cv2.threshold(img_blur, 180, 220, cv2.THRESH_BINARY)
    img_edged = cv2.Canny(thresh, 30, 200)
    show_image(thresh)
    show_image(img_edged)
    contours, hierarchy = cv2.findContours(img_edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    triangles = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        if len(approx) == 3:
            triangles.append(approx)
    triangles.sort(key=cv2.contourArea, reverse=True)
    triangle = triangles[0]
    cv2.drawContours(img, [triangle], -1, (0, 255, 0), 10)
    show_image(img)
    img_warped = warp(img, triangle)
    show_image(img_warped)


if __name__ == '__main__':
    scan('Resources/Code-Photo.jpg')
