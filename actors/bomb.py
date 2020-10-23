from PIL import ImageTk

from SnakeGame.utils.image_processor import ImageProcessor
from SnakeGame.utils.timer import CustomTimer
from SnakeGame.constants.game_params import GameParams

class Bomb:
    WIDTH = 50
    IMAGE = None

    def __init__(self, board, x_cord, y_cord):
        self.board = board
        self.x = x_cord
        self.y = y_cord
        self.is_live = False
        self.index = None
        self.coords = ()

    def get_photo(self):
        if Bomb.IMAGE:
            return Bomb.IMAGE

        masked = ImageProcessor.automask(GameParams.IMAGE_PATH_BOMB, height=Bomb.WIDTH, width=Bomb.WIDTH)[0]

        photo = ImageTk.PhotoImage(masked)

        Bomb.IMAGE = photo

        return photo

    def create(self, duration):
        rectangle_cords = self.x-Bomb.WIDTH/2, self.y-Bomb.WIDTH/2,self.x+Bomb.WIDTH/2,self.y+Bomb.WIDTH/2

        photo = self.get_photo()
        self.img = photo
        self.index = self.board.create_image(self.x, self.y, image=photo,anchor='center')

        self.coords = rectangle_cords

        # destroy after "duration"s have passed
        self.timer = CustomTimer(duration/1000, self.destroy)
        self.timer.start()

        self.is_live = True

    def pause(self):
        self.timer.pause()

    def resume(self):
        self.timer.resume()

    def destroy(self):
        self.board.delete(self.index)
        self.is_live = False

    def get_pickleble_data(self):
        data = dict()
        data['x'] = self.x
        data['y'] = self.y
        data['time_left'] = self.timer.get_time_left()

        return data

    @staticmethod
    def reconstruct(board, **kwargs):
        x = kwargs['x']
        y = kwargs['y']
        time_left = kwargs['time_left']

        bomb_obj = Bomb(board, x, y)
        bomb_obj.create(time_left)
        bomb_obj.pause()

        print ("Bomb reconstructed at -{}".format(bomb_obj.coords))

        return bomb_obj