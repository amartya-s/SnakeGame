from PIL import ImageTk
from SnakeGame.constants.shape import Shape
from SnakeGame.utils.image_processor import ImageProcessor
from SnakeGame.constants.game_states import States
from SnakeGame.constants.game_params import GameParams


class Food:
    IMAGE = None

    def __init__(self, board, x_cord, y_cord, shape=Shape.RECTANGlE):
        self.board = board
        self.x = x_cord
        self.y = y_cord
        self.shape = shape

        self.index = None
        self.coords = ()

    def get_photo(self):
        if Food.IMAGE:
            return Food.IMAGE

        masked = ImageProcessor.automask(GameParams.IMAGE_PATH_FOOD, height=GameParams.FOOD_WIDTH, width=GameParams.FOOD_WIDTH)[0]

        Food.IMAGE = ImageTk.PhotoImage(masked)

        return Food.IMAGE

    def update(self,ind, label):
        frame = self.frames[ind]
        ind += 1
        if ind > len(self.frames):  # With this condition it will play gif infinitely
            ind = 1
        label.configure(image=frame)
        self.board.after(100, self.update, ind, label)

    def create(self):
        rectangle_cords = self.x-GameParams.FOOD_WIDTH/2, self.y-GameParams.FOOD_WIDTH/2,self.x+GameParams.FOOD_WIDTH/2,self.y+GameParams.FOOD_WIDTH/2
        if self.shape == Shape.RECTANGlE:
            photo = self.get_photo()

            self.index = self.board.create_image(self.x, self.y, image=photo,anchor='center')

        if self.shape == Shape.OVAL:
            self.index = self.board.create_oval(rectangle_cords, fill='red')

        self.coords = rectangle_cords

    def destroy(self):
        self.board.delete(self.index)

    def get_pickleble_data(self):
        data = dict()
        data['x'] = self.x
        data['y'] = self.y
        data['shape'] = self.shape

        return data

    @staticmethod
    def reconstruct(board, **kwargs):
        food = Food(board=board, x_cord=kwargs['x'],
                                   y_cord=kwargs['y'], shape=kwargs['shape'])
        food.create()
        return food


class AutoDestroyableFood(Food):
    IMAGE = None

    def __init__(self,  board, duration_in_ms, x_cord, y_cord, shape=Shape.RECTANGlE):
        self.duration = duration_in_ms
        self.arcs = []
        self.timer_rectangle_coords = ()
        self.state = States.NOT_STARTED
        self.start_angle = 90
        self.extent_angle = 0
        self.is_live = True

        super().__init__(board,x_cord,y_cord,shape)

    def get_photo(self):
        if AutoDestroyableFood.IMAGE:
            return AutoDestroyableFood.IMAGE

        masked = ImageProcessor.automask(GameParams.IMAGE_PATH_SUPER_FOOD, height=GameParams.FOOD_WIDTH, width=GameParams.FOOD_WIDTH)[0]

        AutoDestroyableFood.IMAGE = ImageTk.PhotoImage(masked)
        return AutoDestroyableFood.IMAGE

    def create(self, state=States.RUNNING):
        super().create()
        coords = self.coords
        timer_coords = coords[2]+10, coords[3]-GameParams.CLOCK_WIDTH

        self.timer_rectangle_coords = timer_coords[0]-GameParams.CLOCK_WIDTH/2, \
                                 timer_coords[1]-GameParams.CLOCK_WIDTH/2,\
                                 timer_coords[0]+GameParams.CLOCK_WIDTH/2, \
                                 timer_coords[1]+GameParams.CLOCK_WIDTH/2

        total_arcs = self.duration/GameParams.UPDATE_FREQ_IN_MILLIS
        self.extent_angle=360/total_arcs
        self.state = state

        self.animate()

    def animate(self):
        if not self.state == States.RUNNING:
            return
        if self.start_angle > -270:
            arc = self.board.create_arc(self.timer_rectangle_coords, start=self.start_angle, extent=self.extent_angle, fill='gray')
            self.arcs.append(arc)
            self.start_angle -= self.extent_angle
            self.board.after(GameParams.UPDATE_FREQ_IN_MILLIS, lambda: self.animate())
        else:
            self.destroy()

    def pause(self):
        self.state = States.PAUSED

    def resume(self):
        self.state = States.RUNNING
        self.animate()

    def destroy(self):
        self.state = States.END
        for arc in self.arcs:
            self.board.delete(arc)
        self.board.delete(self.index)
        self.is_live = False

    def get_pickleble_data(self):
        data = super().get_pickleble_data()
        data['duration'] = self.duration
        data['time_left'] = self.duration - (self.duration/(360/self.extent_angle))*len(self.arcs)
        data['timer_rectangle_coords'] = self.timer_rectangle_coords
        data['state'] = self.state
        data['start_angle'] = self.start_angle
        data['extent_angle'] = self.extent_angle
        data['is_live'] = self.is_live

        return data

    @staticmethod
    def reconstruct(board, **kwargs):
        food = AutoDestroyableFood(board=board, duration_in_ms=kwargs['duration'], x_cord=kwargs['x'], y_cord=kwargs['y'], shape=kwargs['shape'])
        food.state = States.PAUSED

        time_left = kwargs['time_left']
        board.create_arc(kwargs['timer_rectangle_coords'], start=90, extent=(food.duration - time_left)*food.extent_angle, fill='gray')
        food.create(state=States.PAUSED)

        return food
