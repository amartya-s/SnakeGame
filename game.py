import tkinter as tk

from SnakeGame.controllers.game_controller import Controller


class GameCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, kwargs)
        self.parent = parent
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()


class Game:
    def __init__(self, root, **kwargs):
        master_window_width = 1000
        # master = tk.Frame(root, background='brown', width=master_window_width)
        # master.pack(fill=tk.BOTH, expand=True)

        self.master = root
        self.board = None
        self.snake = None

        self.create_widgets()

        self.controller = Controller(self.board)


    def create_widgets(self):
        bt = tk.Button(master=self.master, text="Play", width=10, height=2, bg='olive', command=lambda: self.play())
        bt.pack(side=tk.TOP)

        canvas = GameCanvas(self.master, bg='black', width=1000, height=800)
        canvas.pack(fill=tk.BOTH, expand=True)

        self.board = canvas
        # canvas.update()
        print(canvas.height)
        print(canvas.width)

    def move(self, event):
        print(event.keysym)
        self.controller.change_direction(event.keysym)

    def play(self):
        self.bind_events()
        self.controller.run()

    def bind_events(self):
        self.board.bind_all("<KeyPress-Left>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Right>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Up>", lambda e: self.move(e))
        self.board.bind_all("<KeyPress-Down>", lambda e: self.move(e))

        print("Event bind done.")


if __name__ == '__main__':

    root = tk.Tk()

    app = Game(root)

    root.title("Snake game")
    root.geometry("1000x800")


    tk.mainloop()
