from agent import Agent
import random
import numpy as np
import itertools

'''
Author: Fraser Paterson (22258324)
'''
class SimpleBayesAgent(Agent):
    '''An abstract super class for an agent in the game The Resistance.
    new_game and *_outcome methods simply inform agents of events that have occured,
    while propose_mission, vote, and betray require the agent to commit some action.'''

    def __init__(self, name, fails_required, mission_sizes):
        '''
        Initialises the agent, and gives it a name
        You can add configuration parameters etc here,
        but the default code will always assume a 1-parameter constructor, which is the agent's name.
        The agent will persist between games to allow for long-term learning etc.
        '''

        self.spy = []
        self.betray_given_spy = []
        self.betray_given_not_spy = []
        self.not_spy = []

        # a string representing the agent
        self.name = name

        self.mission_outcome_list = []

        # keys are individual agents and values are the probabilities that corresponding agent is a spy
        self.spy_probability = {}

        # unconditional probabilities for all actions:
        self.prob_vote_approve = {}
        self.prob_vote_reject = {}
        self.prob_nominate_team = {}
        self.prob_play_mission = {}
        self.prob_sabotage = {}

        # # spy probabilities conditioned on agent's action
        # self.prob_spy_given_vote_approve = {}
        # self.prob_spy_given_vote_reject = {}
        # self.prob_spy_given_nomination_choices = {}
        # self.prob_spy_given_play_mission = {}
        # self.prob_spy_given_betray_mission = {}

        # liklyhood functions; action propbabilities conditioned on is_spy
        self.prob_vote_approve_given_spy = {}
        self.prob_vote_reject_given_spy = {}
        self.prob_nominate_team_given_spy = {}
        self.prob_play_mission_given_spy = {}
        self.prob_betray_mission_given_spy = {}

        # liklyhood functions; action propbabilities conditioned on is NOT spy
        # used to calculate the marginal distribution for action probabilities
        self.prob_vote_approve_given_not_spy = {}
        self.prob_vote_reject_given_not_spy = {}
        self.prob_nominate_team_given_not_spy = {}
        self.prob_play_mission_given_not_spy = {}
        self.prob_betray_mission_given_not_spy = {}

        self.number_failed_missions_participated = [] # index is player, value is number of times this player has participated in a sabotaged mission
        self.mission_sizes = mission_sizes # dict of mission sized for all valid player counts
        self.fails_required = fails_required # fails required per mission for spy victory, typically 1

        self.number_missions_sabotaged = 0 # the number of missions that have been sabotaged
        self.number_missions_succeed = 0 # number of missions resistance pull off
        self.number_missions = 5 # the total number of missions
        self.current_mission = 0 # the number of elapsed missions

        self.number_times_selected_most_suspicious_agent = 0 # the number of times this agent has selected the most suspicious agent for a mission.
        self.number_rejects = 0 # the number of times this agent has voted against a mission
        self.number_approves = 0 # the number of times this agent has voted for a mission

        self.vote_approve_history = {} # dictionary of ints. key = agent index val = number of missions this agent has approved
        self.vote_reject_history = {} # dictionary of ints. key = agent index val = number of missions  this agent has rejected

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

    def num_spies(self, number_players):
        return self.spy_count[number_players]

    def probability_mission_success(self, team):
        '''
        return the probability that the input team will succeed in their assigned mission
        '''
        prob_success = 0
        for player in team:
            prob_success += self.spy_probability[player]

        return (1 - prob_success/len(team))

    def sort_dict_by_value(self, D):
        return sorted(D.items(), key = lambda x: x[1], reverse = False)

    def dict_max_by_value(self, D):
        sorted = self.sort_dict_by_value(D)
        return (list(sorted)[-1], D[list(sorted)[-1]])

    def get_likely_spies(self, L):
        most_likely_spies = []
        for agent in L:
            most_likely_spies.append(agent[0])
        return most_likely_spies

    def all_combinations_of_spies(self, L):
        combs = []
        for subset in itertools.combinations(L, 2):
            combs.append(subset)

        return combs

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

        self.number_of_players = number_of_players # the players
        self.player_number = player_number # this agent
        self.spy_list = spy_list # list of spies
        self.all_players = [i for i in range(number_of_players)]

        # here we simply initialise all probabilities
        for i in range(self.number_of_players):

            # Let the prior probability that agent x is a spy be 0.5
            self.spy_probability[i] = 0.5

            # history of votes for each agent
            self.vote_approve_history[i] = 0
            self.vote_reject_history[i] = 0

            # init action propbabilities conditioned on is_spy
            # these are not PMFs - do not need to sum to 1
            self.prob_vote_approve_given_spy[i] = 0.7
            self.prob_vote_reject_given_spy[i] = 0.3
            self.prob_nominate_team_given_spy[i] = 0.5
            self.prob_play_mission_given_spy[i] = 0.3
            self.prob_betray_mission_given_spy[i] = 0.7

            self.prob_vote_approve_given_not_spy[i] = 0.5
            self.prob_vote_reject_given_not_spy[i] = 0.5
            self.prob_nominate_team_given_not_spy[i] = 0.5
            self.prob_play_mission_given_not_spy[i] = 1.0
            self.prob_betray_mission_given_not_spy[i] = 0.0

            # # init spy probabilities conditioned on agent's action
            # self.prob_spy_given_vote_approve[i] = 1/self.number_of_players
            # self.prob_spy_given_vote_reject[i] = 1/self.number_of_players
            # self.prob_spy_given_nomination_choices[i] = 1/self.number_of_players
            # self.prob_spy_given_play_mission[i] = 1/self.number_of_players
            # self.prob_spy_given_betray_mission[i] = 1/self.number_of_players

            # # init action probabilities:
            # self.prob_vote_approve[i] = 1/self.number_of_players
            # self.prob_vote_reject[i] = 1/self.number_of_players
            # self.prob_nominate_team[i] = 1/self.number_of_players
            # self.prob_play_mission[i] = 1/self.number_of_players
            # self.prob_sabotage[i] = 1/self.number_of_players

            # init action probabilities:
            self.prob_vote_approve[i] = 0.5
            self.prob_vote_reject[i] = 0.5
            self.prob_nominate_team[i] = 0.5
            self.prob_play_mission[i] = 0.5
            self.prob_sabotage[i] = 0.5

        if self.am_spy():
            return spy_list
        else:
            return []

    def propose_mission(self, team_size, fails_required = 1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned.
        fails_required are the number of fails required for the mission to fail.
        '''

        # the proposed team members
        team = []

        # if proposer is spy
        if self.am_spy():

            # always select yourself as team member:
            team.append(self.player_number)

            # sort the dictionary of spy probabilities; return list of tuples from least likely to most likely spies
            ascending_spy_probability = self.sort_dict_by_value(self.spy_probability)

            # merely select a random selection of players to a team if you are a spy
            # Ensures a modicum of confusion among Resistance members.
            while len(team) < team_size:
                # randomly select from all players for the rest of the team:
                player = random.choice([agent for agent in range(self.number_of_players)])
                # if player not in self.spy_list and player not in team:
                if player != self.player_number and player not in team:
                    team.append(player)

            # select the above team
            return team

        # if proposer is resistane
        else:

            # always select yourself as team member:
            team.append(self.player_number)

            # sort the spy_probability by probability (ascending order):
            ascending_spy_probability = self.sort_dict_by_value(self.spy_probability)

            i = 0
            while len(team) < team_size:

                # player = probs[i][0]
                player = ascending_spy_probability[i][0]

                # skip yourself and players already on the team
                if player == self.player_number or player in team:
                    # player = probs[i + 1][0]
                    player = ascending_spy_probability[i + 1][0]

                # append this player to the team that has the
                team.append(player)

            # return the selected team
            return team

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. must find prob of success for mission
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.

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

        '''

        # always vote for missions where this agent is the leader
        if self.player_number == proposer:
            return True

        # if spy
        if self.am_spy():
            # for all players on currrent mission:
            for player in mission:
                if player in self.spy_list:
                    # vote for this team if it contains at least one spy
                    return True

                else:
                    # vote against team if no spies on team
                    return False

        # if resistance
        else:
            # if any one player in the proposed team is among the most likely spies then vote against the team
            number_spies = self.spy_count[self.number_of_players]
            ascending_spy_probabilities = self.sort_dict_by_value(self.spy_probability)
            ascending_spy_probabilities.reverse() # sorted by most likely spy forst and least likely last
            most_likely_spies_tuple = ascending_spy_probabilities[:number_spies]
            # most_likely_spies_tuple = ascending_spy_probabilities[:self.mission_sizes[self.number_of_players][self.current_mission]]
            print(f"\n\nself.current_mission: {self.current_mission}")
            print(f"self.number_of_players: {self.number_of_players}")
            print(f"self.mission_sizes[self.number_of_players][self.current_mission]: {self.mission_sizes[self.number_of_players][self.current_mission]}\n\n")
            # print(f"most_likely_spies_tuple: {most_likely_spies_tuple}")
            most_likely_spies = self.get_likely_spies(most_likely_spies_tuple)

            # vote for any mission where none of the players on the mission are among the most likely spies
            # othersies vote against mission
            for player in mission:
                if player in most_likely_spies:
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

        votes is actually a list of agents that voted for the current mission
        '''

        for agent in self.all_players:

            # if this player voted for the mission
            if agent in votes:

                # if the proposer for the mission is more likely to be a spy than not
                # then anyone who voted for this mission is probably a spy
                # update probability that agents who voted for mission are spies
                if self.spy_probability[proposer] > 0.5:
                    self.spy_probability[agent] = (self.prob_vote_approve_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_approve[agent]

                # increment the number of mission approvals for this agent
                self.vote_approve_history[agent] += 1

                # update the marginal distribution for voting approve fpr this agent:
                self.prob_vote_approve[agent] = self.prob_vote_approve_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_approve_given_not_spy[agent]*(1 - self.spy_probability[agent])

            # if the agent voted to reject the team:
            if agent not in votes:

                # increment the number of mission betrayals for this agent
                self.vote_reject_history[agent] += 1

                # update the marginal distribution for voting reject:
                self.prob_vote_reject[agent] = self.prob_vote_reject_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_reject_given_not_spy[agent]*(1 - self.spy_probability[agent])

    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise.
        Only spies are permitted to betray the mission.
        '''

        # spies betray with probability 0.9
        if self.am_spy():
            # return True
            return random.random() < 0.9
        else:
            return False

    def mission_outcome(self, mission, proposer, num_fails, mission_success):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        num_fails is the number of people on the mission who betrayed the mission,
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It is not expected or required for this function to return anything.
        '''

        # if the mission was sabotaged
        if not mission_success:

            # print(" ------------------------------------ MISSION FAILUE ------------------------------------")

            # for all players on this mission, num_fails of these are spies
            for agent in mission:

                # update the probability that a player on the failed mission is a spy
                self.spy_probability[agent] = (self.prob_betray_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_sabotage[agent] # these are not disjoint

                # update unconditinal probability of sabotage for each agent on the failed mission
                self.prob_sabotage[agent] = self.prob_betray_mission_given_spy[agent]*self.spy_probability[agent] + self.prob_betray_mission_given_not_spy[agent]*(1 - self.spy_probability[agent])

        # if the mission was a success:
        else:

            # print(" ------------------------------------ MISSION SUCCESS ------------------------------------")

            # for all players on this mission:
            for agent in mission:

                # update marginal distribution for play mission probability
                # we don't actually use this anywhere - we thought it might come in handy
                self.prob_play_mission[agent] = self.prob_play_mission_given_spy[agent]*self.spy_probability[agent] + self.prob_play_mission_given_not_spy[agent]*(1 - self.spy_probability[agent])

        # increment the number of elapsed missions
        # self.current_mission += 1

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''

        self.current_mission = rounds_complete - 1
        # print(f"rounds_complete: {rounds_complete}")

        # # pass
        if self.am_spy():
            print("\n----------------- SPY -----------------")
            print(f"missions failed: {missions_failed}")
            print(f"rounds complete: {rounds_complete}")
            print(f"rounds_complete: {rounds_complete}")
            print(f"this agent: {self.player_number}")
            print(f"spies: {self.spy_list}")
            print("sorted spy probabilities for all agents:")
            print(f"{self.sort_dict_by_value(self.spy_probability)}")
            print("----------------- SPY -----------------")

        else:
            print("\n----------------- RESISTANCE -----------------")
            print(f"missions failed: {missions_failed}")
            print(f"rounds complete: {rounds_complete}")
            print(f"rounds_complete: {rounds_complete}")
            print(f"this agent: {self.player_number}")
            print(f"spies: {self.spy_list}")
            print("sorted spy probabilities for all agents:")
            print(f"{self.sort_dict_by_value(self.spy_probability)}")
            print("----------------- RESISTANCE -----------------\n")

        # print(f"Number of completed rounds:   {rounds_complete}")
        # print(f"Number of sabotaged missions: {missions_failed}")

    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        pass

        # if spies_win == True:
        #     print("\n\nThe spies win!")
        #     print(f"they were: {spies}\n\n")
        # else:
        #     print("\n\nthe resistance wins!")
        #     print(f"The spies were: {spies}\n\n")
