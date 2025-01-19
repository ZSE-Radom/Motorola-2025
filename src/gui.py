import tkinter as tk
from tkinter import messagebox
from modes import ClassicMode, BlitzMode, X960Mode

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
        file_menu.add_command(label="Powrót do menu", command=self.back_to_menu)
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

    def back_to_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        MainMenuGUI(self.root)


class MainMenuGUI:
    def __init__(self, root):
        self.root = root
        self.mode = None
        self.create_menu()

    def create_menu(self):
        new_game_btn = tk.Button(self.root, text="Nowa gra offline", command=self.new_offline_game)
        new_game_btn.grid(row=0, column=0, padx=10, pady=10)
        #load_game_btn = tk.Button(self.root, text="Wczytaj grę", command=self.load_game)
        #load_game_btn.grid(row=1, column=0, padx=10, pady=10)
        exit_btn = tk.Button(self.root, text="Wyjście", command=self.root.quit)
        exit_btn.grid(row=2, column=0, padx=10, pady=10)


    def new_offline_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        GameModeSelectionGUI(self.root)

    def show_about(self):
        messagebox.showinfo("O grze", "Szachy motorola alpha\n Autor: XYZ")

class GameModeSelectionGUI:
    def __init__(self, root):
        self.root = root
        self.create_menu()

    def create_menu(self):
        classic_btn = tk.Button(self.root, text="Klasyczne szachy", command=self.select_classic_mode)
        classic_btn.grid(row=0, column=0, padx=10, pady=10)
        chess960_btn = tk.Button(self.root, text="Szachy 960", command=self.select_chess960_mode)
        chess960_btn.grid(row=1, column=0, padx=10, pady=10)
        blitz_btn = tk.Button(self.root, text="Szachy błyskawiczne", command=self.select_blitz_mode)
        blitz_btn.grid(row=2, column=0, padx=10, pady=10)
        custom_btn = tk.Button(self.root, text="Własne zasady", command=self.select_custom_mode)
        custom_btn.grid(row=3, column=0, padx=10, pady=10)

    def select_classic_mode(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        mode = ClassicMode(None)
        gui = ChessGameGUI(self.root, mode)
        mode.gui = gui

    def select_chess960_mode(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        mode = X960Mode(None)
        gui = ChessGameGUI(self.root, mode)
        mode.gui = gui

    def select_blitz_mode(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        mode = BlitzMode(None)
        gui = ChessGameGUI(self.root, mode)
        mode.gui = gui

    def select_custom_mode(self):
        messagebox.showinfo("Info", "Ta opcja nie jest jeszcze dostępna")