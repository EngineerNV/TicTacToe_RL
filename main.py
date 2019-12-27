#  Created by Nick Vaughn ---> EngineerNV
# this main function allows you to play with a prebuilt AI, train the AI, and test the AI
# for Tic Tac Toe using Q Learning techniques

# there is no error checking, so make sure to check arguments!

# example running the code, made for python 3
# play test against the AI yourself, with trained weights
#  python3 main.py -p table.json

# -------------------------------------------------------------
# train the AI against a random agent with alpha and gamma.
# alpha is learning rate, gamma is discount rate--> closer to 1
# means you value future rewards more, saves the weights
# python3 main.py -train table.json 10000 alpha gamma
# python3 main.py -train table.json 10000 .6 .8

# --------------------------------------------------------------
# test the ai over a certain amount of games against a random agent, with loaded weights
# python3 main.py -test table.json 100


import sys
from ticTac import ticTac
from qLearning import qLearning



def play(fileName, player, ai):
    game = ticTac()
    q = qLearning(.6, .8)
    q.loadTable(fileName)

    game.printBoard()
    print()
    print('------------------')
    print()
    row = input('Choose Row 0-2:')
    col = input('Choose Col 0-2:')
    game.playerTurn_rowCol(player, int(row), int(col))
    while 1:
        state = game.board2Key()
        q.q_game_move(game, state, ai)
        game.printBoard()
        if game.checkWin(True):
            break
        print()
        print('------------------')
        print()
        row = input('Choose Row 0-2:')
        col = input('Choose Col 0-2:')
        game.playerTurn_rowCol(player, int(row), int(col))

def main():
    game = ticTac()
    if sys.argv[1] == '-p':
        play(sys.argv[2], 1, 2)
    elif sys.argv[1] == '-test':
        q = qLearning(.6, .8)
        q.loadTable(sys.argv[2])
        q.test(int(sys.argv[3]), game, 1, 2)
    elif sys.argv[1] == '-train':
        q = qLearning(float(sys.argv[4]), float(sys.argv[5]))
        q.train(int(sys.argv[3]), game, 1, 2)
        q.saveTable(sys.argv[2])
if __name__ == "__main__":
    main()