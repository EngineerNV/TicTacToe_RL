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
        self._training     = False
        self._train_thread: threading.Thread | None = None
        self._about_active = False   # stops about-screen animations on navigate-away

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
        self._training     = False
        self._about_active = False
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
        _btn(outer, 'How  It  Works',     ACCENT,     self._show_about,
             width=20, pady=9).pack(pady=5)

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
        # Widgets may have been destroyed if the user navigated away mid-training
        if not self._train_cells[0].winfo_exists():
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
        # Guard: buttons may have been destroyed if the user navigated away
        if hasattr(self, '_start_btn') and self._start_btn.winfo_exists():
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
# HOW IT WORKS  (recruiter-friendly animated explainer)
# ---------------------------------------------------------------------------

    # ── helpers ──────────────────────────────────────────────────────────────

    def _show_about(self):
        self._about_active = True
        self._clear()

        # ── scrollable container ──────────────────────────────────────────
        wrapper = tk.Frame(self.root, bg=BG_DARK)
        wrapper.pack(fill='both', expand=True)

        vscroll = tk.Scrollbar(wrapper, orient='vertical', bg=BG_DARK,
                               troughcolor=BG_CARD, activebackground=TEXT_DIM)
        vscroll.pack(side='right', fill='y')

        canvas = tk.Canvas(wrapper, bg=BG_DARK, highlightthickness=0,
                           yscrollcommand=vscroll.set)
        canvas.pack(side='left', fill='both', expand=True)
        vscroll.config(command=canvas.yview)

        outer = tk.Frame(canvas, bg=BG_DARK, padx=22, pady=14)
        win = canvas.create_window((0, 0), window=outer, anchor='nw')

        def _on_resize(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        outer.bind('<Configure>', _on_resize)

        # mousewheel scrolling
        def _on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        canvas.bind_all('<MouseWheel>', _on_wheel)
        canvas.bind_all('<Button-4>',
                        lambda e: canvas.yview_scroll(-1, 'units'))
        canvas.bind_all('<Button-5>',
                        lambda e: canvas.yview_scroll( 1, 'units'))

        # ── content ───────────────────────────────────────────────────────
        tk.Label(outer, text='HOW  THE  AI  LEARNS',
                 font=FONT_TITLE, bg=BG_DARK, fg=ACCENT).pack()
        tk.Label(outer,
                 text='No  ML  degree  required  —  plain  English  guide',
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_DIM).pack(pady=(2, 14))

        # 2 × 2 card grid
        row1 = tk.Frame(outer, bg=BG_DARK)
        row1.pack()
        self._about_card_trial(row1)
        self._about_card_rewards(row1)

        tk.Frame(outer, bg=BG_DARK, height=8).pack()

        row2 = tk.Frame(outer, bg=BG_DARK)
        row2.pack()
        self._about_card_qtable(row2)
        self._about_card_results(row2)

        _btn(outer, '←  Main  Menu', BG_CARD,
             self._show_menu, width=18).pack(pady=(16, 8))

    def _about_card(self, parent, title, color, w=370, h=None):
        """Styled card frame with a coloured title."""
        card = tk.Frame(parent, bg=BG_CARD, padx=14, pady=12)
        card.pack(side='left', padx=6, pady=4)
        tk.Label(card, text=title, font=FONT_STAT,
                 bg=BG_CARD, fg=color).pack(anchor='w', pady=(0, 6))
        return card

    # ── card 1 : trial & error ────────────────────────────────────────────

    def _about_card_trial(self, parent):
        card = self._about_card(parent, '01  TRIAL  &  ERROR', BTN_GREEN)

        tk.Label(card,
                 text=(
                     'The AI starts knowing\n'
                     'absolutely nothing.\n\n'
                     'It plays thousands of\n'
                     'games, remembers what\n'
                     'worked and what did not,\n'
                     'and keeps improving.\n\n'
                     'Think of it like a\n'
                     'new player grinding\n'
                     'ranked matches.'
                 ),
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM,
                 justify='left').pack(anchor='w')

        cv = tk.Canvas(card, width=152, height=152,
                       bg=BG_CARD, highlightthickness=0)
        cv.pack(pady=(10, 4))

        self._trial_stage_var = tk.StringVar()
        tk.Label(card, textvariable=self._trial_stage_var,
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM,
                 width=26).pack()

        # three snapshots that show the arc of learning
        stages = [
            ([0,1,0, 2,0,1, 0,2,0],  'Episode 1  —  random chaos',  []),
            ([1,0,2, 1,2,0, 0,2,1],  'Episode 5,000  —  improving', []),
            ([1,1,2, 0,2,0, 2,0,1],  'Episode 20,000  —  X wins!',  [2,4,6]),
        ]
        self._draw_trial_board(cv, stages, 0)

    def _draw_trial_board(self, cv, stages, idx):
        if not self._about_active:
            return
        try:
            cv.winfo_exists()
        except Exception:
            return

        board, label, win_cells = stages[idx % len(stages)]
        cv.delete('all')
        sz, pad = 44, 10

        for i, val in enumerate(board):
            r, c = divmod(i, 3)
            x1 = pad + c * (sz + 4)
            y1 = pad + r * (sz + 4)
            x2, y2 = x1 + sz, y1 + sz
            bg = COLOR_WIN if i in win_cells else BG_CELL
            cv.create_rectangle(x1, y1, x2, y2, fill=bg, outline='')
            if val == 1:
                cv.create_text((x1+x2)//2, (y1+y2)//2,
                               text='O', font=('Courier', 22, 'bold'),
                               fill=COLOR_O)
            elif val == 2:
                cv.create_text((x1+x2)//2, (y1+y2)//2,
                               text='X', font=('Courier', 22, 'bold'),
                               fill=COLOR_X)

        self._trial_stage_var.set(label)
        self.root.after(2200,
                        lambda: self._draw_trial_board(cv, stages, idx + 1))

    # ── card 2 : reward system ────────────────────────────────────────────

    def _about_card_rewards(self, parent):
        card = self._about_card(parent, '02  REWARD  SYSTEM', BTN_PURPLE)

        tk.Label(card,
                 text=(
                     'After every game the AI\n'
                     'receives a score.\n\n'
                     'Big rewards for wins.\n'
                     'Small reward for ties.\n'
                     'Massive penalty for\n'
                     'losses.\n\n'
                     'The HUGE loss penalty\n'
                     '(-40) forces the AI to\n'
                     'learn "never lose first,\n'
                     'then try to win."'
                 ),
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM,
                 justify='left').pack(anchor='w')

        chips = tk.Frame(card, bg=BG_CARD)
        chips.pack(pady=(14, 0))

        self._reward_chip_data = [
            ('WIN',  '+10', BTN_GREEN),
            ('TIE',  '+5',  COLOR_TIE),
            ('LOSS', '-40', BTN_RED),
        ]
        self._reward_chip_widgets = []
        for label, val, color in self._reward_chip_data:
            f = tk.Frame(chips, bg=color, padx=12, pady=10)
            f.pack(side='left', padx=6)
            lbl = tk.Label(f, text=label,
                           font=('Courier', 9, 'bold'), bg=color, fg=TEXT_ON)
            lbl.pack()
            num = tk.Label(f, text=val,
                           font=('Courier', 20, 'bold'), bg=color, fg=TEXT_ON)
            num.pack()
            self._reward_chip_widgets.append((f, lbl, num, color))

        tk.Label(card,
                 text='\nResult: the AI is\nUNDEFEATED.',
                 font=('Courier', 11, 'bold'), bg=BG_CARD, fg=ACCENT,
                 justify='left').pack(anchor='w', pady=(8, 0))

        self._pulse_chip(0, True)

    def _pulse_chip(self, idx, highlight):
        if not self._about_active:
            return
        if not self._reward_chip_widgets:
            return
        f, lbl, num, base = self._reward_chip_widgets[idx % len(self._reward_chip_widgets)]
        try:
            if not f.winfo_exists():
                return
            if highlight:
                f.config(bg=TEXT_ON)
                lbl.config(bg=TEXT_ON, fg=base)
                num.config(bg=TEXT_ON, fg=base)
            else:
                f.config(bg=base)
                lbl.config(bg=base, fg=TEXT_ON)
                num.config(bg=base, fg=TEXT_ON)
        except tk.TclError:
            return
        delay = 280 if highlight else 1000
        next_idx = idx if highlight else idx + 1
        self.root.after(delay,
                        lambda: self._pulse_chip(next_idx, not highlight))

    # ── card 3 : q-table ─────────────────────────────────────────────────

    def _about_card_qtable(self, parent):
        card = self._about_card(parent, '03  AI  MEMORY  ( Q-TABLE )', BTN_BLUE)

        tk.Label(card,
                 text=(
                     'The AI keeps a "cheat\n'
                     'sheet" called a Q-Table.\n\n'
                     'For every possible board\n'
                     'it stores a score for\n'
                     'each empty cell.\n\n'
                     'Higher score = smarter\n'
                     'move for that situation.\n\n'
                     'The star  ★  marks\n'
                     'the move it picks.'
                 ),
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM,
                 justify='left').pack(anchor='w')

        cv = tk.Canvas(card, width=160, height=160,
                       bg=BG_CARD, highlightthickness=0)
        cv.pack(pady=(10, 4))

        # example board: 1=O, 2=X, 0=empty
        board = [1, 0, 2,  0, 2, 0,  0, 0, 1]
        # Q-values for each cell (0 for occupied cells)
        qvals = [0, 3.2, 0,  4.1, 0, 2.8,  7.9, 1.5, 0]

        tk.Label(card,
                 text='Bright purple = best move',
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM).pack()

        self._animate_qtable(cv, board, qvals, 0)

    def _animate_qtable(self, cv, board, qvals, step):
        if not self._about_active:
            return
        try:
            if not cv.winfo_exists():
                return
        except Exception:
            return

        cv.delete('all')
        max_steps = 40
        frac = min(1.0, step / max_steps)
        best = qvals.index(max(qvals))
        sz, pad = 46, 10

        for i, val in enumerate(board):
            r, c = divmod(i, 3)
            x1 = pad + c * (sz + 4)
            y1 = pad + r * (sz + 4)
            x2, y2 = x1 + sz, y1 + sz

            if val == 0:
                q = qvals[i]
                intensity = int(frac * min(1.0, q / 8.0) * 200)
                if i == best:
                    # purple highlight for best move
                    g_val = max(0, 0x57 - intensity // 2)
                    fill  = f'#{min(255, 0x89 + intensity):02x}{g_val:02x}{min(255,0xe5):02x}'
                elif q > 0:
                    fill  = f'#20{min(255, 0x30 + intensity):02x}20'
                else:
                    fill  = BG_CELL
            else:
                fill = BG_CELL

            cv.create_rectangle(x1, y1, x2, y2, fill=fill, outline='')

            if val == 1:
                cv.create_text((x1+x2)//2, (y1+y2)//2,
                               text='O', font=('Courier', 20, 'bold'),
                               fill=COLOR_O)
            elif val == 2:
                cv.create_text((x1+x2)//2, (y1+y2)//2,
                               text='X', font=('Courier', 20, 'bold'),
                               fill=COLOR_X)
            elif i == best and step >= max_steps:
                cv.create_text((x1+x2)//2, (y1+y2)//2,
                               text='★', font=('Courier', 20),
                               fill=TEXT_ON)

        if step < max_steps:
            self.root.after(40,
                            lambda: self._animate_qtable(cv, board, qvals, step + 1))
        else:
            self.root.after(2500,
                            lambda: self._animate_qtable(cv, board, qvals, 0))

    # ── card 4 : results ─────────────────────────────────────────────────

    def _about_card_results(self, parent):
        card = self._about_card(parent, '04  AFTER  20,000  GAMES', ACCENT)

        tk.Label(card,
                 text=(
                     'Tested against 1,000\n'
                     'games of pure random\n'
                     'play:\n'
                 ),
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM,
                 justify='left').pack(anchor='w')

        cv = tk.Canvas(card, width=200, height=145,
                       bg=BG_CARD, highlightthickness=0)
        cv.pack()

        tk.Label(card,
                 text=(
                     'Zero losses.  Ever.\n\n'
                     'The AI found the optimal\n'
                     'strategy through pure\n'
                     'trial and error —\n'
                     'no human guidance,\n'
                     'no hand-coded rules.'
                 ),
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM,
                 justify='left').pack(anchor='w', pady=(8, 0))

        tk.Label(card,
                 text='That\'s  Reinforcement\nLearning.',
                 font=('Courier', 11, 'bold'), bg=BG_CARD, fg=ACCENT,
                 justify='left').pack(anchor='w', pady=(6, 0))

        self._animate_results(cv, 0)

    def _animate_results(self, cv, step):
        if not self._about_active:
            return
        try:
            if not cv.winfo_exists():
                return
        except Exception:
            return

        cv.delete('all')
        max_steps = 55
        frac  = min(1.0, step / max_steps)
        bars  = [('Win', 57.0, COLOR_X), ('Tie', 43.0, COLOR_TIE), ('Loss', 0.0, BTN_RED)]
        bw    = 46
        gap   = 22
        base_y = 120
        max_h  = 95
        start_x = 18

        for j, (label, pct, color) in enumerate(bars):
            x = start_x + j * (bw + gap)
            h = int(pct / 100 * max_h * frac)
            cv.create_rectangle(x, base_y - h, x + bw, base_y,
                                fill=color, outline='')
            cv.create_text(x + bw // 2, base_y + 11,
                           text=label, font=('Courier', 9), fill=TEXT_DIM)
            if step >= max_steps:
                cv.create_text(x + bw // 2, base_y - h - 11,
                               text=f'{pct:.0f}%',
                               font=('Courier', 9, 'bold'), fill=TEXT_ON)

        if step < max_steps:
            self.root.after(28,
                            lambda: self._animate_results(cv, step + 1))
        else:
            self.root.after(3000,
                            lambda: self._animate_results(cv, 0))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def launch():
    root = tk.Tk()
    app  = TicTacToeApp(root)
    root.mainloop()


if __name__ == '__main__':
    launch()
