
import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Optional, Generator, Tuple
from model import GameState
from solver import hanoi_moves

Move = Tuple[int, int]

class HanoiUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=8)
        self.state = GameState(4)
        self._solver: Optional[Generator[Move, None, None]] = None
        self._auto_after: Optional[str] = None
        self.peg_color = "#64748b"
        self.disk_color = "#0ea5e9"

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Canvas
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#f8fafc")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        # mouse interactions
        self.canvas.bind("<ButtonPress-1>", self._press)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        # drag state
        self._drag_start: Optional[int] = None
        self._drag_disk: Optional[int] = None
        self._drag_item: Optional[int] = None
        self._drag_half: int = 0
        self._drag_disk_h: int = 0

        # Controls
        bar = ttk.Frame(self, padding=(0,8,0,0))
        bar.grid(row=1, column=0, sticky="ew")
        bar.columnconfigure(9, weight=1)

        ttk.Label(bar, text="Disks:").grid(row=0, column=0)
        self.n_var = tk.IntVar(value=self.state.n_disks)
        self.spin = ttk.Spinbox(bar, from_=1, to=8, textvariable=self.n_var, width=4, wrap=True)
        self.spin.grid(row=0, column=1, padx=6)

        ttk.Button(bar, text="New", command=self._new).grid(row=0, column=2, padx=3)
        ttk.Button(bar, text="Reset", command=self._reset).grid(row=0, column=3, padx=3)
        ttk.Button(bar, text="Step ▶", command=self._step).grid(row=0, column=4, padx=3)
        self.auto_var = tk.BooleanVar(value=False)
        self.auto_btn = ttk.Checkbutton(bar, text="Auto", variable=self.auto_var, command=self._auto_toggle)
        self.auto_btn.grid(row=0, column=5, padx=6)
        ttk.Button(bar, text="Peg Color", command=self._choose_peg_color).grid(row=0, column=6, padx=3)
        ttk.Button(bar, text="Disk Color", command=self._choose_disk_color).grid(row=0, column=7, padx=3)

        self.status = ttk.Label(bar, text="Moves: 0")
        self.status.grid(row=0, column=8, sticky="e")

        self.redraw()

    # ---- Controls ----
    def _new(self):
        self._stop_auto()
        self.state.reset(self.n_var.get())
        self._solver = None
        self.redraw()
        self._update_status()

    def _reset(self):
        self._stop_auto()
        self.state.reset(self.state.n_disks)
        self._solver = None
        self.redraw()
        self._update_status()

    def _prepare_solver(self):
        self._solver = hanoi_moves(self.state.n_disks)

    def _step(self):
        if self._solver is None:
            self._prepare_solver()
        try:
            src, dst = next(self._solver)
        except StopIteration:
            self.auto_var.set(False)
            return
        self.state.move(src, dst)
        self.redraw()
        self._update_status()

    def _auto_toggle(self):
        if self.auto_var.get():
            if self._solver is None:
                self._prepare_solver()
            self._schedule()
        else:
            self._stop_auto()

    def _choose_peg_color(self):
        color = colorchooser.askcolor(color=self.peg_color, title="Select peg color")[1]
        if color:
            self.peg_color = color
            self.redraw()

    def _choose_disk_color(self):
        color = colorchooser.askcolor(color=self.disk_color, title="Select disk color")[1]
        if color:
            self.disk_color = color
            self.redraw()

    def _schedule(self):
        self._step()
        if self.auto_var.get():
            self._auto_after = self.after(300, self._schedule)

    def _stop_auto(self):
        if self._auto_after is not None:
            self.after_cancel(self._auto_after)
            self._auto_after = None
        self.auto_var.set(False)

    # ---- Canvas interactions ----
    def _press(self, event):
        # record the starting peg; actual drag starts on motion
        w = self.canvas.winfo_width()
        peg_w = w / 3
        self._drag_start = min(2, int(event.x // peg_w))

    def _drag(self, event):
        if self._drag_start is None:
            return
        if self._drag_disk is None:
            # initialize dragging on first motion
            if not self.state.pegs[self._drag_start]:
                self._drag_start = None
                return
            self.state.selected_peg = None
            self._drag_disk = self.state.pegs[self._drag_start].pop()
            c = self.canvas
            w = c.winfo_width() or 640
            h = c.winfo_height() or 360
            base_y = h - 40
            peg_w = w / 3
            peg_top = 80
            max_disk = self.state.n_disks
            disk_h = max(14, int((base_y - peg_top - 20) / max_disk))
            self._drag_disk_h = disk_h
            width_factor = (self._drag_disk / max_disk)
            half = int((peg_w * 0.4) * (0.3 + 0.7 * width_factor))
            self._drag_half = half
            self.redraw()
            self._drag_item = c.create_rectangle(
                event.x - half,
                event.y - disk_h / 2,
                event.x + half,
                event.y + disk_h / 2,
                outline="",
                fill=self.disk_color,
            )
        else:
            c = self.canvas
            half = self._drag_half
            disk_h = self._drag_disk_h
            c.coords(
                self._drag_item,
                event.x - half,
                event.y - disk_h / 2,
                event.x + half,
                event.y + disk_h / 2,
            )

    def _release(self, event):
        if self._drag_disk is not None and self._drag_start is not None:
            c = self.canvas
            w = c.winfo_width()
            peg_w = w / 3
            dest = min(2, int(event.x // peg_w))
            # restore disk to perform move via model
            self.state.pegs[self._drag_start].append(self._drag_disk)
            moved = self.state.move(self._drag_start, dest)
            c.delete(self._drag_item)
            self._drag_disk = None
            self._drag_item = None
            self._drag_start = None
            self.redraw()
            self._update_status()
        else:
            self._drag_start = None
            self._click(event)
    def _click(self, event):
        w = self.canvas.winfo_width()
        peg_w = w / 3
        peg_index = min(2, int(event.x // peg_w))

        st = self.state
        if st.selected_peg is None:
            st.selected_peg = peg_index
        else:
            st.move(st.selected_peg, peg_index)
            st.selected_peg = None
        self.redraw()
        self._update_status()

    def _update_status(self):
        txt = f"Moves: {self.state.moves_made}"
        if self.state.is_solved():
            txt += " — Solved! 🎉"
        self.status.config(text=txt)

    # ---- Drawing ----
    def redraw(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 640
        h = c.winfo_height() or 360
        margin = 24
        base_y = h - 40
        peg_w = w/3
        peg_xs = [peg_w*i + peg_w/2 for i in range(3)]
        peg_top = 80

        # base
        c.create_rectangle(margin, base_y, w-margin, base_y+8, fill="#334155", outline="")
        # pegs
        for x in peg_xs:
            c.create_rectangle(x-4, peg_top, x+4, base_y, fill=self.peg_color, outline="")

        # disks
        # IMPORTANT: we iterate bottom->top (the list is stored bottom..top)
        max_disk = self.state.n_disks
        disk_h = max(14, int((base_y - peg_top - 20) / max_disk))
        for peg_i, stack in enumerate(self.state.pegs):
            for level, disk in enumerate(stack):  # bottom -> top
                y2 = base_y - level * disk_h
                y1 = y2 - (disk_h - 2)
                width_factor = (disk / max_disk)
                half = int((peg_w * 0.4) * (0.3 + 0.7 * width_factor))
                x = peg_xs[peg_i]
                c.create_rectangle(x-half, y1, x+half, y2, outline="", fill=self.disk_color)

        # selection highlight
        if self.state.selected_peg is not None:
            x = peg_xs[self.state.selected_peg]
            c.create_rectangle(x-peg_w/2+6, peg_top+6, x+peg_w/2-6, base_y-6, outline="#22c55e", width=3, dash=(4,2))
