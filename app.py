
# Towers of Hanoi — Simple (Rules-Correct)
# A simple implementation of the Towers of Hanoi game using Tkinter for the GUI.
import tkinter as tk
from ui import HanoiUI

def main():
    root = tk.Tk()
    root.title("Towers of Hanoi — Simple (Rules-Correct)")
    ui = HanoiUI(root)
    ui.pack(fill="both", expand=True)
    root.minsize(640, 420)
    root.mainloop()

if __name__ == "__main__":
    main()
