"""
qLearning.py  --  TicTacToe RL  |  EngineerNV
Q-Learning agent for Tic-Tac-Toe.

Board positions (linear index):
  0 | 1 | 2
  3 | 4 | 5
  6 | 7 | 8

Values:  0 = empty,  1 = O (opponent),  2 = X (AI)
The AI always plays as X (player 2).
"""

import random
import json

from ticTac import ticTac


class qLearning:
    def __init__(self, alpha: float, gamma: float):
        """
        alpha (learning rate)  – how strongly each new experience updates Q-values.
                                  Range 0–1; 0.6 is a solid default.
        gamma (discount factor)– how much future rewards are valued relative to
                                  immediate ones. Range 0–1; 0.8 is a solid default.
        """
        self.learningRate  = alpha
        self.discountRate  = gamma
        self.qTable: dict  = {}   # state-string -> list of 9 Q-values

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------

    def loadTable(self, fileName: str):
        """Load a previously trained Q-table from a JSON file."""
        with open(fileName, 'r') as fp:
            self.qTable = json.load(fp)

    def saveTable(self, fileName: str):
        """Persist the current Q-table to a JSON file."""
        with open(fileName, 'w') as fp:
            json.dump(self.qTable, fp)

    # -----------------------------------------------------------------------
    # Q-table access
    # -----------------------------------------------------------------------

    def getQ(self, state: str, action: int | None = None):
        """
        Return Q-value(s) for a state.
        If action is None, returns the full list of 9 Q-values.
        Unseen states are initialised to all zeros (optimistic start).
        """
        if state not in self.qTable:
            self.qTable[state] = [0.0] * 9
        if action is None:
            return self.qTable[state]
        return self.qTable[state][action]

    def updateQ(self, state: str, action: int, value: float):
        """Write a single Q-value into the table, initialising the row if needed."""
        row = self.getQ(state)   # ensures row exists
        row[action] = value

    # -----------------------------------------------------------------------
    # Learning update  (Bellman equation)
    # -----------------------------------------------------------------------

    def learn(self, state: str, nextState: str, action: int,
              game: ticTac, player: int):
        """
        Apply the Q-Learning update rule:

          Q(s, a)  ←  (1 - α) · Q(s, a)
                     + α · [ R(s, a) + γ · max_a' Q(s', a') ]

        The reward R is computed from the game's current outcome.
        If the game is over there are no future Q-values to add.
        """
        reward = game.moveReward(player)

        if game.checkWin(False):
            # Terminal state: no future value
            target = reward
        else:
            # Only consider Q-values for cells that are still empty
            future_qs = [self.getQ(nextState)[i] for i in game.emptySpaces()]
            target = reward + self.discountRate * max(future_qs)

        current  = self.getQ(state, action)
        new_val  = current * (1 - self.learningRate) + self.learningRate * target
        self.updateQ(state, action, new_val)

    # -----------------------------------------------------------------------
    # Action selection
    # -----------------------------------------------------------------------

    def q_game_move(self, game: ticTac, state: str, ai_player: int) -> int:
        """
        Pure exploitation: pick the legal move with the highest Q-value.
        Returns the linear board index of the chosen action.
        """
        empty   = game.emptySpaces()
        q_vals  = self.getQ(state)
        # Filter to only legal (empty) cells, then pick the argmax
        action  = max(empty, key=lambda i: q_vals[i])
        game.playerTurn_linBoard(ai_player, action)
        return action

    # -----------------------------------------------------------------------
    # CLI training loop  (epsilon-greedy with linear decay)
    # -----------------------------------------------------------------------

    def train(self, epochs: int, game: ticTac, ai_player: int,
              random_player: int, epsilon_start: float = 0.90,
              epsilon_end: float = 0.05):
        """
        Train for `epochs` episodes against a random opponent.

        Exploration follows a linearly-decaying epsilon schedule:
          - Starts at epsilon_start (lots of exploration early on)
          - Decays to epsilon_end   (mostly exploitation by the end)

        The AI plays as `ai_player`, the random agent as `random_player`.
        """
        epsilon       = epsilon_start
        epsilon_decay = (epsilon_start - epsilon_end) / epochs

        for _ in range(epochs):
            game.clearBoard()
            game.randomMove(random_player)   # opponent goes first

            while game.checkWin(False) == 0:
                state = game.board2Key()

                # Epsilon-greedy: explore or exploit
                if random.random() < epsilon:
                    action = game.randomMove(ai_player)
                else:
                    action = self.q_game_move(game, state, ai_player)

                if action == -1:
                    break   # board full guard

                # Opponent responds — only if the game is still going
                if game.checkWin(False) == 0:
                    game.randomMove(random_player)

                next_state = game.board2Key()
                self.learn(state, next_state, action, game, ai_player)

            epsilon = max(epsilon_end, epsilon - epsilon_decay)

    # -----------------------------------------------------------------------
    # Evaluation loop
    # -----------------------------------------------------------------------

    def test(self, trials: int, game: ticTac, ai_player: int,
             random_player: int):
        """
        Run `trials` games (pure exploitation, no exploration) and print stats.
        """
        wins = ties = losses = 0

        for _ in range(trials):
            game.clearBoard()
            game.randomMove(random_player)

            while game.checkWin(False) == 0:
                state = game.board2Key()
                self.q_game_move(game, state, ai_player)
                # Opponent responds only if AI didn't just end the game
                if game.checkWin(False) == 0:
                    game.randomMove(random_player)

            result = game.checkWin(False)
            if result == 2:
                ties += 1
            elif game.playerThatWon == ai_player:
                wins += 1
            else:
                losses += 1

        print(f'Tic Tac Stats  -->  {trials} games')
        print(f'  Win  : {wins   / trials * 100:.1f}%')
        print(f'  Tie  : {ties   / trials * 100:.1f}%')
        print(f'  Loss : {losses / trials * 100:.1f}%')
