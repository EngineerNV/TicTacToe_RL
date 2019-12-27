# RL Q learning TIC TAC TOE

Created by Nick Vaughn

This repo is used as a tutorial to show how to use RL methods into games with changing
or multiple states that cannot be cateloged with a simple switch statement

We have an AI learning for a random agent opponent that does not have intelligence in plays

The Algorithm relies heavily on the following Q learning formula 

There is a 25 % chance that during training that the move being made will be random, instead of using Q learning  

Q leanring focuses on the actions made between states, I store the States inside of a dictionary with a list of 9 elements representing
the actions that can be taken at the state.

Alpha is the learning rate, determines how much we change the Q value from changing values 
gamma is the dicount factor --- value between 0<gamma<=1, the closer to one, the more important future rewards are to algorithm

LearningChange = R(s_prime,a)+ gamma*maxQ(s_prime,all a's)
Q(s,action) = Q(s, action) * (1 - alpha) + alpha * learningChange

Main Algorithm for learning: 

for amount of epochs:

 opponent_moves

  while GameNotOver:
  
    AI_Moves
    
    opponent_moves
    
    UpdateQTable 

Using main.py script:


there is no error checking, so make sure to check arguments!

example running the code, made for python 3
play test against the AI yourself, with trained weights


python3 main.py -p table.json

-------------------------------------------------------------
train the AI against a random agent with alpha and gamma.
alpha is learning rate, gamma is discount rate--> closer to 1
means you value future rewards more, saves the weights


python3 main.py -train table.json 10000 alpha gamma

python3 main.py -train table.json 10000 .6 .8

--------------------------------------------------------------
test the ai over a certain amount of games against a random agent, with loaded weights

python3 main.py -test table.json 100
