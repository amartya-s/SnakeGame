import random
import copy
import datetime

from SnakeGame.constants.direction import Direction
from SnakeGame.actors.snake import Snake, Segment
from SnakeGame.actors.food import Food
from SnakeGame.actors.bomb import Bomb
from SnakeGame.constants.game_states import States
from SnakeGame.controllers.datastore import DataStoreManager


SNAKE_INIT_COORD = (600,200)
FOOD_INIT_COORD = (500, 100)


class Controller:
    def __init__(self):
        self.board = None
        self.snake = None
        self.food = None
        self.bomb_by_index = dict()
        self.snake_direction = None
        self.state = States.NOT_STARTED
        self.score_label = None
        self.data_store = None

    def run(self, inst=datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')):
        self.setup_game()
        self.data_store = DataStoreManager(inst)
        self.score_label.set(str(self.data_store.get_score()))

    def setup_game(self):
        self.add_snake()
        self.add_food()
        self.randomly_add_bomb()

    def pause(self):
        for index, bomb in self.bomb_by_index.items():
            bomb.pause()

        self.state = States.PAUSED

        print("Game Paused")

    def resume(self):
        for index, bomb in self.bomb_by_index.items():
            bomb.resume()

        self.state = States.RUNNING

        print("Game resumed")

    def pause_and_resume(self):
        if self.state in [States.PAUSED]:
            self.resume()
        elif self.state in [States.RUNNING]:
            self.pause()

    def is_overlaping(self, x1, y1, x2, y2, i1, j1, i2, j2):
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

        # collision with itself
        for segment in self.snake.segments:

            if snake_head.index == segment.index:
                continue

            is_overlapping = self.is_overlaping(*(snake_head_coords + segment.coords))

            if is_overlapping:
                print("Overlapped with head: {}".format(snake_head.index))
                self.snake.set_property(segments=[snake_head, segment], **{'fill':'Red'})
                self.end_game()

        # collision with food
        is_overlapping = self.is_overlaping(*(snake_head_coords + food_coords))
        if is_overlapping:
            self.snake.add_segment(Segment.TAIL, direction=self.snake_direction)
            self.add_food()

            if len(self.snake.segments) % Snake.SPEED_INCREMENT_SEGMENT_COUNT == 0:
                self.snake.increment_speed()
                self.update_score(10,snake_head_coords, )
            else:
                self.update_score(1,snake_head_coords)

        # collision with bomb
        bomb_by_index_copy = copy.copy(self.bomb_by_index)

        for index, bomb in self.bomb_by_index.items():
            # del non-existent references of bomb
            if not bomb.is_live:
                del bomb_by_index_copy[index]
            else:
                bomb_coords = bomb.coords
                snake_head_coords = self.snake.head.coords
                is_overlapping = self.is_overlaping(*(snake_head_coords + bomb_coords))

                if is_overlapping:
                    print("Bomb {} overlapped with head: {}".format(index,snake_head.index))
                    self.end_game()
                    break

        self.bomb_by_index = bomb_by_index_copy

    def add_snake(self):

        self.snake = Snake(self.board)
        self.snake.add_segment(segment_type=Segment.HEAD,direction=Direction.RIGHT, **{'snake_init_coords': SNAKE_INIT_COORD})
        self.snake.add_segment(segment_type=Segment.BODY, direction=Direction.RIGHT)
        self.snake.add_segment(segment_type=Segment.BODY, direction=Direction.RIGHT)
        self.snake.add_segment(segment_type=Segment.BODY, direction=Direction.RIGHT)
        self.snake.add_segment(segment_type=Segment.BODY, direction=Direction.RIGHT)
        self.snake.add_segment(segment_type=Segment.TAIL, direction=Direction.RIGHT)

        print(self.snake)

    def add_food(self):

        # destroy food (if existing)
        if self.food:
            self.food.destroy()
            del self.food

        x=random.randint(Food.FOOD_WIDTH/2, self.board.width-Food.FOOD_WIDTH/2)
        y=random.randint(Food.FOOD_WIDTH/2, self.board.height-Food.FOOD_WIDTH/2)

        food = Food(self.board, *(x,y))
        self.food = food

    def add_bomb(self):
        x=random.randint(Bomb.WIDTH/2, self.board.width-Bomb.WIDTH/2)
        y=random.randint(Bomb.WIDTH/2, self.board.height-Bomb.WIDTH/2)

        # y=random.randint(self.snake.head.coords[1], self.snake.head.coords[3])

        bomb_coords = (x-Bomb.WIDTH/2, y-Bomb.WIDTH/2,x+Bomb.WIDTH/2,y+Bomb.WIDTH/2)
        snake_head_coords = self.snake.head.coords

        # should not overlap with food
        if self.is_overlaping(*(self.food.coords + bomb_coords)):
            print("bomb overlapping with food")
            self.add_bomb()
            return

        # should not overlap with any segment of snake
        for segment in self.snake.segments:
            if self.is_overlaping(*(segment.coords + bomb_coords)):
                print("Bomb overlapping with snake")
                self.add_bomb()
                return

        # should not be in the direction snake is moving
        if self.snake.head.original_direction in [Direction.LEFT, Direction.RIGHT] and (
                snake_head_coords[1] <= bomb_coords[1] <= snake_head_coords[3] or snake_head_coords[1] <= bomb_coords[3] <= snake_head_coords[3]
            or (bomb_coords[1] <= snake_head_coords[1] and bomb_coords[3] >= snake_head_coords[3])
        ):
            print("Bomb overlapping with direction snake is moving")
            self.add_bomb()
            return
        if self.snake.head.original_direction in [Direction.UP, Direction.DOWN] and (
                snake_head_coords[0] <= bomb_coords[0] <= snake_head_coords[2] or snake_head_coords[0] <= bomb_coords[2] <= snake_head_coords[2]
                or (bomb_coords[0] <= snake_head_coords[0] and bomb_coords[2] >= snake_head_coords[2])
        ):
            print("Bomb overlapping with direction snake is moving")
            self.add_bomb()
            return

        bomb = Bomb(self.board, x, y)
        bomb.create(duration=random.randint(3000,10000))

        self.bomb_by_index[bomb.index] = bomb

    def change_direction(self, direction):
        if self.state == States.NOT_STARTED:
            self.state = States.RUNNING
            self.snake_direction = direction
            self.move_snake()
            print("snake moving")
            return

        snake_direction = self.snake_direction
        if (snake_direction == Direction.RIGHT and direction == Direction.LEFT) \
                or (snake_direction == Direction.LEFT and direction == Direction.RIGHT) \
                or (snake_direction == Direction.UP and direction == Direction.DOWN)\
                or (snake_direction == Direction.DOWN and direction == Direction.UP):
            return

        self.snake_direction = direction

    def move_snake(self):

        if self.state == States.RUNNING:
            self.check_collision()
            prev_head = self.snake.head
            self.snake.add_segment(Segment.HEAD, self.snake_direction)
            new_head = self.snake.head

            #self.board.create_line(prev_head.coords[0],prev_head.coords[1], new_head.coords[0],new_head.coords[1], fill='white' )
            #self.board.create_line(prev_head.coords[2],prev_head.coords[3], new_head.coords[2],new_head.coords[3] , fill='white')

            self.snake.remove_tail()

        self.board.after(self.snake.speed, lambda: self.move_snake())

    def randomly_add_bomb(self):
        if self.state in [States.RUNNING]:
            self.add_bomb()

        self.board.after(random.randint(10000, 50000), lambda: self.randomly_add_bomb())

    @staticmethod
    def val(c):
        if c >= '0' and c <= '9':
            return ord(c) - ord('0')
        else:
            return ord(c) - ord('a') + 10;

            # Function to convert a number

    @staticmethod
    # from given base 'b' to decimal
    def toDeci(hex):

        power = 1  # Initialize power of base
        num = 0  # Initialize result

        num = Controller.val(hex[1]) + Controller.val(hex[0])*16

        return num

    def animate_score_box(self, score_box_id, score_text_id):
        self.board.move(score_box_id, 0, -1)
        self.board.move(score_text_id, 0, -1)
        fill = self.board.itemcget(score_box_id, 'fill')
        redValue, blueValue, greenValue = Controller.toDeci(fill[1:3]), Controller.toDeci(fill[3:5]), Controller.toDeci(fill[5:7])
        redValue = redValue + 5 if redValue < 255 else 255
        blueValue = blueValue + 5 if blueValue < 255 else 255
        greenValue = greenValue + 5 if greenValue < 255 else 255

        backgroundColor = "#%02x%02x%02x" % (redValue, blueValue, greenValue)

        fill = self.board.itemconfig(score_box_id, **{'fill': backgroundColor})

        if redValue == greenValue == blueValue == 255:
            self.board.delete(score_box_id)
            self.board.delete(score_text_id)
            return

        self.board.after(10, lambda: self.animate_score_box( score_box_id, score_text_id))

    def update_score(self, increment_by,snake_head_coord):
        score = int(self.score_label.get()) + increment_by
        self.score_label.set(str(score))

        score_bubble_coord = snake_head_coord[0]-15, snake_head_coord[1]-15, snake_head_coord[2]+15, snake_head_coord[3]+15
        score_bubble = self.board.create_oval(score_bubble_coord, fill="#%02x%02x%02x" % (0, 100, 255) )

        score_text_coords = score_bubble_coord[0]+(score_bubble_coord[2]-score_bubble_coord[0])/2, score_bubble_coord[1]+(score_bubble_coord[3]-score_bubble_coord[1])/2
        print(self.board)
        print(score_text_coords)
        print(increment_by)
        score_text = self.board.create_text(score_text_coords, fill="blue",font="Times 20  bold", text='+{}'.format(increment_by))
        print(score_text)
        self.animate_score_box(score_bubble, score_text)


    def end_game(self):
        self.state = States.END

        for index, bomb in self.bomb_by_index.items():
            bomb.pause()