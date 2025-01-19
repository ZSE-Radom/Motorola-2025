import tkinter as tk
from tkinter import messagebox


class ChessGameGUI:
    def __init__(self, root, mode):
        self.root = root
        self.mode = mode
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        self.status_label = tk.Label(root, text=f"Teraz rusza się: {self.mode.current_turn}")
        self.status_label.grid(row=8, column=0, columnspan=8)
        self.create_board()
        self.create_menu()
        self.update_board()
        self.update_timer()

    def create_board(self):
        for i in range(8):
            for j in range(8):
                btn = tk.Button(self.root, width=4, height=2, command=lambda x=i, y=j: self.on_click(x, y))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Opcje", menu=file_menu)
        file_menu.add_command(label="Nowa gra", command=self.new_game)
        file_menu.add_separator()
        file_menu.add_command(label="Wyjście", command=self.root.quit)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Pomoc", menu=help_menu)
        help_menu.add_command(label="O grze", command=self.show_about)

    def new_game(self):
        self.mode.board = self.mode.initialize_board()
        self.mode.current_turn = "Biały"
        self.mode.timer = {"Biały": 600, "Czarny": 600}
        self.mode.move_history = []
        self.mode.running = True
        self.mode.selected_piece = None
        self.mode.valid_moves = []
        self.mode.last_move = None
        self.update_board()

    def show_about(self):
        messagebox.showinfo("O grze", "Szachy motorola alpha\n Autor: XYZ")

    def update_board(self):
        for i in range(8):
            for j in range(8):
                piece = self.mode.board[i][j]
                self.buttons[i][j].config(text=piece if piece != " " else "", bg="light gray")
        if self.mode.selected_piece:
            x, y = self.mode.selected_piece
            self.buttons[x][y].config(bg="yellow")
        self.status_label.config(text=f"Teraz rusza się: {self.mode.current_turn}")

    def update_timer(self):
        self.root.title(f"Biały: {self.mode.timer['Biały']}s - Czarny: {self.mode.timer['Czarny']}s - Kolej: {self.mode.current_turn}")
        self.root.after(1000, self.update_timer)

    def on_click(self, x, y):
        self.mode.on_click(x, y, self.buttons)
