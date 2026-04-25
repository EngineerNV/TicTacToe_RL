"""
Headless screenshot script — captures each UI screen using Xvfb.
Run via:  xvfb-run -s "-screen 0 1024x768x24" python3 take_screenshots.py
"""

import tkinter as tk
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from gui import TicTacToeApp, BG_DARK

OUT = '/home/user/TicTacToe_RL/screenshots'
os.makedirs(OUT, exist_ok=True)


def save(root, name):
    root.update_idletasks()
    root.update()
    # Use PIL to grab the window by geometry
    try:
        from PIL import ImageGrab
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save(f'{OUT}/{name}.png')
        print(f'  saved {name}.png  ({w}x{h})')
    except Exception as e:
        # Fallback: scrot full screen
        os.system(f'scrot -z {OUT}/{name}.png')
        print(f'  saved {name}.png (scrot fallback): {e}')


root = tk.Tk()
app  = TicTacToeApp(root)

# ── 1. Menu screen ────────────────────────────────────────────────────────
def shot_menu():
    root.update(); root.update_idletasks()
    save(root, '1_menu')

    # ── 2. Training screen ────────────────────────────────────────────────
    root.after(100, lambda: app._show_train())
    root.after(300, shot_train)

def shot_train():
    root.update(); root.update_idletasks()
    save(root, '2_train_idle')

    # Put some fake stats on the board so it looks live
    cells = app._train_cells
    demo  = [2, 1, 0,  0, 2, 0,  1, 0, 2]
    from gui import COLOR_X, COLOR_O, BG_CELL
    for i, lbl in enumerate(cells):
        v = demo[i]
        if v == 2: lbl.config(text='X', fg=COLOR_X, bg=BG_CELL)
        elif v == 1: lbl.config(text='O', fg=COLOR_O, bg=BG_CELL)
    app._sv_ep.set('Episode: 8,250')
    app._sv_win.set('Win:  57.3%')
    app._sv_tie.set('Tie:  42.7%')
    app._sv_loss.set('Loss:   0.0%')
    app._sv_eps.set('ε: 0.092')
    app._progress['maximum'] = 20000
    app._progress['value']   = 8250
    app._sv_pct.set('41.3%')
    root.update()
    save(root, '3_train_live')

    root.after(100, lambda: app._show_play())
    root.after(300, shot_play_empty)

def shot_play_empty():
    root.update(); root.update_idletasks()
    save(root, '4_play_empty')

    # Simulate a mid-game board
    from gui import COLOR_X, COLOR_O, BG_CELL, COLOR_WIN
    demo  = [1, 0, 2,  0, 2, 0,  1, 0, 0]
    cells = app._play_cells
    for i, btn in enumerate(cells):
        v = demo[i]
        if v == 1: btn.config(text='O', fg=COLOR_O, bg=BG_CELL)
        elif v == 2: btn.config(text='X', fg=COLOR_X, bg=BG_CELL)
        else: btn.config(text='', bg=BG_CELL)
    app._play_status.set('Your turn  ( O )')
    root.update()
    save(root, '5_play_midgame')

    # Simulate AI wins
    demo2 = [1, 1, 2,  0, 2, 0,  2, 0, 1]
    for i, btn in enumerate(cells):
        v = demo2[i]
        if v == 1: btn.config(text='O', fg=COLOR_O, bg=BG_CELL)
        elif v == 2: btn.config(text='X', fg=COLOR_X, bg=BG_CELL)
        else: btn.config(text='', bg=BG_CELL)
    # highlight the diagonal
    for i in [2, 4, 6]:
        cells[i].config(bg=COLOR_WIN)
    app._play_status.set('AI  Wins!')
    root.update()
    save(root, '6_play_ai_wins')

    root.after(100, root.destroy)

root.after(200, shot_menu)
root.mainloop()
print('Done — screenshots in', OUT)
