import time
from PIL import ImageTk

from SnakeGame.utils.image_processor import ImageProcessor
from SnakeGame.utils.timer import CustomTimer


class Bomb:
    WIDTH = 50
    IMAGE = None
    IMAGE_PATH = r'C:\Users\Amartya\PycharmProjects\Projects\SnakeGame\images\bomb.jpg'

    def __init__(self, board, x_cord, y_cord):
        self.board = board
        self.x = x_cord
        self.y = y_cord
        self.is_live = False
        self.index = None
        self.timer = None
        self.time_left = None
        self.coords = ()

    def get_photo(self):
        if Bomb.IMAGE:
            return Bomb.IMAGE

        masked = ImageProcessor.automask(Bomb.IMAGE_PATH, height=Bomb.WIDTH, width=Bomb.WIDTH)[0]

        photo = ImageTk.PhotoImage(masked)

        Bomb.IMAGE = photo

        return photo

    def create(self, duration):
        rectangle_cords = self.x-Bomb.WIDTH/2, self.y-Bomb.WIDTH/2,self.x+Bomb.WIDTH/2,self.y+Bomb.WIDTH/2

        photo = self.get_photo()
        self.img = photo
        self.index = self.board.create_image(self.x, self.y, image=photo,anchor='center')

        self.coords = rectangle_cords
        self.time_left = duration

        # destroy after "duration"s have passed
        t=CustomTimer(duration/1000, self.destroy)

        self.timer = t
        self.timer.start()

        self.is_live = True

    def pause(self):
        self.timer.pause()
        print("Timer paused")

    def resume(self):
        self.timer.resume()

    def destroy(self):
        self.board.delete(self.index)
        self.is_live = False