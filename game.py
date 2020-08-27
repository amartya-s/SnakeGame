import tkinter as tk
from tkinter import ttk

from SnakeGame.controllers.game_controller import Controller


class GameCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, kwargs)
        self.parent = parent
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

        self.state = False

        self.bind("<Configure>", self.on_resize)

        self.parent.master.bind("<F11>", self.toggle_fullscreen)
        self.parent.master.bind("<Escape>", self.end_fullscreen)

        print("Binding done")

        self.toggle_fullscreen()


    def on_resize(self, event):
        wscale = event.width / self.width
        hscale = event.height / self.height

        self.width = event.width
        self.height = event.height

        # self.scale("all", 0, 0, wscale, hscale)

        print("{}-{}".format(self.width, self.height))

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.parent.master.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.parent.master.attributes("-fullscreen", False)
        return "break"


class Game:
    def __init__(self, root, **kwargs):
        master_window_width = 1000
        # master = tk.Frame(root, background='brown', width=master_window_width)
        # master.pack(fill=tk.BOTH, expand=True)

        self.master = root
        self.board = None
        self.snake = None

        self.create_widgets()

        self.state = False

        self.controller = Controller()


    @staticmethod
    def get_control_text():
        return "Pause <Space> | Full Screen <F11>"

    @staticmethod
    def get_game_levels():
        return ["Level 1", "Level 2", "Level 3"]

    @staticmethod
    def get_player_types():
        return ["Type 1", "Type 2", "Type 3"]

    def display_player(self, event):
        print(self.player_type_var.get())

    def create_widgets(self):
        control_frame = tk.Frame(master=self.master, bg='pink', relief='ridge',borderwidth=2, width=400, height=400)
        control_frame.pack()

        # Play button
        bt = tk.Button(master=control_frame, text="Play", font="Times 20 bold", borderwidth=4, relief="raised", justify="center", width=10
                       , command=self.create_game_window)

        # select level frame
        dropdown_frame = tk.Frame(control_frame, width=100, height=100, relief='groove',borderwidth=3)

        self.game_level_var = tk.StringVar(dropdown_frame)
        choices = Game.get_game_levels()
        self.game_level_var.set(choices[0])

        tk.Label(dropdown_frame, text="Select Level ",
                  font="Times 20 bold", borderwidth=4, justify="center").grid(row=0,column=5, pady=10)

        combo_box_level = ttk.Combobox(dropdown_frame,textvariable=self.game_level_var,state='readonly',justify='center', height=150, width=50)
        combo_box_level['values'] = tuple(choices)
        combo_box_level.grid()
        combo_box_level.set(self.game_level_var.get())

        # select player type frame
        choose_player_frame = tk.Frame(control_frame, relief='groove',borderwidth=5, highlightbackground='red')

        self.player_type_var = tk.StringVar(choose_player_frame)
        choices = Game.get_player_types()
        self.player_type_var.set(choices[0])

        tk.Label(choose_player_frame, text="Select player type ",
                  font="Times 20 bold", borderwidth=4, justify="center").grid(row=0,column=5, pady=10)

        combo_box_player = ttk.Combobox(choose_player_frame,textvariable=self.player_type_var,state='readonly',justify='center', height=150, width=50)
        combo_box_player['values'] = tuple(choices)
        combo_box_player.grid()
        combo_box_player.set(self.player_type_var.get())
        combo_box_player.bind_all("<<ComboboxSelected>>", lambda e:self.display_player(e))

        # display player window
        player_display_frame = tk.Frame(control_frame, relief='groove', borderwidth=5, highlightbackground='red')
        display_canvas = tk.Canvas(player_display_frame,  bg='white', width=100, height=100,highlightthickness=3, highlightbackground="red")
        display_canvas.pack()
        #display_canvas.create_

        # placing everything in the grid structure
        dropdown_frame.grid(row=1, column=1, rowspan=10, columnspan=5, padx=5,pady=5)
        choose_player_frame.grid(row=11, column=1, rowspan=10, columnspan=5, padx=1,pady=5)
        player_display_frame.grid(row=11, column=6, rowspan=10, columnspan=5, padx=1,pady=5)
        bt.grid(row=5,column=6,padx=10)
        combo_box_level.grid(row=2, column=0, rowspan=len(choices), columnspan=10, sticky='nsew')
        combo_box_player.grid(row=2, column=0, rowspan=len(choices), columnspan=10, sticky='nsew')

    def create_game_window(self):
        game_window = tk.Toplevel(self.master)
        game_window.title("Snake Game")

        board_frame = tk.Frame(master=game_window, bg='green',highlightthickness=3, highlightbackground="yellow")
        board_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        top_frame = tk.Frame(board_frame, height=100)
        top_frame.pack(side=tk.TOP, expand=True)

        score_label = tk.Label(top_frame, width=200)
        score_label.pack(side=tk.LEFT)

        tk.Label(top_frame,
              text=Game.get_control_text()).pack(side=tk.RIGHT)

        canvas = GameCanvas(board_frame, bg='white', width=1000, height=800,highlightthickness=3, highlightbackground="red")
        canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.board = canvas
        self.controller.board = self.board

        self.play()

    def move(self, event):
        self.controller.change_direction(event.keysym)

    def pause_and_resume(self, event):
        self.controller.pause_and_resume()

    def play(self):
        self.bind_events()
        self.controller.run()

    def bind_events(self):
        self.board.bind_all("<KeyPress-Left>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Right>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Up>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Down>", lambda e: self.move(e))

        self.board.bind_all("<space>", lambda e: self.pause_and_resume(e))

        print("Event bind done.")


if __name__ == '__main__':

    root = tk.Tk()

    app = Game(root)

    root.title("Snake game")
    root.geometry("600x400")
    root.grid_rowconfigure(0, weight=1, minsize=1)
    root.grid_columnconfigure(0, weight=1)
    tk.mainloop()
