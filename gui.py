"""
gui.py  --  TicTacToe RL  |  EngineerNV
Tkinter-based GUI with two modes:
  - Training visualizer: watch the AI learn in real time
  - Play mode: click to challenge the trained AI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import os

from ticTac import ticTac
from qLearning import qLearning

# ---------------------------------------------------------------------------
# Color palette (dark terminal aesthetic)
# ---------------------------------------------------------------------------
BG_DARK    = '#0d1117'
BG_CARD    = '#161b22'
BG_CELL    = '#21262d'
CELL_HOVER = '#30363d'
COLOR_X    = '#ff7b72'   # red  – AI (X)
COLOR_O    = '#79c0ff'   # blue – human / opponent (O)
COLOR_WIN  = '#f0c850'   # gold – winning highlight
COLOR_TIE  = '#8b949e'   # grey – tie
BTN_GREEN  = '#238636'
BTN_RED    = '#da3633'
BTN_PURPLE = '#8957e5'
BTN_BLUE   = '#1f6feb'
TEXT_ON    = '#f0f6fc'
TEXT_DIM   = '#8b949e'
ACCENT     = '#f78166'

FONT_TITLE = ('Courier', 26, 'bold')
FONT_CELL  = ('Courier', 42, 'bold')
FONT_LABEL = ('Courier', 11)
FONT_STAT  = ('Courier', 13, 'bold')
FONT_BTN   = ('Courier', 12, 'bold')
FONT_SMALL = ('Courier', 10)

TABLE_FILE = 'table.json'


# ---------------------------------------------------------------------------
# Helper: make a styled button
# ---------------------------------------------------------------------------
def _btn(parent, text, color, cmd, width=20, pady=9):
    b = tk.Button(
        parent, text=text, font=FONT_BTN,
        bg=color, fg=TEXT_ON,
        activebackground=color, activeforeground=TEXT_ON,
        relief='flat', cursor='hand2',
        padx=18, pady=pady, width=width,
        command=cmd,
    )
    return b


# ---------------------------------------------------------------------------
# Main application window
# ---------------------------------------------------------------------------
class TicTacToeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('TicTacToe  RL  |  Q-Learning')
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        # Shared state
        self._training   = False
        self._train_thread: threading.Thread | None = None

        self._show_menu()

    # -----------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------
    def _clear(self):
        """Destroy all widgets so we can redraw a new screen."""
        for w in self.root.winfo_children():
            w.destroy()

    # -----------------------------------------------------------------------
    # MENU SCREEN
    # -----------------------------------------------------------------------
    def _show_menu(self):
        self._training = False
        self._clear()

        outer = tk.Frame(self.root, bg=BG_DARK, padx=50, pady=35)
        outer.pack()

        # ASCII banner
        banner = (
            ' _____ _    _____    _____          \n'
            '|_   _|_|  |_   _|  |_   _|__  ___ \n'
            '  | | | |/ __| | |/ _` |/ __|\n'
            '  | | | | (__ | | (_| | (__ \n'
            '  |_| |_|\___| |_|\__,_|\\___|\n'
        )
        tk.Label(outer, text='TIC  TAC  TOE', font=FONT_TITLE,
                 bg=BG_DARK, fg=ACCENT).pack(pady=(0, 2))
        tk.Label(outer, text='Q - Learning  Reinforcement  AI',
                 font=FONT_LABEL, bg=BG_DARK, fg=TEXT_DIM).pack()

        # Decorative mini-board
        mini = tk.Frame(outer, bg=BG_DARK)
        mini.pack(pady=18)
        symbols = ['X', 'O', 'X', 'O', 'X', 'O', ' ', ' ', 'X']
        colors  = [COLOR_X, COLOR_O, COLOR_X, COLOR_O, COLOR_X,
                   COLOR_O, TEXT_DIM, TEXT_DIM, COLOR_X]
        for i, (sym, col) in enumerate(zip(symbols, colors)):
            r, c = divmod(i, 3)
            lbl = tk.Label(mini, text=sym, font=('Courier', 18, 'bold'),
                           bg=BG_CELL, fg=col, width=2, height=1, relief='flat')
            lbl.grid(row=r, column=c, padx=3, pady=3, ipadx=8, ipady=4)

        tk.Label(outer, text='', bg=BG_DARK).pack()  # spacer

        _btn(outer, 'Play  vs  AI',       BTN_GREEN,  self._show_play   ).pack(pady=5)
        _btn(outer, 'Train  AI',          BTN_PURPLE, self._show_train  ).pack(pady=5)
        _btn(outer, 'Test  Performance',  BTN_BLUE,   self._run_test    ).pack(pady=5)

        tk.Label(outer, text='\nby  EngineerNV  |  github.com/EngineerNV',
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_DIM).pack(pady=(20, 0))

    # -----------------------------------------------------------------------
    # PLAY SCREEN  (Human = O, goes first;  AI = X)
    # -----------------------------------------------------------------------
    def _show_play(self):
        self._clear()

        if not os.path.exists(TABLE_FILE):
            messagebox.showerror('No Model',
                                 'No table.json found.\nPlease train the AI first.')
            self._show_menu()
            return

        self._game = ticTac()
        self._q    = qLearning(0.6, 0.8)
        self._q.loadTable(TABLE_FILE)
        self._human_turn = True   # human (O) goes first

        outer = tk.Frame(self.root, bg=BG_DARK, padx=35, pady=22)
        outer.pack()

        tk.Label(outer, text='PLAY  VS  AI', font=FONT_TITLE,
                 bg=BG_DARK, fg=ACCENT).pack()
        tk.Label(outer, text='You are  O  |  AI is  X',
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_DIM).pack(pady=2)

        self._play_status = tk.StringVar(value='Your turn  ( O )')
        tk.Label(outer, textvariable=self._play_status, font=FONT_STAT,
                 bg=BG_DARK, fg=COLOR_O, width=28).pack(pady=(6, 14))

        # Clickable 3x3 board
        board_frame = tk.Frame(outer, bg=BG_DARK)
        board_frame.pack()
        self._play_cells: list[tk.Button] = []
        for i in range(9):
            r, c = divmod(i, 3)
            cell = tk.Button(
                board_frame, text='', font=FONT_CELL,
                bg=BG_CELL, fg=TEXT_ON,
                activebackground=CELL_HOVER,
                relief='flat', width=3, height=1,
                cursor='hand2',
                command=lambda idx=i: self._human_move(idx),
            )
            cell.grid(row=r, column=c, padx=4, pady=4, ipadx=10, ipady=10)
            self._play_cells.append(cell)

        # Legend
        legend = tk.Frame(outer, bg=BG_DARK)
        legend.pack(pady=(10, 0))
        tk.Label(legend, text='You = O', font=FONT_SMALL,
                 bg=BG_DARK, fg=COLOR_O).pack(side='left', padx=12)
        tk.Label(legend, text='AI = X', font=FONT_SMALL,
                 bg=BG_DARK, fg=COLOR_X).pack(side='left', padx=12)

        # Buttons
        btns = tk.Frame(outer, bg=BG_DARK)
        btns.pack(pady=(18, 0))
        _btn(btns, 'New  Game',   BTN_GREEN,  self._show_play,  width=14).pack(side='left', padx=5)
        _btn(btns, 'Main  Menu',  BG_CARD,    self._show_menu,  width=14).pack(side='left', padx=5)

    def _human_move(self, idx: int):
        if not self._human_turn:
            return
        r, c = divmod(idx, 3)
        if not self._game.playerTurn_rowCol(1, r, c):
            return   # cell already taken
        self._refresh_play_board()
        if self._check_play_end():
            return
        self._human_turn = False
        self._play_status.set('AI  is  thinking...')
        self.root.after(420, self._ai_play_move)   # slight pause for feel

    def _ai_play_move(self):
        state = self._game.board2Key()
        self._q.q_game_move(self._game, state, 2)
        self._refresh_play_board()
        if not self._check_play_end():
            self._human_turn = True
            self._play_status.set('Your turn  ( O )')

    def _refresh_play_board(self):
        linear = self._game.linearBoard()
        for i, cell in enumerate(self._play_cells):
            v = linear[i]
            if v == 1:
                cell.config(text='O', fg=COLOR_O, bg=BG_CELL, state='normal')
            elif v == 2:
                cell.config(text='X', fg=COLOR_X, bg=BG_CELL, state='normal')
            else:
                cell.config(text='', bg=BG_CELL, state='normal')

    def _check_play_end(self) -> bool:
        result = self._game.checkWin(False)
        if result is False:
            return False
        # Game over — show outcome
        if result == 2:
            self._play_status.set("It's  a  Tie!")
            self._highlight_board(COLOR_TIE)
        elif self._game.playerThatWon == 1:
            self._play_status.set('You  Win!  Nice move!')
            self._highlight_board(COLOR_O)
        else:
            self._play_status.set('AI  Wins!')
            self._highlight_board(COLOR_X)
        for cell in self._play_cells:
            cell.config(state='disabled', cursor='arrow')
        return True

    def _highlight_board(self, color: str):
        for cell in self._play_cells:
            if cell['text']:
                cell.config(bg=color)

    # -----------------------------------------------------------------------
    # TRAIN SCREEN
    # -----------------------------------------------------------------------
    def _show_train(self):
        self._clear()
        self._training = False
        self._ep_count = 0
        self._t_wins = self._t_ties = self._t_losses = 0

        outer = tk.Frame(self.root, bg=BG_DARK, padx=35, pady=20)
        outer.pack()

        tk.Label(outer, text='TRAINING  MODE', font=FONT_TITLE,
                 bg=BG_DARK, fg=BTN_PURPLE).pack()
        tk.Label(outer, text='Watch the AI improve in real time',
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_DIM).pack(pady=(2, 14))

        # ── Controls row ──────────────────────────────────────────────────
        ctrl = tk.Frame(outer, bg=BG_DARK)
        ctrl.pack(pady=(0, 10))

        tk.Label(ctrl, text='Episodes:', font=FONT_LABEL,
                 bg=BG_DARK, fg=TEXT_DIM).grid(row=0, column=0, sticky='e', padx=(0, 4))
        self._ep_var = tk.StringVar(value='20000')
        tk.Entry(ctrl, textvariable=self._ep_var, font=FONT_LABEL,
                 bg=BG_CARD, fg=TEXT_ON, insertbackground=TEXT_ON,
                 relief='flat', width=8).grid(row=0, column=1, padx=(0, 16))

        tk.Label(ctrl, text='Viz speed:', font=FONT_LABEL,
                 bg=BG_DARK, fg=TEXT_DIM).grid(row=0, column=2, sticky='e', padx=(0, 4))
        self._speed_var = tk.IntVar(value=5)
        tk.Scale(ctrl, variable=self._speed_var, from_=1, to=50,
                 orient='horizontal', bg=BG_DARK, fg=TEXT_DIM,
                 highlightthickness=0, sliderrelief='flat',
                 length=130, troughcolor=BG_CARD).grid(row=0, column=3)

        tk.Label(ctrl, text='(1=every game, 50=every 50th)',
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_DIM).grid(
                     row=1, column=2, columnspan=2, pady=(2, 0))

        # ── Live board ────────────────────────────────────────────────────
        board_frame = tk.Frame(outer, bg=BG_DARK)
        board_frame.pack()
        self._train_cells: list[tk.Label] = []
        for i in range(9):
            r, c = divmod(i, 3)
            lbl = tk.Label(board_frame, text='', font=FONT_CELL,
                           bg=BG_CELL, fg=TEXT_ON,
                           width=3, height=1, relief='flat')
            lbl.grid(row=r, column=c, padx=4, pady=4, ipadx=10, ipady=10)
            self._train_cells.append(lbl)

        # ── Stats row ─────────────────────────────────────────────────────
        stats = tk.Frame(outer, bg=BG_DARK)
        stats.pack(pady=(12, 0))

        self._sv_ep   = tk.StringVar(value='Episode:  0')
        self._sv_win  = tk.StringVar(value='Win:   0.0%')
        self._sv_tie  = tk.StringVar(value='Tie:   0.0%')
        self._sv_loss = tk.StringVar(value='Loss:  0.0%')
        self._sv_eps  = tk.StringVar(value='ε: 0.900')

        for sv, fg in [
            (self._sv_ep,   TEXT_ON),
            (self._sv_win,  COLOR_X),
            (self._sv_tie,  COLOR_TIE),
            (self._sv_loss, COLOR_O),
            (self._sv_eps,  BTN_PURPLE),
        ]:
            tk.Label(stats, textvariable=sv, font=FONT_STAT,
                     bg=BG_DARK, fg=fg, width=13).pack(side='left', padx=5)

        # ── Progress bar ──────────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use('default')
        style.configure('RL.Horizontal.TProgressbar',
                        troughcolor=BG_CARD, background=BTN_PURPLE,
                        bordercolor=BG_DARK, lightcolor=BTN_PURPLE,
                        darkcolor=BTN_PURPLE)
        self._progress = ttk.Progressbar(
            outer, length=460, mode='determinate',
            style='RL.Horizontal.TProgressbar')
        self._progress.pack(pady=(8, 0))

        self._sv_pct = tk.StringVar(value='0%')
        tk.Label(outer, textvariable=self._sv_pct, font=FONT_SMALL,
                 bg=BG_DARK, fg=TEXT_DIM).pack()

        # ── Action buttons ────────────────────────────────────────────────
        btns = tk.Frame(outer, bg=BG_DARK)
        btns.pack(pady=(14, 0))

        self._start_btn = _btn(btns, 'Start  Training', BTN_GREEN,
                               self._start_training, width=16)
        self._start_btn.pack(side='left', padx=5)

        self._stop_btn = _btn(btns, 'Stop  &  Save', BTN_RED,
                              self._stop_training, width=16)
        self._stop_btn.config(state='disabled')
        self._stop_btn.pack(side='left', padx=5)

        _btn(btns, 'Main  Menu', BG_CARD,
             self._safe_back_to_menu, width=12).pack(side='left', padx=5)

    # ── Training control ──────────────────────────────────────────────────

    def _start_training(self):
        try:
            total = int(self._ep_var.get())
            if total < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror('Bad Input', 'Episodes must be a positive integer.')
            return

        self._training = True
        self._t_wins = self._t_ties = self._t_losses = self._ep_count = 0
        self._start_btn.config(state='disabled')
        self._stop_btn.config(state='normal')
        self._progress['maximum'] = total
        self._progress['value']   = 0

        # Load existing knowledge if available
        q = qLearning(0.6, 0.8)
        if os.path.exists(TABLE_FILE):
            q.loadTable(TABLE_FILE)
        self._train_q = q

        self._train_thread = threading.Thread(
            target=self._train_loop, args=(total,), daemon=True)
        self._train_thread.start()

    def _stop_training(self):
        self._training = False
        self._start_btn.config(state='normal')
        self._stop_btn.config(state='disabled')
        if hasattr(self, '_train_q'):
            self._train_q.saveTable(TABLE_FILE)

    def _safe_back_to_menu(self):
        self._training = False
        if self._train_thread and self._train_thread.is_alive():
            self._train_thread.join(timeout=0.5)
        if hasattr(self, '_train_q') and self._ep_count > 0:
            self._train_q.saveTable(TABLE_FILE)
        self._show_menu()

    # ── Background training loop ──────────────────────────────────────────

    def _train_loop(self, total: int):
        """
        Runs entirely in a background thread.
        Communicates with the main thread only via root.after() callbacks —
        never touches tkinter widgets directly.
        """
        q    = self._train_q
        game = ticTac()

        epsilon       = 0.90    # start with lots of exploration
        epsilon_min   = 0.05
        epsilon_decay = (epsilon - epsilon_min) / total

        show_every = max(1, self._speed_var.get())  # update viz every N episodes

        for ep in range(1, total + 1):
            if not self._training:
                break

            game.clearBoard()
            game.randomMove(1)   # opponent (O) moves first

            while game.checkWin(False) == 0:
                state = game.board2Key()

                # Epsilon-greedy action selection
                if random.random() < epsilon:
                    action = game.randomMove(2)
                else:
                    action = q.q_game_move(game, state, 2)

                if action == -1:
                    break   # board full edge-case guard

                # Opponent responds only if game is still going
                if game.checkWin(False) == 0:
                    game.randomMove(1)

                next_state = game.board2Key()
                q.learn(state, next_state, action, game, 2)

            # Tally outcome
            result = game.checkWin(False)
            if result == 2:
                self._t_ties += 1
            elif game.playerThatWon == 2:
                self._t_wins += 1
            else:
                self._t_losses += 1

            epsilon = max(epsilon_min, epsilon - epsilon_decay)
            self._ep_count = ep

            # Schedule a UI refresh on the main thread
            if ep % show_every == 0 or ep == total:
                board_snap = list(game.linearBoard())
                ep_copy    = ep
                eps_copy   = epsilon
                w, t, l    = self._t_wins, self._t_ties, self._t_losses
                self.root.after(
                    0,
                    lambda b=board_snap, e=ep_copy, eps=eps_copy,
                           wins=w, ties=t, losses=l:
                    self._refresh_train_ui(b, e, eps, wins, ties, losses, total)
                )

        # Training finished or stopped
        self.root.after(0, self._training_finished)

    def _refresh_train_ui(self, board, ep, epsilon, wins, ties, losses, total):
        """Called on the main thread to update training widgets."""
        if not hasattr(self, '_train_cells'):
            return

        # Draw board
        for i, lbl in enumerate(self._train_cells):
            v = board[i]
            if v == 1:
                lbl.config(text='O', fg=COLOR_O, bg=BG_CELL)
            elif v == 2:
                lbl.config(text='X', fg=COLOR_X, bg=BG_CELL)
            else:
                lbl.config(text='', bg=BG_CELL)

        total_g = wins + ties + losses or 1
        wp = wins   / total_g * 100
        tp = ties   / total_g * 100
        lp = losses / total_g * 100
        pct = ep / total * 100

        self._sv_ep.set(f'Episode: {ep:,}')
        self._sv_win.set(f'Win:  {wp:5.1f}%')
        self._sv_tie.set(f'Tie:  {tp:5.1f}%')
        self._sv_loss.set(f'Loss: {lp:5.1f}%')
        self._sv_eps.set(f'ε: {epsilon:.3f}')
        self._progress['value'] = ep
        self._sv_pct.set(f'{pct:.1f}%')

    def _training_finished(self):
        self._training = False
        if hasattr(self, '_start_btn'):
            self._start_btn.config(state='normal')
            self._stop_btn.config(state='disabled')
        if hasattr(self, '_train_q'):
            self._train_q.saveTable(TABLE_FILE)

        total = self._ep_count or 1
        wp = self._t_wins   / total * 100
        tp = self._t_ties   / total * 100
        lp = self._t_losses / total * 100

        messagebox.showinfo(
            'Training Complete',
            f'Finished {self._ep_count:,} episodes\n\n'
            f'Win:  {wp:.1f}%\n'
            f'Tie:  {tp:.1f}%\n'
            f'Loss: {lp:.1f}%\n\n'
            f'Model saved → {TABLE_FILE}',
        )

    # -----------------------------------------------------------------------
    # QUICK TEST  (runs synchronously — 1000 games is instant)
    # -----------------------------------------------------------------------
    def _run_test(self):
        if not os.path.exists(TABLE_FILE):
            messagebox.showerror('No Model',
                                 'No table.json found.\nPlease train the AI first.')
            return

        q    = qLearning(0.6, 0.8)
        q.loadTable(TABLE_FILE)
        game = ticTac()
        wins = ties = losses = 0
        trials = 1000

        for _ in range(trials):
            game.clearBoard()
            game.randomMove(1)
            while game.checkWin(False) == 0:
                state = game.board2Key()
                q.q_game_move(game, state, 2)
                if game.checkWin(False) == 0:
                    game.randomMove(1)
            result = game.checkWin(False)
            if result == 2:
                ties += 1
            elif game.playerThatWon == 2:
                wins += 1
            else:
                losses += 1

        messagebox.showinfo(
            f'Test Results  ({trials:,} games vs random)',
            f'Win:  {wins/trials*100:.1f}%\n'
            f'Tie:  {ties/trials*100:.1f}%\n'
            f'Loss: {losses/trials*100:.1f}%\n\n'
            f'{"Undefeated!" if losses == 0 else f"Losses: {losses}"}',
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def launch():
    root = tk.Tk()
    app  = TicTacToeApp(root)
    root.mainloop()


if __name__ == '__main__':
    launch()
