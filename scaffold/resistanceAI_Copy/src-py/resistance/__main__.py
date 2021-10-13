from random_agent import RandomAgent
from agent_SimpleBayes import SimpleBayesAgent
from game import Game

# ALL BELOW ADDED --------------------------------------------------------------------------------------------------

#game parameters for agents to access
#python is such that these variables could be mutated, so tournament play
#will be conducted via web sockets.
#e.g. self.mission_size[8][3] is the number to be sent on the 3rd mission in a game of 8

# for key : value in mission_sizes, key = number of players in the game,
# val[i] = n where i is the mission number and n is number to be sent on ith mission
mission_sizes = {
        5:[2,3,2,3,3], \
        6:[3,3,3,3,3], \
        7:[2,3,3,4,5], \
        8:[3,4,4,5,5], \
        9:[3,4,4,5,5], \
        10:[3,4,4,5,5]
}

#number of spies for different game sizes
spy_count = {5:2, 6:2, 7:3, 8:3, 9:3, 10:4}

#e.g. self.betrayals_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail # OG
#e.g. self.fails_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail

# for key : value in fails_required, key = number of players in the game,
# val[i] = n where i is the mission number and n is number of betreyals required for mission of size i to fail
fails_required = {
        5:[1,1,1,1,1], \
        6:[1,1,1,1,1], \
        7:[1,1,1,2,1], \
        8:[1,1,1,2,1], \
        9:[1,1,1,2,1], \
        10:[1,1,1,2,1]
}

# ALL ABOVE ADDED --------------------------------------------------------------------------------------------------

# agents = [
#     RandomAgent(name='r1'),
#     RandomAgent(name='r2'),
#     RandomAgent(name='r3'),
#     RandomAgent(name='r4'),
#     RandomAgent(name='r5'),
#     RandomAgent(name='r6'),
#     RandomAgent(name='r7')
# ]

agents = [
    SimpleBayesAgent(name = 'r1', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r2', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r3', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r4', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r5', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r6', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r7', fails_required = fails_required, mission_sizes = mission_sizes)
]

game = Game(agents)
game.play()
print(game)
