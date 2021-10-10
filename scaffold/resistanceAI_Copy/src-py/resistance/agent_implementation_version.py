from agent import Agent
import random

# NOTES:
# maintain a probability estmate for the probability that each agent is a spy
# adjust with basean update each game

class SimpleBayesAgent(Agent):
    '''An abstract super class for an agent in the game The Resistance.
    new_game and *_outcome methods simply inform agents of events that have occured,
    while propose_mission, vote, and betray require the agent to commit some action.'''

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

    def __init__(self, name, fails_required, mission_sizes):
        '''
        Initialises the agent, and gives it a name
        You can add configuration parameters etc here,
        but the default code will always assume a 1-parameter constructor, which is the agent's name.
        The agent will persist between games to allow for long-term learning etc.
        '''
        self.name = name
        self.spy_suspicions = [] # index is the player for which the value is the suspicion estimate (probability)
        self.number_failed_missions_participated = [] # index is player value is number of times this player has been part of a sabotaged mission
        self.mission_sizes = mission_sizes
        self.fails_required = fails_required

        self.number_missions_sabotaged = 0
        self.number_missions_completed = 0
        # dictionary of ints. key = agent index val = number of missions this agent has approved

        self.vote_history = {}
        for i in range(number_of_players):
            self.number_of_players.append(0)
            self.vote_history[i] = 0

    def __str__(self):
        '''
        Returns a string represnetation of the agent
        '''
        return 'Agent ' + self.name

    def __repr__(self):
        '''
        returns a representation fthe state of the agent.
        default implementation is just the name, but this may be overridden for debugging
        '''
        return self.__str__()

    def am_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def new_game(self, number_of_players, player_number, spy_list):
        '''
        initialises the game, informing the agent of the number_of_players,
        the player_number (an id number for the agent in the game),
        and a list of agent indexes, which is the set of spies if this agent is a spy,
        or an empty list if this agent is not a spy.
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list

        if self.am_spy():
            return spy_list
        else:
            return []

        # # if not a spy
        # if not self.am_spy():
        #
        #     # init the prob that all players are spies to 1/(number_of_players-1)
        #     for spy_probability in self.spy_suspicions:
        #         # spy_probability = 1/(number_of_players - 1)
        #         spy_probability = 1/(number_of_players)

        # init the prob that all players are spies to 1/(number_of_players-1)
        for spy_probability in self.spy_suspicions:
            # spy_probability = 1/(number_of_players - 1)
            spy_probability = 1/(number_of_players)

    def propose_mission(self, team_size, fails_required = 1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned.
        fails_required are the number of fails required for the mission to fail.
        '''

        team = []
        while len(team)<team_size:
            agent = random.randrange(team_size)
            if agent not in team:
                team.append(agent)
        return team

        # # if not a spy
        # if not self.am_spy():
        #     # SIMPLE: always propose a mission
        #     pass
        # else:
        #     # SIMPLE: always propose mission
        #     pass

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''

        '''
        If the probability of a spy on proposed mission > average probability that spy on mission, decline, else accept
        '''
        if not self.am_spy():
            # SIMPLE: always vote for any mission
            return True
        else:
            # SIMPLE: vote against mission 1/3 of the time
            return random.random() < 0.33

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''

        '''
        why have this?
        do we test for a certain pattern of viting? or for a frequency of betreyals? are these the same?
        do baysean updates here?
        mission = [a, b, ..., n]
        proposer = i
        votes = {0: T/F, 1: T/F, ..., n: T/F}

        if proposer proposes a mission with a known spy then proposer is almost certainly a spy

        we update each agent's history of votes for/against missions
        we somehow use this history to make the baysian updates - here?
            - perhaps not here, we have the reccord of votes now

        do we wnat to keep track of the number of missions proposed by each agent?

        '''
        # update each agent's history of votes for/against missions
        for agent, vote in votes.items():
            # if the agent voted for the mission
            if vote == True:
                # increment the number of mission approvals for this agent
                self.vote_history[agent] += 1

    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise.
        Only spies are permitted to betray the mission.
        '''
        if self.am_spy():
            # betrey with probability 0.5
            return random.random() < 0.5 # SIMPLE
        else:
            return 1

    def mission_outcome(self, mission, proposer, num_fails, mission_success):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        num_fails is the number of people on the mission who betrayed the mission,
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        '''
        # update self.spy_suspicions for all those who were on a failed mission
        # incr the relevant indices in self.spy_suspicions by incr
        pass

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        print(f"Number of completed rounds:   {rounds_complete}")
        print(f"Number of sabotaged missions: {missions_failed}")

    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        if spies_win:
            print("\n\nThe spies win!")
            print(f"they were: {spies}\n\n")
        else:
            print("\n\nthe resistance wins!")
            print(f"The spies were: {spies}\n\n")

if __name__ == '__main__':
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
    name = "DEEP MEMER"

    agent = SimpleBayesAgent(name, fails_required, mission_sizes)
    agent.new_game(5, 0, spies):
    team = agent.propose_mission(3)
    print(f"\n\nteam: {team}\n\n")
