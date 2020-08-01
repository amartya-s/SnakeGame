import random

from SnakeGame.constants.direction import Direction
from SnakeGame.actors.snake import Snake, Segment
from SnakeGame.actors.food import Food

SNAKE_INIT_COORD = (100,100)
FOOD_INIT_COORD = (500, 100)

class Controller:
    def __init__(self, board):
        self.board = board
        self.snake = None
        self.food = None

        self.setup_game()

    def setup_game(self):
        self.add_snake()
        self.add_food()

    def run(self):
        self.snake.set_direction(Direction.RIGHT)
        self.snake.move()

    def is_ovaerlapping(self, x1,y1,x2,y2,i1,j1,i2,j2):
        # left-right overlapping
        if x1 >= i2 or i1 >= x2:
            return  False

        # top-bottom collision
        if y1 >= j2 or j1 >= y2:
            return False

        return True

    def collision_callback_fn(self):
        snake_head = self.snake.head
        snake_head_coords = snake_head.coords

        food_coords = tuple(self.board.coords(self.food.index))

        # collision with itself
        for segment in self.snake.segments:

            if snake_head.index == segment.index:
                continue

            is_overlapping = self.is_ovaerlapping(*(snake_head_coords + segment.coords))

            if is_overlapping:
                print("Overlapped with head: {}".format(snake_head.index))
                self.snake.set_property(segments=[snake_head, segment], **{'fill':'Red'})
                self.end_game()

        # collision with food
        is_overlapping = self.is_ovaerlapping(*(snake_head_coords+food_coords))
        if is_overlapping:
            self.snake.add_tail()
            self.add_food()

            if len(self.snake.segments) % Snake.SPEED_INCREMENT_SEGMENT_COUNT == 0:
                self.snake.increment_speed()

    def add_snake(self):

        self.snake = Snake(self.board, self.collision_callback_fn)
        self.snake.add_head(False, *(SNAKE_INIT_COORD))


    def add_food(self):

        # destroy food (if existing)
        if self.food:
            self.food.destroy()

        x=random.randint(20, self.board.width-20)
        y=random.randint(20, self.board.height-20)

        # self.board.update()
        #
        # x,y=self.board.width-20,self.board.height-20
        # x,y=self.board.height,self.board.width

        food = Food(self.board, *(x,y))
        self.food = food

    def move_snake(self, direction):
        self.snake.set_direction(direction)

    def end_game(self):
        self.snake.freeze()