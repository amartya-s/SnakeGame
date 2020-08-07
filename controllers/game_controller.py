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
        self.snake_direction = Direction.RIGHT

        self.setup_game()

    def setup_game(self):
        self.add_snake()
        self.add_food()

    def run(self):
        self.move_snake()

    def is_ovaerlapping(self, x1,y1,x2,y2,i1,j1,i2,j2):
        # left-right overlapping
        if x1 >= i2 or i1 >= x2:
            return  False

        # top-bottom collision
        if y1 >= j2 or j1 >= y2:
            return False

        return True

    def check_collision(self):
        snake_head = self.snake.head
        snake_head_coords = snake_head.coords

        food_coords = self.food.coords
        print(food_coords)

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
            self.snake.add_segment(is_head=False, direction=self.snake_direction)
            self.add_food()

            if len(self.snake.segments) % Snake.SPEED_INCREMENT_SEGMENT_COUNT == 0:
                self.snake.increment_speed()

    def add_snake(self):

        self.snake = Snake(self.board)
        self.snake.add_segment(is_head=True,direction=self.snake_direction, **{'snake_init_coords': SNAKE_INIT_COORD})
        self.snake.add_segment(is_head=False, direction=self.snake_direction)

    def add_food(self):

        # destroy food (if existing)
        if self.food:
            self.food.destroy()
            del self.food

        x=random.randint(Food.FOOD_WIDTH, self.board.width-20)
        y=random.randint(Food.FOOD_WIDTH, self.board.height-20)


        food = Food(self.board, *(x,y))
        self.food = food

    def change_direction(self, direction):
        snake_direction = self.snake_direction
        if (snake_direction == Direction.RIGHT and direction == Direction.LEFT) \
                or (snake_direction == Direction.LEFT and direction == Direction.RIGHT) \
                or (snake_direction == Direction.UP and direction == Direction.DOWN)\
                or (snake_direction == Direction.DOWN and direction == Direction.UP):
            print("Keypress {} blocked".format(direction))
            return

        self.snake_direction = direction
        print("Direction set to {}".format(self.snake_direction))

    def move_snake(self):

        if self.snake.is_frozen:
            return

        self.check_collision()

        self.snake.add_segment(True, self.snake_direction)

        self.snake.remove_tail()

        self.board.after(self.snake.speed, lambda: self.move_snake())


    def end_game(self):
        self.snake.freeze()