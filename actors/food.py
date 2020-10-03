from PIL import ImageTk, Image
from SnakeGame.constants.shape import Shape
from SnakeGame.utils.image_processor import ImageProcessor
from SnakeGame.constants.game_states import States
from SnakeGame.utils.animation import AnimationUtil


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
        print("Called from herer")
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


class AutoDestroyableFood(Food):
    CLOCK_WIDTH = 20
    UPDATE_FREQ_IN_MILLIS = 200
    IMAGE = None
    IMAGE_PATH = r'C:\Users\Amartya\PycharmProjects\Projects\SnakeGame\images\frog.jpg'

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

        masked = ImageProcessor.automask(AutoDestroyableFood.IMAGE_PATH, height=Food.FOOD_WIDTH, width=Food.FOOD_WIDTH)[0]

        AutoDestroyableFood.IMAGE = ImageTk.PhotoImage(masked)
        print('called get photo')
        return AutoDestroyableFood.IMAGE

    def create(self):
        super().create()
        coords = self.coords
        timer_coords = coords[2]+10, coords[3]-AutoDestroyableFood.CLOCK_WIDTH

        self.timer_rectangle_coords = timer_coords[0]-AutoDestroyableFood.CLOCK_WIDTH/2, \
                                 timer_coords[1]-AutoDestroyableFood.CLOCK_WIDTH/2,\
                                 timer_coords[0]+AutoDestroyableFood.CLOCK_WIDTH/2, \
                                 timer_coords[1]+AutoDestroyableFood.CLOCK_WIDTH/2

        total_arcs = self.duration/AutoDestroyableFood.UPDATE_FREQ_IN_MILLIS
        self.extent_angle=360/total_arcs
        self.state = States.RUNNING

        self.animate()

    def animate(self):
        if not self.state == States.RUNNING:
            return
        if self.start_angle > -270:
            arc = self.board.create_arc(self.timer_rectangle_coords, start=self.start_angle, extent=self.extent_angle, fill='gray')
            self.arcs.append(arc)
            self.start_angle -= self.extent_angle
            self.board.after(AutoDestroyableFood.UPDATE_FREQ_IN_MILLIS, lambda: self.animate())
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

