from PIL import Image, ImageDraw


def build_code(size=500):
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    width, height = img.size
    draw.polygon([(width / 2, 0), (0, height), (width, height)], fill=(255, 255, 255, 255))
    img.show()
    img.save('Code.png')


if __name__ == '__main__':
    build_code()
