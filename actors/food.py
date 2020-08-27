from PIL import ImageTk, Image
from SnakeGame.constants.shape import Shape
from SnakeGame.service.image_processor import ImageProcessor


class Food:
    FOOD_WIDTH = 80
    IMAGE = None
    IMAGE_PATH = r'C:\Users\Amartya\PycharmProjects\Projects\SnakeGame\images\rat.jpg'

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

        masked = ImageProcessor.automask(Food.IMAGE_PATH, height=Food.FOOD_WIDTH, width=Food.FOOD_WIDTH)[0]

        Food.IMAGE = ImageTk.PhotoImage(masked)

        return Food.IMAGE

    def update(self,ind, label):
        frame = self.frames[ind]
        ind += 1
        if ind > len(self.frames):  # With this condition it will play gif infinitely
            ind = 1
        print(frame)
        label.configure(image=frame)
        self.board.after(100, self.update, ind, label)

    def create(self):
        rectangle_cords = self.x-Food.FOOD_WIDTH/2, self.y-Food.FOOD_WIDTH/2,self.x+Food.FOOD_WIDTH/2,self.y+Food.FOOD_WIDTH/2
        if self.shape == Shape.RECTANGlE:
            photo = self.get_photo()

            self.index = self.board.create_image(self.x, self.y, image=photo,anchor='center')
            #label = tk.Label(self.board)
            #label_window = self.board.create_window(self.x, self.y, window=label)
            #self.update(0, label)

        if self.shape == Shape.OVAL:
            self.index = self.board.create_oval(rectangle_cords, fill='red')

        self.coords = rectangle_cords

    def destroy(self):
        self.board.delete(self.index)