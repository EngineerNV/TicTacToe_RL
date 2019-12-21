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


class qLearning:
	def __init__(self, alpha, gamma):
		self.qReward = {} # this will be a dictionary where the state is the key, and the list is 
		self.learrningRate = alpha
		self.discountRate = gamma

