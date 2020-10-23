import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter.messagebox import showinfo

from SnakeGame.constants.game_states import States
from SnakeGame.constants.game_params import GameParams
from SnakeGame.utils.animation import AnimationUtil
from SnakeGame.controllers.game_controller import Controller
from SnakeGame.controllers.datastore import DataStoreManager


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

        print("Window resized | width:{}-height:{}".format(self.width, self.height))

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

        self.master = root
        self.board = None
        self.pause_label = None

        self.create_widgets()
        self.controller = Controller()

    @staticmethod
    def get_control_text():
        return "Pause <Space> | Full Screen <F11>"

    @staticmethod
    def get_saved_games():
        saved_games = ['Select']
        saved_games.extend(DataStoreManager.get_saved_games())
        return saved_games

    def bind_events(self):
        self.board.bind_all("<KeyPress-Left>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Right>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Up>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Down>", lambda e: self.move(e))

        self.board.bind_all("<space>", lambda e: self.pause_and_resume(e))

        print("Event bind done.")

    def get_save_resume_frame(self, coords):
        mf = tk.Frame(self.board, width=80, height=5, bg='white')

        # save btn
        img = Image.open(GameParams.SAVE_IMAGE_PATH)
        tk.save_img = ImageTk.PhotoImage(img)
        save_bt = tk.Button(mf, image=tk.save_img, width=190, height=90, borderwidth=0, command=lambda: self.save_btn_handler())
        save_bt.pack(side=tk.TOP, expand=False)

        # resume btn
        img = Image.open(GameParams.RESUME_IMAGE_PATH)
        tk.resume_img = ImageTk.PhotoImage(img)
        resume_bt = tk.Button(mf, image=tk.resume_img, width=190, height=90, borderwidth=0, command=lambda: self.resume_bt_handler())
        resume_bt.pack(side=tk.BOTTOM, expand=False)

        return mf

    def move(self, event):
        self.controller.change_direction(event.keysym)

    def start_new_game(self):
        self.create_game_window()
        self.bind_events()
        self.controller.start_new_game()

    def load_game(self):
        self.create_game_window()
        self.controller.set_datastore(inst=self.saved_games_var.get())
        success = self.controller.load_game()
        if not success:
            showinfo("Window", "Game failed loading")
            return

        self.bind_events()
        self.pause()

    def resume(self):
        self.save_resume_bt_frame.place_forget()
        self.board.delete(self.pause_label)

    def pause(self):
        pause_label = tk.Label(self.board, text='PAUSED', font="InkFree 40 bold", width=self.board.width,
                               bg='wheat4',
                               foreground='white')
        self.pause_label = self.board.create_window(self.board.width / 2, self.board.height / 2,
                                                    anchor=tk.CENTER,
                                                    window=pause_label)
        coords = self.board.coords(self.pause_label)
        if not hasattr(self, 'save_resume_bt_frame'):
            mf = self.get_save_resume_frame(coords)
            self.save_resume_bt_frame = mf
        self.save_resume_bt_frame.place(in_=self.board, x=coords[0] - 90, y=coords[1] + 45)

    def pause_and_resume(self, e=None):
        if self.controller.state == States.RUNNING:
            self.pause()
            self.controller.pause()
        elif self.controller.state == States.PAUSED:
            self.resume()
            self.controller.resume()

    def save_btn_handler(self):
        success = self.controller.save_game()
        if success:
            showinfo("Window", "Game Saved")
        else:
            showinfo("Window", "Failed saving game")

    def resume_bt_handler(self):
        self.resume()
        self.controller.resume()

    def create_widgets(self):
        control_frame = tk.Frame(master=self.master, bg='pink', relief='ridge',borderwidth=2, width=400, height=100)
        control_frame.pack(pady=10, padx=10)

        # Play button
        new_bt = tk.Button(master=control_frame, text="New Game", font="Times 20 bold", borderwidth=4, relief="raised", justify="center", width=10, height=1
                       , command=self.start_new_game)
        new_bt.bind("<Enter>", lambda e: AnimationUtil.fade_btn(e, new_bt, "#f47142", "white"))
        new_bt.bind("<Leave>", lambda e: AnimationUtil.fade_btn(e, new_bt, "white", "black"))

        # Load button
        load_bt = tk.Button(master=control_frame, text="Load", font="Times 20 bold", borderwidth=4, relief="raised", justify="center", width=10, height=1
                       , command=self.load_game)
        load_bt.bind("<Enter>", lambda e: AnimationUtil.fade_btn(e, load_bt, "#f47142", "white"))
        load_bt.bind("<Leave>", lambda e: AnimationUtil.fade_btn(e, load_bt, "white", "black"))

        # select samed games frame
        dropdown_frame = tk.Frame(control_frame, width=50, height=200, relief='groove',borderwidth=3)

        self.saved_games_var = tk.StringVar(dropdown_frame)
        saved_games = Game.get_saved_games()
        self.saved_games_var.set(saved_games[0])

        tk.Label(dropdown_frame, text="Saved games ",
                  font="Times 20 bold", borderwidth=4, justify="center").pack(side=tk.TOP)

        combo_box_level = ttk.Combobox(dropdown_frame,textvariable=self.saved_games_var,state='readonly',justify='center', height=100, width=50)
        combo_box_level['values'] = tuple(saved_games)
        combo_box_level.pack(side=tk.BOTTOM)
        combo_box_level.set(self.saved_games_var.get())

        # placing everything in the grid structure
        dropdown_frame.grid(row=1, column=1, rowspan=5, columnspan=2, padx=5)
        new_bt.grid(row=1,column=6, rowspan=3 ,padx=10)
        load_bt.grid(row=4, column=6, rowspan=3, columnspan=5, padx=1,pady=5)

    def create_game_window(self):
        game_window = tk.Toplevel(self.master)
        game_window.title("Snake Game")

        board_frame = tk.Frame(master=game_window, bg='black',highlightthickness=3, highlightbackground="yellow")
        board_frame.pack( fill=tk.BOTH,  expand=True)

        top_frame = tk.Frame(board_frame, height=100, borderwidth=5,highlightthickness=3, highlightbackground='red')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        s_label_f = tk.Frame(master=top_frame, width=100,height=100, padx=10,relief='groove', borderwidth=5,highlightbackground='green')
        s_label_f.pack(side=tk.LEFT)

        score_label_textvar = tk.StringVar()
        score_label = ttk.Label(s_label_f, font=("Helvetica", 50), justify='left', anchor='w',textvariable=score_label_textvar)
        score_label.pack(side=tk.LEFT)
        score_label_textvar.set("0")

        ttk.Label(top_frame,
              text=Game.get_control_text(),justify='right', anchor='e').pack(side=tk.RIGHT)

        canvas = GameCanvas(board_frame, bg='white', width=1000, height=800,highlightthickness=3, highlightbackground="red")
        canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.board = canvas

        self.controller.set_board(self.board)
        self.controller.set_score_label(score_label_textvar)


if __name__ == '__main__':

    root = tk.Tk()

    app = Game(root)

    root.title("Snake game")
    root.geometry("600x200")
    # root.grid_rowconfigure(0, weight=1, minsize=1)
    # root.grid_columnconfigure(0, weight=1)
    tk.mainloop()
