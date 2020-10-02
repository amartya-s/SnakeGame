import colour
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import ttk

from SnakeGame.controllers.game_controller import Controller
from SnakeGame.constants.game_states import States


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

        #self.scale("all", 0, 0, wscale, hscale)

        print("width:{}-height:{}".format(self.width, self.height))

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

        self.popup_idx = None

        self.create_widgets()

        self.state = False

        self.pause_label = None

        self.controller = Controller()


    @staticmethod
    def fade(widget, smoothness=4, cnf={}, **kw):  #source: https://stackoverflow.com/questions/49433315/is-there-a-wayor-a-library-for-making-a-smooth-colour-transition-in-tkinter

        """This function will show faded effect on widget's different color options.

        Args:
            widget (tk.Widget): Passed by the bind function.
            smoothness (int): Set the smoothness of the fading (1-10).
            background (str): Fade background color to.
            foreground (str): Fade foreground color to."""

        kw = tk._cnfmerge((cnf, kw))
        if not kw: raise ValueError("No option given, -bg, -fg, etc")
        if len(kw) > 1: return [Game.fade(widget, smoothness, {k: v}) for k, v in kw.items()][0]
        if not getattr(widget, '_after_ids', None): widget._after_ids = {}
        widget.after_cancel(widget._after_ids.get(list(kw)[0], ' '))
        c1 = tuple(map(lambda a: a / (65535), widget.winfo_rgb(widget[list(kw)[0]])))
        c2 = tuple(map(lambda a: a / (65535), widget.winfo_rgb(list(kw.values())[0])))
        colors = tuple(colour.rgb2hex(c, force_long=True)
                       for c in colour.color_scale(c1, c2, max(1, smoothness * 100)))

        def worker(count=0):
            if len(colors) - 1 <= count: return
            widget.config({list(kw)[0]: colors[count]})
            widget._after_ids.update({list(kw)[0]: widget.after(
                max(1, int(smoothness / 10)), worker, count + 1)})

        worker()

    def bg_config(self, event, widget, bg, fg):
        Game.fade(widget, smoothness=5, fg=fg, bg=bg)

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
        bt.bind("<Enter>", lambda e: self.bg_config(e,bt, "#f47142", "white"))
        bt.bind("<Leave>", lambda e: self.bg_config(e,bt, "white", "black"))
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

        #game_window.minsize(width=1500, height=1000)

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
        self.controller.board = self.board
        self.controller.score_label = score_label_textvar

        self.play()

    def move(self, event):
        self.controller.change_direction(event.keysym)

    def save_btn_handler(self):
        self.board.delete(self.popup_idx)

    def resume_bt_handler(self):
        self.board.delete(self.popup_idx)
        self.pause_and_resume()

    def display_save_btn(self):
        style = ttk.Style()
        style.configure('Popup-Button', activebackground="#33B5E5", borderwidth=10, relief=tk.FLAT, justify="center", font="Times 20  bold")

        f = tk.Frame(self.board, width=300, height=200, borderwidth=4,relief=tk.RIDGE)
        lbl = ttk.Label(f,text="Do you want to save the game ?")
        lbl.configure(font="Times 15  bold")
        lbl.pack()

        cf = tk.Frame(f,width=300, height=200)
        cf.pack(expand=True, fill=tk.BOTH,pady=10)

        save_btn=tk.Button(cf, text='Save', width=50, command=self.save_btn_handler)
        save_btn.configure(borderwidth=4, relief=tk.RAISED, justify="center", font="Times 20  bold")
        save_btn.pack(side=tk.TOP, pady=5, padx=20)

        resume_btn=tk.Button(cf, text='Resume (<Space>)', width=50, command=self.resume_bt_handler)
        resume_btn.configure(  borderwidth=4, relief=tk.RAISED, justify="center", font="Times 20  bold")
        resume_btn.pack(side=tk.BOTTOM, padx=20)

        self.popup_idx = self.board.create_window(self.board.width/2, self.board.height/2, anchor=tk.NW,window=f, width=400, height=200)

    def fade_away(self):
        alpha = self.game_window.attributes("-alpha")
        if alpha > 0.4:
            alpha -= .1
            self.game_window.attributes("-alpha", alpha)
            print('fading away - {}'.format(alpha))
            self.game_window.after(100, self.fade_away)
    @staticmethod
    def RBGAImage(path):

        return Image.open(path).convert("RGBA")

    def pause_and_resume(self, e=None):

        self.controller.pause_and_resume()
        # self.fade_away()
        if self.controller.state == States.PAUSED:
            pass
            # img = Game.RBGAImage("images/pause-img.jpg")
            # tk.Label(image=ImageTk.PhotoImage(img)).pack()
            #self.display_save_btn()
            # mf = tk.Frame(self.board, width=self.board.width, bg='blue')
            # mf.pack(fill=tk.BOTH, expand=True)

            # f1=tk.Frame(mf, width=self.board.width, height=self.board.height/2, bg='green')
            # f1.pack(side=tk.TOP)
            # f2 = tk.Frame(mf, width=self.board.width, height=self.board.height/2, bg='grey')
            # f2.pack(side=tk.BOTTOM)
            #self.fade_away()
            # pause_label = tk.Frame(self.board, width=self.board.width, height=50, bg='black')
            # pause_label.pack(fill=tk.X, expand=True)
            # tk.Label(pause_label,text='PAUSED',font="Times 40 bold", anchor=tk.CENTER).pack()
            #
            # self.board.create_rectangle(0,0,self.board.width, self.board.height, fill='black',stipple="gray50")

            window_height = 50
            #self.board.create_window(self.board.width/2, self.board.height/2, anchor=tk.CENTER, window=pause_label)



            #self.board.delete(self.popup_idx)
            #self.pause_label.pack_forget()

    def play(self):
        self.bind_events()
        #self.pause_label = tk.Frame(self.board, width=self.board.width, height=50, bg='yellow')
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
    # root.grid_rowconfigure(0, weight=1, minsize=1)
    # root.grid_columnconfigure(0, weight=1)
    tk.mainloop()
