import collections

from SnakeGame.constants.shape import Shape
from SnakeGame.constants.direction import Direction


class Segment(object):
    SEGMENT_LENGTH = 30
    SEGMENT_WIDTH = 30

    def __init__(self, board, shape,direction, x, y):
            self.shape = shape
            self.board = board
            self.index = None

            self.x = self.y = None
            self.coords = ()
            self.original_direction = direction

            self.create(x, y)

    def create(self, x_coord, y_coord):
        x_diff = Segment.SEGMENT_LENGTH / 2
        y_diff = Segment.SEGMENT_WIDTH / 2

        rectangle_coords = x_coord - x_diff, y_coord - y_diff, x_coord + x_diff, y_coord + y_diff

        if self.shape == Shape.RECTANGlE:
            index = self.board.create_rectangle(rectangle_coords, fill='pink', tags=('segment'))
        if self.shape == Shape.OVAL:
            index = self.board.create_oval(rectangle_coords, fill='pink', tags=('segment'))

        self.index = index

        self.x = x_coord
        self.y = y_coord

        self.coords = rectangle_coords

    def configure(self, **kwargs):
        self.board.itemconfigure(self.index, **kwargs)

    def recreate(self, shape):
        self.board.delete(self.index)

        self.shape = shape

        if self.shape == Shape.RECTANGlE:
            index = self.board.create_rectangle(*self.coords, fill='pink', tags=('segment'))
        if self.shape == Shape.OVAL:
            index = self.board.create_oval(*self.coords, fill='pink', tags=('segment'))

        self.index = index

class Snake(object):

    SPEED_INCREMENT_SEGMENT_COUNT = 2
    SPEED_INCREMENT_FACTOR = 10

    def __init__(self, canvas, collision_callbak_fn, **properties):

        self.properties = properties
        self.canvas = canvas
        self.collision_callback_fn = collision_callbak_fn

        self.segments = collections.deque([])
        self.direction = Direction.RIGHT
        self.speed = 100

        self.head = None
        self.tail = None

        self.is_frozen = False
        self.is_changing = False

    def set_is_changing(self, is_changing):
        self.is_changing = is_changing

    def freeze(self):
        self.is_frozen = True

    def unfreeze(self):
        self.is_frozen = False
        self.move()

    def increment_speed(self):
        self.speed -= Snake.SPEED_INCREMENT_FACTOR
        print("Speed incremented: {}".format(self.speed))

    def set_direction(self, direction):
        if (self.direction == Direction.RIGHT and direction == Direction.LEFT) \
                or (self.direction == Direction.LEFT and direction == Direction.RIGHT) \
                or (self.direction == Direction.UP and direction == Direction.DOWN)\
                or (self.direction == Direction.DOWN and direction == Direction.UP):

            return

        self.direction = direction

    def set_property(self, segments, **kwargs):
        for segment in segments:
            segment.configure(**kwargs)

    def add_head(self,flag=False, *snake_init_coords):

        if not len(self.segments):
            head_coords = snake_init_coords
            prev_head = None
        else:
            head = self.segments[len(self.segments)-1]
            head_coords = head.x, head.y

            prev_head = head

        dx = dy = 0

        if self.direction == Direction.UP:
            dy= - Segment.SEGMENT_LENGTH
        if self.direction == Direction.DOWN:
            dy = Segment.SEGMENT_LENGTH
        if self.direction == Direction.LEFT:
            dx = -Segment.SEGMENT_LENGTH
        if self.direction == Direction.RIGHT:
            dx = Segment.SEGMENT_LENGTH

        x_coord_of_new_segment, y_coord_of_new_segment = head_coords[0]+dx, head_coords[1]+dy

        if x_coord_of_new_segment <= 0:
            x_coord_of_new_segment = self.canvas.width - Segment.SEGMENT_WIDTH
        if x_coord_of_new_segment >= self.canvas.width:
            x_coord_of_new_segment = Segment.SEGMENT_WIDTH
        if y_coord_of_new_segment <= 0:
            y_coord_of_new_segment = self.canvas.height - Segment.SEGMENT_WIDTH
        if y_coord_of_new_segment >= self.canvas.height:
            y_coord_of_new_segment = Segment.SEGMENT_WIDTH

        # self.canvas.create_line(head_coords+(x_coord_of_new_segment, y_coord_of_new_segment), fill="white")


        shape = Shape.RECTANGlE

        segment = Segment(self.canvas, shape, self.direction, x_coord_of_new_segment, y_coord_of_new_segment)

        if not prev_head:
            self.tail = segment
        else:
            prev_head.recreate(Shape.OVAL)

        self.segments.append(segment)
        self.canvas.update()

        self.head = segment



    def add_tail(self):

        direction = self.tail.original_direction

        dx = dy = 0

        if self.direction == Direction.UP:
            dy= Segment.SEGMENT_LENGTH
        if self.direction == Direction.DOWN:
            dy = - Segment.SEGMENT_LENGTH
        if self.direction == Direction.LEFT:
            dx = Segment.SEGMENT_LENGTH
        if self.direction == Direction.RIGHT:
            dx = - Segment.SEGMENT_LENGTH

        tail_coords = self.tail.coords

        coords_of_new_segment = tail_coords[0]+dx, tail_coords[1]+dy

        segment = Segment(self.canvas, Shape.OVAL, direction, *coords_of_new_segment)

        self.segments.appendleft(segment)
        self.canvas.update()

        self.tail = segment

        print("Tail added")


    def remove_tail(self):
        segment = self.segments.popleft()
        self.canvas.delete(segment.index)

        del segment

        self.tail = self.segments[len(self.segments)-1]


    def move(self):

        if self.is_frozen:
            return

        if not self.is_changing:

            self.collision_callback_fn()

            self.add_head(True)

            self.remove_tail()

        self.canvas.after(self.speed, lambda: self.move())
