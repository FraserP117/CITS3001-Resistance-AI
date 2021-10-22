from random_agent import RandomAgent
from agent_SimpleBayes import SimpleBayesAgent
from game import Game
from rulebook_agent_1 import RuleBookAgent

import matplotlib.pyplot as plt

#game parameters for agents to access
#python is such that these variables could be mutated, so tournament play
#will be conducted via web sockets.
#e.g. self.mission_size[8][3] is the number to be sent on the 3rd mission in a game of 8
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
#e.g. self.betrayals_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail
fails_required = {
        5:[1,1,1,1,1], \
        6:[1,1,1,1,1], \
        7:[1,1,1,2,1], \
        8:[1,1,1,2,1], \
        9:[1,1,1,2,1], \
        10:[1,1,1,2,1]
        }

# agents = [
#     RandomAgent(name='r1'),
#     RandomAgent(name='r2'),
#     RandomAgent(name='r3'),
#     RandomAgent(name='r4'),
#     RandomAgent(name='r5'),
#     RandomAgent(name='r6'),
#     RandomAgent(name='r7'),
#     RandomAgent(name='r8'),
#     RandomAgent(name='r9'),
#     RandomAgent(name='r10')
# ]

# agents = [
#     SimpleBayesAgent(name = 'r1', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r2', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r3', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r4', fails_required = fails_required, mission_sizes = mission_sizes),
#     RandomAgent(name='r5'),
#     RandomAgent(name='r6'),
#     RandomAgent(name='r7')
# ]

# -------------------------------------------------------------------------------------


# agents = [
#     RandomAgent(name = 'r1'),
#     RandomAgent(name = 'r2'),
#     RandomAgent(name = 'r3'),
#     RandomAgent(name = 'r4'),
#     RandomAgent(name = 'r5'),
#     RandomAgent(name = 'r6'),
#     SimpleBayesAgent(name='r7', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name='r8', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name='r9', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name='r10', fails_required = fails_required, mission_sizes = mission_sizes)
# ]

# OG
# game = Game(agents)
# game.play()
# print(game)

# # 1 simplebayes spy
# agents = [
#     SimpleBayesAgent(name = 'r1', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r2', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r3', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r4', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r5', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r6', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r7', fails_required = fails_required, mission_sizes = mission_sizes),
#     RandomAgent(name='r8'),
#     RandomAgent(name='r9'),
#     RandomAgent(name='r10')
# ]

# # 1 simplebayes spy
# agents = [
#     RuleBookAgent(name = 'r1', fails_required = fails_required, mission_sizes = mission_sizes),
#     RuleBookAgent(name = 'r2', fails_required = fails_required, mission_sizes = mission_sizes),
#     RuleBookAgent(name = 'r3', fails_required = fails_required, mission_sizes = mission_sizes),
#     RuleBookAgent(name = 'r4', fails_required = fails_required, mission_sizes = mission_sizes),
#     RuleBookAgent(name = 'r5', fails_required = fails_required, mission_sizes = mission_sizes),
#     RuleBookAgent(name = 'r6', fails_required = fails_required, mission_sizes = mission_sizes),
#     RuleBookAgent(name = 'r7', fails_required = fails_required, mission_sizes = mission_sizes),
#     RandomAgent(name='r8'),
#     RandomAgent(name='r9'),
#     RandomAgent(name='r10')
# ]

# # 2 simplebayes spies
# agents = [
#     SimpleBayesAgent(name = 'r1', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r2', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r3', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r4', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r5', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r6', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r7', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r8', fails_required = fails_required, mission_sizes = mission_sizes),
#     RandomAgent(name='r9'),
#     RandomAgent(name='r10')
# ]

# # no simple bayes spies
# agents = [
#     SimpleBayesAgent(name = 'r1', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r2', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r3', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r4', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r5', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r6', fails_required = fails_required, mission_sizes = mission_sizes),
#     RandomAgent(name='r7'),
#     RandomAgent(name='r8'),
#     RandomAgent(name='r9'),
#     RandomAgent(name='r10')
# ]

agents = [
    SimpleBayesAgent(name = 'r1', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r2', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r3', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r4', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r5', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r6', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r7', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r8', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r9', fails_required = fails_required, mission_sizes = mission_sizes),
    SimpleBayesAgent(name = 'r10', fails_required = fails_required, mission_sizes = mission_sizes),
]

# # no simple bayes spies
# agents = [
#     SimpleBayesAgent(name = 'r1', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r2', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r3', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r4', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r5', fails_required = fails_required, mission_sizes = mission_sizes),
#     SimpleBayesAgent(name = 'r6', fails_required = fails_required, mission_sizes = mission_sizes),
#     RuleBookAgent(name='r7'),
#     RuleBookAgent(name='r8'),
#     RuleBookAgent(name='r9'),
#     RuleBookAgent(name='r10')
# ]

# # RuleBookAgents
# agents = [
#     RuleBookAgent(name = 'r1'),
#     RuleBookAgent(name = 'r2'),
#     RuleBookAgent(name = 'r3'),
#     RuleBookAgent(name = 'r4'),
#     RuleBookAgent(name = 'r5'),
#     RuleBookAgent(name = 'r6'),
#     RuleBookAgent(name = 'r7'),
#     RuleBookAgent(name = 'r8'),
#     RuleBookAgent(name = 'r9'),
#     RuleBookAgent(name = 'r10')
# ]

missions_lost = []
games_played = []
total_missions_lost = 0
loss_rates = []

games_lost = 0
games_won = 0

# play 100 games
for i in range(1000):
    game = Game(agents)
    # print(f"game spies: {game.spies}")
    game.play()
    missions_lost.append(game.missions_lost)
    total_missions_lost += game.missions_lost
    loss_rate = total_missions_lost/5
    loss_rates.append(loss_rate)
    games_played.append(i)

loss_rate = total_missions_lost/1000

print(f"average games lost: {loss_rate}")
plt.plot(games_played, missions_lost, linewidth = 0.5)
plt.title(f"SimpleBayesAgent: average rounds lost by resistane: {loss_rate}")
plt.xlabel("games played")
plt.ylabel("missions lost by resistance")
plt.show()
