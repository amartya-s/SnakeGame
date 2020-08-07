import collections

from SnakeGame.constants.shape import Shape
from SnakeGame.constants.direction import Direction

class Segment(object):
    SEGMENT_LENGTH = 35
    SEGMENT_WIDTH = 25
    HEAD = 'head'
    TAIL = 'tail'

    def __init__(self, board, shape,direction, x, y,color):
            self.shape = shape
            self.board = board
            self.index = None

            self.x = self.y = None
            self.coords = ()
            self.original_direction = direction
            self.color = color

            self.create(x, y)

    def create(self, x_coord, y_coord):
        len_diff = Segment.SEGMENT_LENGTH / 2
        width_diff = Segment.SEGMENT_WIDTH / 2

        if self.original_direction in [Direction.LEFT, Direction.RIGHT]:
            rectangle_coords = x_coord - len_diff, y_coord - width_diff, x_coord + len_diff, y_coord + width_diff
        else:
            rectangle_coords = x_coord - width_diff, y_coord - len_diff, x_coord + width_diff, y_coord + len_diff

        if self.shape == Shape.RECTANGlE:
            index = self.board.create_rectangle(rectangle_coords, fill=self.color, tags=('segment'))
        else:
            index = self.board.create_oval(rectangle_coords, fill=self.color, tags=('segment'))

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

    def __init__(self, canvas, **properties):

        self.properties = properties
        self.canvas = canvas

        self.segments = collections.deque([])

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

    def set_property(self, segments, **kwargs):
        for segment in segments:
            segment.configure(**kwargs)

    def add_segment(self, is_head, direction, **kwargs):

        dx = dy = 0

        if direction == Direction.UP:
            if is_head:
                dy= - Segment.SEGMENT_LENGTH
            else:
                dy = Segment.SEGMENT_LENGTH
        if direction == Direction.DOWN:
            if is_head:
                dy = Segment.SEGMENT_LENGTH
            else:
                dy =  - Segment.SEGMENT_LENGTH
        if direction == Direction.LEFT:
            if is_head:
                dx = -Segment.SEGMENT_LENGTH
            else:
                dx = Segment.SEGMENT_LENGTH
        if direction == Direction.RIGHT:
            if is_head:
                dx = Segment.SEGMENT_LENGTH
            else:
                dx = - Segment.SEGMENT_LENGTH

        x_coord_of_new_segment, y_coord_of_new_segment = None,None

        prev_head = None

        if is_head:
            if not len(self.segments):
                head_coords = kwargs['snake_init_coords']
            else:
                head = self.segments[len(self.segments) - 1]
                head_coords = head.x, head.y
                prev_head = head

            x_coord_of_new_segment, y_coord_of_new_segment = head_coords[0] + dx, head_coords[1] + dy

            if x_coord_of_new_segment <= 0:
                x_coord_of_new_segment = self.canvas.width - Segment.SEGMENT_WIDTH
            if x_coord_of_new_segment >= self.canvas.width:
                x_coord_of_new_segment = Segment.SEGMENT_WIDTH
            if y_coord_of_new_segment <= 0:
                y_coord_of_new_segment = self.canvas.height - Segment.SEGMENT_WIDTH
            if y_coord_of_new_segment >= self.canvas.height:
                y_coord_of_new_segment = Segment.SEGMENT_WIDTH

        else:
            tail_coords = self.tail.x, self.tail.y

            x_coord_of_new_segment, y_coord_of_new_segment = tail_coords[0] + dx, tail_coords[1] + dy

        color = 'red' if is_head else 'pink'

        new_segment = Segment(self.canvas, Shape.OVAL, direction, x_coord_of_new_segment,
                              y_coord_of_new_segment, color)

        if is_head:
            self.segments.append(new_segment)
            self.head = new_segment
            if not prev_head:
                self.tail = new_segment
            else:
                prev_head.recreate(Shape.OVAL)
        else:
            self.tail = new_segment
            self.segments.appendleft(new_segment)

        self.canvas.update()

    def remove_tail(self):
        segment = self.segments.popleft()
        self.canvas.delete(segment.index)

        del segment

        self.tail = self.segments[len(self.segments)-1]


