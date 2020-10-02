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


def scan(path):
    img = cv2.imread(path)
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
    contours.sort(key=cv2.contourArea, reverse=True)
    cv2.drawContours(img, contours[0], -1, (0, 255, 0), 10)
    show_image(img)


if __name__ == '__main__':
    scan('Resources/Code-Photo.jpg')
