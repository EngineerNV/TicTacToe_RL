"""
main.py  --  TicTacToe RL  |  EngineerNV
Command-line entry point for training, testing, and playing Tic-Tac-Toe
against a Q-Learning AI.

Usage
-----
  GUI (recommended):
      python3 main.py -gui

  Play against the AI in the terminal:
      python3 main.py -p table.json

  Train the AI (saves weights to file):
      python3 main.py -train table.json <episodes> <alpha> <gamma>
      python3 main.py -train table.json 20000 0.6 0.8

  Test AI performance over N games:
      python3 main.py -test table.json <num_games>
      python3 main.py -test table.json 1000
"""

import sys
from ticTac import ticTac
from qLearning import qLearning


# ---------------------------------------------------------------------------
# Terminal play mode  (human = O, goes first;  AI = X)
# ---------------------------------------------------------------------------

def play(fileName: str):
    """Interactive human-vs-AI game in the terminal."""
    game = ticTac()
    q    = qLearning(0.6, 0.8)
    q.loadTable(fileName)

    print('\nBoard positions:')
    print(' 0 | 1 | 2')
    print(' 3 | 4 | 5')
    print(' 6 | 7 | 8')
    print('\nYou are O  |  AI is X\n')

    while True:
        # ── Human move ────────────────────────────────────────────────────
        game.printBoard()
        print('\n------------------')
        try:
            row = int(input('Choose Row 0-2: '))
            col = int(input('Choose Col 0-2: '))
        except ValueError:
            print('Please enter a number.')
            continue

        if not game.playerTurn_rowCol(1, row, col):
            print('Cell already taken — try again.')
            continue

        if game.checkWin(True):
            game.printBoard()
            break

        # ── AI move ───────────────────────────────────────────────────────
        state = game.board2Key()
        q.q_game_move(game, state, 2)
        print()

        if game.checkWin(True):
            game.printBoard()
            break


# ---------------------------------------------------------------------------
# CLI dispatcher
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]

    if mode == '-gui':
        # Launch the tkinter GUI
        try:
            from gui import launch
        except ModuleNotFoundError:
            print('tkinter is not installed.')
            print('On Debian/Ubuntu:  sudo apt install python3-tk')
            sys.exit(1)
        launch()

    elif mode == '-p':
        if len(sys.argv) < 3:
            print('Usage: python3 main.py -p <table_file>')
            sys.exit(1)
        play(sys.argv[2])

    elif mode == '-test':
        if len(sys.argv) < 4:
            print('Usage: python3 main.py -test <table_file> <num_games>')
            sys.exit(1)
        game = ticTac()
        q    = qLearning(0.6, 0.8)
        q.loadTable(sys.argv[2])
        q.test(int(sys.argv[3]), game, 2, 1)

    elif mode == '-train':
        if len(sys.argv) < 6:
            print('Usage: python3 main.py -train <table_file> <episodes> <alpha> <gamma>')
            sys.exit(1)
        table_file = sys.argv[2]
        episodes   = int(sys.argv[3])
        alpha      = float(sys.argv[4])
        gamma      = float(sys.argv[5])

        game = ticTac()
        q    = qLearning(alpha, gamma)

        # Continue from existing weights if the file already exists
        import os
        if os.path.exists(table_file):
            q.loadTable(table_file)
            print(f'Loaded existing weights from {table_file}')

        print(f'Training for {episodes:,} episodes  (alpha={alpha}, gamma={gamma}) ...')
        q.train(episodes, game, 2, 1)
        q.saveTable(table_file)
        print(f'Done — weights saved to {table_file}')

    else:
        print(f'Unknown mode: {mode}')
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
