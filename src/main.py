import tkinter as tk
from modes import ClassicMode
from gui import ChessGameGUI

if __name__ == "__main__":
    root = tk.Tk()
    mode = ClassicMode(None)
    gui = ChessGameGUI(root, mode)
    mode.gui = gui
    root.mainloop()
