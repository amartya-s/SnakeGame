import sys
import random
import copy
import traceback
import datetime

import tkinter as tk

from SnakeGame.constants.direction import Direction
from SnakeGame.actors.snake import Snake, Segment
from SnakeGame.utils.animation import AnimationUtil
from SnakeGame.actors.food import Food, AutoDestroyableFood
from SnakeGame.actors.bomb import Bomb
from SnakeGame.constants.game_states import States
from SnakeGame.constants.game_params import GameParams
from SnakeGame.controllers.datastore import DataStoreManager


class Controller:
    def __init__(self):
        self.board = None
        self.snake = None
        self.food = None
        self.foods_with_timers = []
        self.bomb_by_index = dict()
        self.state = States.NOT_STARTED
        self.score_label = None
        self.data_store = None

    def set_datastore(self, inst):
        self.data_store = DataStoreManager(inst)

    def start_new_game(self):
        self.setup_game()
        #self.score_label.set(str(self.score_label.get()))

    def setup_game(self):
        self.add_snake()
        self.add_food()

    def pause(self):
        for index, bomb in self.bomb_by_index.items():
            bomb.pause()

        for food in self.foods_with_timers:
            food.pause()

        self.state = States.PAUSED

        print("Game Paused")

    def resume(self):
        for index, bomb in self.bomb_by_index.items():
            bomb.resume()
        for food in self.foods_with_timers:
            food.resume()

        self.state = States.RUNNING

        self.board.after(self.snake.speed, lambda: self.move_snake())

        self.board.after(random.randint(GameParams.BOMB_DURATION_MIN_MAX[0], GameParams.BOMB_DURATION_MIN_MAX[1]),
                         lambda: self.randomly_add_bomb())

        duration = random.randint(GameParams.RANDOM_FOOD_WITH_TIMER_AFTER_DURATION_MIN_MAX[0],
                                  GameParams.RANDOM_FOOD_WITH_TIMER_AFTER_DURATION_MIN_MAX[1])
        self.board.after(duration, lambda: self.randomly_add_food_with_timer())

        print("Game resumed")

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
            self.snake.add_segment(Segment.TAIL, direction=self.snake.head.direction)
            self.add_food()

            if len(self.snake.segments) % GameParams.SPEED_INCREMENT_SEGMENT_COUNT == 0 and self.snake.speed >= GameParams.MAX_SNAKE_SPEED:
                self.snake.increment_speed(increment_by=GameParams.SPEED_INCREMENT_FACTOR)

            self.update_score(GameParams.FOOD_SCORE,snake_head_coords)

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

        # collision with destroyable food
        foods_with_timers = []
        for food in self.foods_with_timers:
            # del non-existent references of food
            if not food.is_live:
                del food
            else:
                food_coords = food.coords
                is_overlapping = self.is_overlaping(*(snake_head_coords + food_coords))
                if is_overlapping:
                    food.destroy()
                    self.update_score(GameParams.FOOD_WITH_TIMER_SCORE,snake_head_coords)
                else:
                    foods_with_timers.append(food)

        # Warning: self.foods_with_timers might got updated
        self.foods_with_timers = foods_with_timers

    def add_snake(self):
        self.snake = Snake(self.board)
        self.snake.add_segment(segment_type=Segment.HEAD,direction=Direction.RIGHT, **{'snake_init_coords': GameParams.SNAKE_INIT_COORD})
        self.snake.add_segment(segment_type=Segment.BODY, direction=Direction.RIGHT)
        self.snake.add_segment(segment_type=Segment.BODY, direction=Direction.RIGHT)
        self.snake.add_segment(segment_type=Segment.BODY, direction=Direction.RIGHT)
        self.snake.add_segment(segment_type=Segment.BODY, direction=Direction.RIGHT)
        self.snake.add_segment(segment_type=Segment.TAIL, direction=Direction.RIGHT)

        print(self.snake)

    def add_food(self, auto_destroy_duration=0):

        # destroy food (if existing) -> only if it's a non-destroyable food
        if self.food and auto_destroy_duration == 0:
            self.food.destroy()
            del self.food

        x = random.randint(GameParams.FOOD_WIDTH/2, self.board.width-GameParams.FOOD_WIDTH/2)
        y = random.randint(GameParams.FOOD_WIDTH/2, self.board.height-GameParams.FOOD_WIDTH/2)

        # check if it's food_with_timer and if it collides with food_without_timer,
        # then recursively call add_food with duration
        if auto_destroy_duration != 0 and \
                self.is_overlaping(*((x-GameParams.FOOD_WIDTH/2, y-GameParams.FOOD_WIDTH/2, x+GameParams.FOOD_WIDTH/2, y+GameParams.FOOD_WIDTH/2) + self.food.coords)):
            self.add_food(auto_destroy_duration=auto_destroy_duration)

        if auto_destroy_duration == 0:
            food = Food(self.board, *(x, y))
            food.create()
            self.food = food
        else:
            food = AutoDestroyableFood(self.board, auto_destroy_duration, *(x, y))
            food.create()
            self.foods_with_timers.append(food)
            print("food with timer added with duration {}s".format(auto_destroy_duration/1000))

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
        if self.snake.head.direction in [Direction.LEFT, Direction.RIGHT] and (
                snake_head_coords[1] <= bomb_coords[1] <= snake_head_coords[3] or snake_head_coords[1] <= bomb_coords[3] <= snake_head_coords[3]
            or (bomb_coords[1] <= snake_head_coords[1] and bomb_coords[3] >= snake_head_coords[3])
        ):
            print("Bomb overlapping with direction snake is moving")
            self.add_bomb()
            return
        if self.snake.head.direction in [Direction.UP, Direction.DOWN] and (
                snake_head_coords[0] <= bomb_coords[0] <= snake_head_coords[2] or snake_head_coords[0] <= bomb_coords[2] <= snake_head_coords[2]
                or (bomb_coords[0] <= snake_head_coords[0] and bomb_coords[2] >= snake_head_coords[2])
        ):
            print("Bomb overlapping with direction snake is moving")
            self.add_bomb()
            return

        bomb = Bomb(self.board, x, y)
        duration = random.randint(GameParams.BOMB_DURATION_MIN_MAX[0], GameParams.BOMB_DURATION_MIN_MAX[1])
        bomb.create(duration=duration)

        print('Bomb added with with duration: {}'.format(duration/1000))

        self.bomb_by_index[bomb.index] = bomb

    def change_direction(self, direction):
        if self.state == States.NOT_STARTED:
            self.state = States.RUNNING
            self.move_snake()
            print("snake moving")

            self.randomly_add_bomb()
            self.randomly_add_food_with_timer()

            return

        if self.state != States.RUNNING:
            return

        snake_direction = self.snake.head.direction
        if (snake_direction == Direction.RIGHT and direction == Direction.LEFT) \
                or (snake_direction == Direction.LEFT and direction == Direction.RIGHT) \
                or (snake_direction == Direction.UP and direction == Direction.DOWN)\
                or (snake_direction == Direction.DOWN and direction == Direction.UP):
            return

        self.snake.head.change_direction(direction)

    def move_snake(self):

        if self.state != States.RUNNING:
            return

        self.check_collision()
        prev_head = self.snake.head
        self.snake.add_segment(Segment.HEAD, self.snake.head.direction)
        new_head = self.snake.head
        self.snake.remove_tail()

        self.board.after(self.snake.speed, lambda: self.move_snake())

    def randomly_add_bomb(self):
        if self.state not in [States.RUNNING]:
            return

        self.add_bomb()
        duration = random.randint(GameParams.RANDOM_BOMB_AFTER_DURATION_MIN_MAX[0], GameParams.RANDOM_BOMB_AFTER_DURATION_MIN_MAX[1])
        print("Will add bomb after {}s".format(duration/1000))
        self.board.after(duration, lambda: self.randomly_add_bomb())

    def randomly_add_food_with_timer(self):
        if self.state not in [States.RUNNING]:
            return

        if len(self.foods_with_timers) < GameParams.FOOD_WITH_TIMERS_ALLOWED_AT_SAME_TIME:
            duration = random.randint(GameParams.FOOD_WITH_TIMER_DURATION_MIN_MAX[0], GameParams.FOOD_WITH_TIMER_DURATION_MIN_MAX[1]) # in ms
            self.add_food(auto_destroy_duration=duration)

        duration = random.randint(GameParams.RANDOM_FOOD_WITH_TIMER_AFTER_DURATION_MIN_MAX[0], GameParams.RANDOM_FOOD_WITH_TIMER_AFTER_DURATION_MIN_MAX[1])
        print('Will add food with timer after - {}s'.format(duration/1000))
        self.board.after(duration, lambda: self.randomly_add_food_with_timer())

    def update_score(self, increment_by,snake_head_coord):
        score = int(self.score_label.get()) + increment_by
        self.score_label.set(str(score))

        score_bubble_coord = snake_head_coord[0]-15, snake_head_coord[1]-15, snake_head_coord[2]+15, snake_head_coord[3]+15
        score_bubble = self.board.create_oval(score_bubble_coord, fill="#%02x%02x%02x" % (0, 100, 255) )

        score_text_coords = score_bubble_coord[0]+(score_bubble_coord[2]-score_bubble_coord[0])/2, score_bubble_coord[1]+(score_bubble_coord[3]-score_bubble_coord[1])/2

        score_text = self.board.create_text(score_text_coords, fill="#%02x%02x%02x" % (0, 0, 255),font="Times 20  bold", text='+{}'.format(increment_by))

        AnimationUtil.fade_away(self.board, score_text, Direction.UP)
        AnimationUtil.fade_away(self.board, score_bubble, Direction.UP)

    def load_game(self):
        try:
            success = self.data_store.load()
            if not success:
                return success
            score = self.data_store.get_score()
            player_data = self.data_store.get_player()
            food_data = self.data_store.get_food()
            foods_with_timer_data = self.data_store.get_foods_with_timer()
            bombs_data = self.data_store.get_bombs()

            self.snake = Snake.reconstruct(self.board, player_data)
            self.food = Food.reconstruct(self.board, **food_data)
            print("Food data: {}".format(food_data))

            for food in foods_with_timer_data:
                print("Food with timer -{}".format(food))
                food_obj = AutoDestroyableFood.reconstruct(self.board, **food)
                self.foods_with_timers.append(food_obj)
            print ("Reconstruced food_with_timer =>")
            print (self.foods_with_timers)

            for bomb in bombs_data:
                print('Reconstructing bomb: {}'.format(bomb))
                bomb_obj = Bomb.reconstruct(self.board, **bomb)
                self.bomb_by_index[bomb_obj.index] = bomb_obj
            print ("Reconstructed bombs:=")
            print (self.bomb_by_index)

            self.score_label.set(str(score))

            self.randomly_add_bomb()
            self.randomly_add_food_with_timer()

            self.state = States.PAUSED

            return True
        except Exception as e:
            print (e)
            print('Failed loading game')
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            return False

    def save_game(self):
        try:
            if not self.data_store:  # don ot set if game loaded from previous saved game
                self.set_datastore(inst=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d__%H%M%S'))

            # get food
            food = self.food.get_pickleble_data()

            # get all food with timers
            foods_with_timer = [food.get_pickleble_data() for food in self.foods_with_timers]

            # get all bombs
            bombs = [bomb.get_pickleble_data() for bomb in list(self.bomb_by_index.values()) if bomb.is_live]

            # get snake
            snake = self.snake.get_pickleble_data()

            # get score
            score = self.score_label.get()

            self.data_store.update(player=snake, bombs=bombs, food=food, foods_with_timer=foods_with_timer,score=score)

            print('game saved')
            return True
        except Exception as e:
            print("Failed saving game")
            print(e)
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            return False

    def end_game(self):
        game_over_label = tk.Label(self.board, text='GAME OVER', font="InkFree 40 bold", width=self.board.width,
                               bg='red',
                               foreground='white')
        self.board.create_window(self.board.width / 2, self.board.height / 2,
                                                    anchor=tk.CENTER,
                                                    window=game_over_label)
        self.state = States.END

        for index, bomb in self.bomb_by_index.items():
            bomb.pause()

        for food in self.foods_with_timers:
            food.pause()