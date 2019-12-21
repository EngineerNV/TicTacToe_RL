# created by EngineerNV github
# this code is the main logic for a tic tac toe
# it is a class that holds all of the logic and win conditions
# tracks player one and player two
import random


class ticTac:
    def __init__(self):
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # setup board: 0 is empty, 1 is player 1 etc

    def printBoard(self):
        for row in self.board:
            for element in row:
                print(str(element) + '\t', end='')
            print(end='\n')

    def playerTurn(self, player, r, c): # taking up board
        if self.board[r][c] == 0:
            self.board[r][c] = player
            return True
        else:
            print('invalid move')
            return False

    def randomMove(self, player): # keeps running until we take up a free space
        finished = False
        if self.checkBoardFull():
            return
        while finished == False:
            r = random.randint(0, 2)
            c = random.randint(0, 2)
            finished = self.playerTurn(player, r, c)

    def clearBoard(self): # clearing the board placements with 0
        for row in self.board:
            for element in row:
                element = 0

    def checkBoardFull(self): # boolean function returning True or False
        element = 0
        return 1 ^ (any(element in rowList for rowList in self.board))

    def checkWin(self):  # checking win conditions
        maxRow, maxCol = 3, 3
        if self.checkBoardFull() == True:
            print("Tie Game")
            return 2  # special output for a tie
        for r in range(maxRow):
            for c in range(maxCol):
                player = self.board[r][c]
                if r == 0 and c == 0 and player != 0:  # if we have a player spot in top left corner
                    if self.board[r+1][c+1] == self.board[r+2][c+2] == player:
                        print('Player '+str(player) + ' Wins!')
                        return True
                    elif self.board[r+1][c] == self.board[r+2][c] == player:  # down horizontal
                        print('Player ' + str(player) + ' Wins!')
                        return True
                    elif self.board[r][c+1] == self.board[r][c+2] == player:  # right horizontal
                        print('Player ' + str(player) + ' Wins!')
                        return True
                elif r == 2 and c == 2 and player != 0:  # if we have a player spot in bottom right corner
                    if self.board[r][c-2] == self.board[r][c-1] == player:  # right horizontal
                        print('Player ' + str(player) + ' Wins!')
                        return True
                    elif self.board[r-2][c] == self.board[r-1][c] == player:  # up horizontal
                        print('Player ' + str(player) + ' Wins!')
                        return True
                elif r == 0 and c == 2 and player != 0:  # if we have a player spot in top right corner
                    if self.board[r+2][c-2] == self.board[r+1][c-1] == player:
                        print('Player ' + str(player) + ' Wins!')
                        return True
        return False
a = ticTac()


while a.checkWin() == False:
    a.randomMove(1)
    a.randomMove(2)
a.printBoard()
print(a.checkWin())