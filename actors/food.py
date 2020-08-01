from SnakeGame.constants.shape import Shape

FOOD_WIDTH = 30

class Food:
    def __init__(self, board, x_cord, y_cord, shape=Shape.RECTANGlE):
        self.board = board
        self.x = x_cord
        self.y = y_cord
        self.shape = shape

        self.index = None

        self.create()

    def create(self):
        rectangle_cords = self.x-FOOD_WIDTH/2, self.y-FOOD_WIDTH/2,self.x+FOOD_WIDTH/2,self.y+FOOD_WIDTH/2
        if self.shape == Shape.RECTANGlE:
            self.index = self.board.create_rectangle(rectangle_cords, fill='brown')
        if self.shape == Shape.OVAL:
            self.index = self.board.create_oval(rectangle_cords, fill='red')

    def destroy(self):
        self.board.delete(self.index)