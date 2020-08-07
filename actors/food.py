import tkinter
from PIL import Image, ImageTk,ImageDraw

from SnakeGame.constants.shape import Shape


class ImageProcessor:

    @staticmethod
    def color_cmp(orig, comp):
        tolerance = 5  # You can adjust color tolerance value
        inside = []
        for i in range(len(orig)):
            if (orig[i] - tolerance) <= comp[i] <= (orig[i] + tolerance):
                inside.append(True)
            else:
                inside.append(False)
        if inside.count(False):
            return 0
        else:
            return 1

    @staticmethod
    def automask(path, height, width):
        img = Image.open(path)
        img = img.resize((height, width), Image.ADAPTIVE)

        to_copare_with_pixel = img.getpixel((0, 0))
        backgroundcolor = (0, 0, 0)
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                pix_color = img.getpixel((x, y))
                if ImageProcessor.color_cmp(pix_color, to_copare_with_pixel):
                    img.putpixel((x, y), backgroundcolor)
                else:
                    img.putpixel((x, y), pix_color)
        return img


class Food:
    FOOD_WIDTH = 40
    IMAGE = None
    IMAGE_PATH = r'C:\Users\Amartya\PycharmProjects\Projects\SnakeGame\images\apple2.jpg'

    def __init__(self, board, x_cord, y_cord, shape=Shape.RECTANGlE):
        self.board = board
        self.x = x_cord
        self.y = y_cord
        self.shape = shape

        self.index = None
        self.coords = ()

        self.create()

    def get_photo(self):
        if Food.IMAGE:
            return Food.IMAGE

        masked = ImageProcessor.automask(Food.IMAGE_PATH, height=Food.FOOD_WIDTH, width=Food.FOOD_WIDTH)

        photo = ImageTk.PhotoImage(masked)

        Food.IMAGE = photo

        return photo

    def create(self):
        rectangle_cords = self.x-Food.FOOD_WIDTH/2, self.y-Food.FOOD_WIDTH/2,self.x+Food.FOOD_WIDTH/2,self.y+Food.FOOD_WIDTH/2
        if self.shape == Shape.RECTANGlE:
            photo = self.get_photo()
            self.img = photo
            self.index = self.board.create_image(self.x, self.y, image=photo,anchor='center')

        if self.shape == Shape.OVAL:
            self.index = self.board.create_oval(rectangle_cords, fill='red')

        self.coords = rectangle_cords

    def destroy(self):
        self.board.delete(self.index)