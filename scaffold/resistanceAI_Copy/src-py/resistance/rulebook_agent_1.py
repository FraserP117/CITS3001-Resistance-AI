from agent import Agent
import random


class RuleBookAgent(Agent):
    '''A sample implementation of a random agent in the game The Resistance'''

    def __init__(self, name='Rando'):
        '''
        Initialises the agent.
        Nothing to do here.
        '''
        self.name = name

    def new_game(self, number_of_players, player_number, spy_list):
        '''
        initialises the game, informing the agent of the
        number_of_players, the player_number (an id number for the agent in the game),
        and a list of agent indexes which are the spies, if the agent is a spy, or empty otherwise
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list
        self.fail_frequency = [0] * number_of_players

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def fail_frequency_order(self):
        lis_order = []
        used = []
        while len(lis_order) != len(self.fail_frequency):
            biggest = -1
            for i in range(len(self.fail_frequency)):
                if self.fail_frequency[i] > biggest and (i not in used):
                    biggest = i
                    used.append(i)
                    lis_order.append(i)
        return lis_order

    def propose_mission(self, team_size, betrayals_required=1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned.
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        team = []

        if self.is_spy():
            team.append(self.player_number)
            while len(team) < team_size:
                if random.random() >= 0.9:
                    agent = random.choice(self.spy_list)
                    if agent not in team:
                        team.append(agent)
                else:
                    agent = random.choice(range(self.number_of_players))
                    if agent not in team and agent not in self.spy_list:
                        team.append(agent)
        else:
            team.append(self.player_number)
            least_likely = self.fail_frequency_order()
            pos = 0
            while len(team) < team_size:
                team.append(least_likely[pos])
                pos += 1

        print("\n----------------- MISSION -----------------")
        print(f"members: {team}\n\n")
        return team

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        if self.is_spy():
            if any(x in mission for x in self.spy_list):
                if random.random() >= 0.9:
                    return True
                else:
                    return False
            else:
                if random.random() >= 0.25:
                    return True
                else:
                    return False
        else:
            prob_spy = self.fail_frequency_order()[:self.spy_count[self.number_of_players]]
            if any(x in mission for x in prob_spy):
                return False
            else:
                return True

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''

    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise.
        By default, spies will betray 30% of the time.
        '''
        if self.is_spy():
            return random.random() < 0.8

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals is the number of people on the mission who betrayed the mission,
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        '''
        if not mission_success:
            for agent in mission:
                self.fail_frequency[agent] = self.fail_frequency[agent] + 1

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        if self.is_spy():
            print("\n----------------- SPY -----------------")
            print(f"missions failed: {missions_failed}")
            print(f"rounds complete: {rounds_complete}")
            print(f"this agent: {self.player_number}")
            print(f"spies: {self.spy_list}")
            print("----------------- SPY -----------------\n")
        else:
            print("\n----------------- RESISTANCE -----------------")
            print(f"missions failed: {missions_failed}")
            print(f"rounds complete: {rounds_complete}")
            print(f"this agent: {self.player_number}")
            print(f"fail_frequency: {self.fail_frequency}")
            print("----------------- RESISTANCE -----------------\n")

    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        if spies_win:
            print("----------------- SPIES WIN -----------------\n")
        else:
            print("----------------- RESISTANCE WIN -----------------\n")
