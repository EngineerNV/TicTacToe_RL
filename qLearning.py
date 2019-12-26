# this class is used to implement Q learning techniques for a tictactoe game
# it is assumed that the ai is always going second while playing 

# actions correlate to this format, of what cell would be taken
# the state is the combo of different x and o's on the board
# Board 3x3
#  0	1	  2
#  3    4     5
#  6    7     8
# this relies on class objects from ticTac.py
# the board is a double list of integers
# 0 == empty, 1 == O, 2 == X
# the AI player will act as X
# the random player will act as O


from ticTac import ticTac
import random

class qLearning:
    def __init__(self, alpha, gamma):
        self.qTable = {}  # this will be a dictionary where the state is the key, and the list is
        self.learningRate = alpha
        self.discountRate = gamma

    def updateQ(self, state, action, value):  # this updates the q table, and intializes the Q row if not already
        if state in self.qTable:
            qActList = self.qTable[state]
            qActList[action] = value
        else:
            qActList = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            qActList[action] = value
            self.qTable[state] = qActList

    def getQ(self, state, action=None):
        if state not in self.qTable:  # initialize q table state action set if not already in dictionary
            self.qTable[state] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        if action == None:  # return entire action list if no action specified
            return self.qTable[state]
        qActList = self.qTable[state]
        return qActList[action]

    def learn(self, state, nextState, action, game, player):  # Q(s,a) = (1-alpha)*Q(s,a) + alpha*(R_t+gamma* Q_a max(s_t+1,a))
        futureQList = []
        reward = game.moveReward(player)
        qActions = self.getQ(nextState)
        for i in game.emptySpaces():
            futureQList.append(qActions[i])
        if game.checkWin(False):  # if we have a game over there will be no future value to add
            learningChange = reward
        else:  # if we are still playing
            learningChange = reward + self.discountRate * (max(futureQList))
        newQValue = self.getQ(state, action) * (1 - self.learningRate) + self.learningRate * learningChange
        self.updateQ(state, action, newQValue)

    def train(self, epochs, game, ai_q, ai_random):
        for i in range(0, epochs):  # performing the episodes
            game.clearBoard()  # making sure we have a fresh board
            game.randomMove(ai_random)  # making opponent make the first move
            while game.checkWin(False) == 0:
                state = game.board2Key()
                explore = random.randint(0, 4)  # 25 % chance of choosing a random action
                if explore == 0:
                    action = game.randomMove(ai_q)
                else:
                    actFree = game.emptySpaces()  # these three lines make sure we don't use Qs action of filled spaces
                    freeQ = [x for i, x in enumerate(self.getQ(state)) if i in actFree]
                    action = actFree[freeQ.index(max(freeQ))]
                    game.playerTurn_linBoard(ai_q, action)  # updating choice
                game.randomMove(ai_random)  # opponent chooses
                nextState = game.board2Key()
                self.learn(state, nextState, action, game, ai_q) # updating Q table with moves

q = qLearning(.6, .8)
t = ticTac()
q.train(50,t,2,1)
print(q.qTable)
