"""
ticTac.py  --  TicTacToe RL  |  EngineerNV
Game engine for Tic-Tac-Toe.

Board is a 3x3 nested list.
  0 = empty cell
  1 = Player O
  2 = Player X

Linear index mapping (left-to-right, top-to-bottom):
  0 | 1 | 2
  3 | 4 | 5
  6 | 7 | 8
"""

import random


class ticTac:
    def __init__(self):
        self.board           = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.playerThatWon   = 0
        # Lookup table: linear index -> (row, col)
        self._idx_to_rc      = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2),
            (2, 0), (2, 1), (2, 2),
        ]

    # -----------------------------------------------------------------------
    # Display
    # -----------------------------------------------------------------------

    def printBoard(self):
        """Print the board to stdout using O / X / * symbols."""
        symbols = {1: 'O', 2: 'X', 0: '*'}
        for row in self.board:
            print('\t'.join(symbols[v] for v in row))

    # -----------------------------------------------------------------------
    # Move placement
    # -----------------------------------------------------------------------

    def playerTurn_rowCol(self, player: int, r: int, c: int) -> bool:
        """Place a token at (row, col). Returns False if the cell is taken."""
        if self.board[r][c] != 0:
            return False
        self.board[r][c] = player
        return True

    def playerTurn_linBoard(self, player: int, index: int) -> bool:
        """Place a token using a linear index 0-8. Returns False if taken."""
        r, c = self._idx_to_rc[index]
        return self.playerTurn_rowCol(player, r, c)

    def randomMove(self, player: int) -> int:
        """
        Make a uniformly random legal move for `player`.
        Returns the linear index of the chosen cell, or -1 if the board is full.
        """
        if self.checkBoardFull():
            return -1
        empty = self.emptySpaces()
        index = random.choice(empty)
        self.playerTurn_linBoard(player, index)
        return index

    # -----------------------------------------------------------------------
    # Board state queries
    # -----------------------------------------------------------------------

    def clearBoard(self):
        """Reset the board and winner tracking to the initial state."""
        self.board         = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.playerThatWon = 0

    def linearBoard(self) -> list:
        """Return the board as a flat list of 9 values (row-major order)."""
        return self.board[0] + self.board[1] + self.board[2]

    def board2Key(self) -> str:
        """
        Encode the current board state as a 9-character string.
        Used as the dictionary key in the Q-table.
        e.g. '000210020'
        """
        return ''.join(str(v) for v in self.linearBoard())

    def emptySpaces(self) -> list:
        """Return a list of linear indices for all unoccupied cells."""
        return [i for i, v in enumerate(self.linearBoard()) if v == 0]

    def checkBoardFull(self) -> bool:
        """Return True if every cell is occupied (no empty spaces left)."""
        return all(v != 0 for row in self.board for v in row)

    # -----------------------------------------------------------------------
    # Reward for RL
    # -----------------------------------------------------------------------

    def moveReward(self, player: int) -> float:
        """
        Return the immediate reward for `player` given the current board:
          +10  win
          + 5  tie
          -40  loss  (high penalty encourages the AI to avoid losing)
            0  game still in progress
        """
        outcome = self.checkWin(False)
        if outcome == 0 or outcome is False:
            return 0       # game still going
        if self.playerThatWon == player:
            return 10      # win
        if self.playerThatWon == 0:
            return 5       # tie
        return -40         # loss

    # -----------------------------------------------------------------------
    # Win detection
    # -----------------------------------------------------------------------

    def checkWin(self, verbose: bool):
        """
        Check all win conditions on the current board.

        Returns:
          True  – a player has three in a row (sets self.playerThatWon)
          2     – the board is full with no winner (tie)
          False – game is still in progress

        Pass verbose=True to print the result to stdout.
        """
        b = self.board

        # Check all rows, columns, and the two diagonals
        lines = [
            # rows
            [b[0][0], b[0][1], b[0][2]],
            [b[1][0], b[1][1], b[1][2]],
            [b[2][0], b[2][1], b[2][2]],
            # columns
            [b[0][0], b[1][0], b[2][0]],
            [b[0][1], b[1][1], b[2][1]],
            [b[0][2], b[1][2], b[2][2]],
            # diagonals
            [b[0][0], b[1][1], b[2][2]],
            [b[0][2], b[1][1], b[2][0]],
        ]

        for line in lines:
            if line[0] != 0 and line[0] == line[1] == line[2]:
                self.playerThatWon = line[0]
                if verbose:
                    print(f'Player {line[0]} Wins!')
                return True

        # No winner yet — check for tie
        if self.checkBoardFull():
            self.playerThatWon = 0
            if verbose:
                print('Tie Game')
            return 2

        self.playerThatWon = 0
        return False
