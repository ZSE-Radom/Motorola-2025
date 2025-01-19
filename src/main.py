import tkinter as tk
from gui import MainMenuGUI

debug = True

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Szachy motorola alpha")
    MainMenuGUI(root)
    root.mainloop()
