
Towers of Hanoi — Simple Flat Project (Rules Correct)
Test change

Internal model:
  - Each peg list stores disks from bottom -> top
  - The TOP is list[-1] (pop/append)
  - Disk sizes: 1 (smallest) .. n (largest)
  - Initial left peg: [n, n-1, ..., 1]

Files:
  - app.py   (entry point)
  - model.py (rules & state)
  - solver.py
  - ui.py    (Tkinter UI & drawing)

Run:
  python app.py
  # or open app.py in Thonny and press Run

Use the "Peg Color" and "Disk Color" buttons to customize the appearance.
Disks can be moved by either clicking pegs or dragging the top disk with the mouse.
