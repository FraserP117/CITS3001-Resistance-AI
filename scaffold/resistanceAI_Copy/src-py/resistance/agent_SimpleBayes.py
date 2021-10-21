from agent import Agent
import random
import numpy as np
import itertools

'''
Author: Fraser Paterson (22258324)

CURRENT APPROACH:
Let T = a set of agents selected as the current mission team.
Let S = the mission is sabotaged.
P(S | T) = sum of the probabilities that each player on the team is a spy divided by size of team:
    - P(S | T) = Σ over all a on team of P(spy(a))/len(T)

* Not using the vote outcome at all to update spy probabilities
* init all spy prpbabilities - for all agents - to 0.5
* These probabilities are never getting updated from 0.5


maintain a table of possible worlds were a world is a particular configuration of spies, e.g if players = {a, b, c, d, e}
then there are 2 spies. Each possible world is then {(a, b), (a, c), (a, d), (a, e), (b, c), (b, d), (b, e), (c, d), (c, e), (d, e)}
P(W) = 1/number of worlds initially

If a and c go on a mission and the mission was sabotaged, increment P(a and c are spies | the mission was sabotaged by 1 player) by the bayesian update

assume spies betray with probability 0.8

(a, c) go on mission and mission fails with 1 betrayal -> a or c is a spy


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

        # unconditional spy probabilities for all agents
        self.spy_probability = {}

        #
        self.Possible_worlds_probability = {}

        # unconditional probabilities for all actions:
        self.prob_vote_approve = {}
        self.prob_vote_reject = {}
        self.prob_nominate_team = {}
        self.prob_play_mission = {}
        self.prob_sabotage = {}

        # spy probabilities conditioned on agent's action
        self.prob_spy_given_vote_approve = {}
        self.prob_spy_given_vote_reject = {}
        self.prob_spy_given_nomination_choices = {}
        self.prob_spy_given_play_mission = {}
        self.prob_spy_given_betray_mission = {}

        # liklyhood functions; action propbabilities conditioned on is_spy
        # tune with genetic algorithm?
        self.prob_vote_approve_given_spy = {}
        self.prob_vote_reject_given_spy = {}
        self.prob_nominate_team_given_spy = {}
        self.prob_play_mission_given_spy = {}
        self.prob_betray_mission_given_spy = {}

        # liklyhood functions; action propbabilities conditioned on is NOT spy
        # used to calculate the marginal distribution for action probabilities
        # calculate these with the conditional prob formula?
        # tune with genetic algorithm?
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

    def sum_distribution(self, distribution):
        sum = 0
        for key, val in distribution.items():
            sum += val
        return sum

    def probability_mission_success(self, team):
        '''
        return the probability that the input team will succeed in their assigned mission
        '''
        prob_success = 0
        for player in team:
            prob_success += self.spy_probability[player]

        return (1 - prob_success/len(team))

    # def sort_dict_by_value(self, D):
    #     sorted_values = sorted(D.values()) # Sort the values
    #     sorted_dict = {}
    #
    #     for i in sorted_values:
    #         for k in D.keys():
    #             if D[k] == i:
    #                 sorted_dict[k] = D[k]
    #                 # break
    #
    #     return sorted_dict

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

        # print(f"new_game spy_list: {spy_list}")

        self.number_of_players = number_of_players # the players
        self.player_number = player_number # this agent
        self.spy_list = spy_list # list of spies
        self.all_players = [i for i in range(number_of_players)]

        # for i in range(len(self.all_combinations_of_spies())):
        #     self.Possible_worlds_probability[i] = (0.5, self.all_combinations_of_spies()[i])

        for i in range(self.number_of_players):
            # the suspicion probabilities for all agents; estimated probability that agent is a spy:
            self.spy_probability[i] = 0.5

            # self.number_of_players.append(0)
            self.vote_approve_history[i] = 0
            self.vote_reject_history[i] = 0

            # init action propbabilities conditioned on is_spy
            # these are not PMFs - do not need to sum to 1
            self.prob_vote_approve_given_spy[i] = 0.5
            self.prob_vote_reject_given_spy[i] = 0.5
            self.prob_nominate_team_given_spy[i] = 0.5
            self.prob_play_mission_given_spy[i] = 0.3
            self.prob_betray_mission_given_spy[i] = 0.7

            self.prob_vote_approve_given_not_spy[i] = 0.5
            self.prob_vote_reject_given_not_spy[i] = 0.5
            self.prob_nominate_team_given_not_spy[i] = 0.5
            self.prob_play_mission_given_not_spy[i] = 1.0
            self.prob_betray_mission_given_not_spy[i] = 0.0

            # init spy probabilities conditioned on agent's action
            # perhaps these do not sum to 1
            self.prob_spy_given_vote_approve[i] = 1/self.number_of_players
            self.prob_spy_given_vote_reject[i] = 1/self.number_of_players
            self.prob_spy_given_nomination_choices[i] = 1/self.number_of_players
            self.prob_spy_given_play_mission[i] = 1/self.number_of_players
            self.prob_spy_given_betray_mission[i] = 1/self.number_of_players

            # init action probabilities:
            self.prob_vote_approve[i] = 1/self.number_of_players
            self.prob_vote_reject[i] = 1/self.number_of_players
            self.prob_nominate_team[i] = 1/self.number_of_players
            self.prob_play_mission[i] = 1/self.number_of_players
            self.prob_sabotage[i] = 1/self.number_of_players

        if self.am_spy():
            return spy_list
        else:
            return []

    def propose_mission(self, team_size, fails_required = 1): # nominate a mission team
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned.
        fails_required are the number of fails required for the mission to fail.
        '''

        # the proposed team members
        team = []

        # if proposer is spy
        if self.am_spy():

            # print(f"\n\nspy probs: {self.spy_probability}\n\n")

            # always select self as team member:
            team.append(self.player_number)

            ascending_spy_probability = self.sort_dict_by_value(self.spy_probability)
            # print(f"ascending_spy_probability: {ascending_spy_probability}")
            # print(f"self.spy_list: {self.spy_list}")

            # always add non-spies to team containing a spy - where selector is spy
            while len(team) < team_size:
                # randomly select resistance members for the rest of the team:
                player = random.choice([agent for agent in range(self.number_of_players)])
                # if player not in self.spy_list and player not in team:
                if player != self.player_number and player not in team:
                    team.append(player)

            # print(f"selected SPY team: {team}, team_size: {team_size}, len(team): {len(team)}")
            return team

        # if proposer is resistane
        else:

            '''
            Want to find P(mission failure) for all possible missions and select
            the mission with the smallest probability of failure

            self is always on the mission hence need to check ( self.num_players choose (team_size - 1) )
            combinations to find the one least likely of failure
            '''

            # always select self as team member:
            team.append(self.player_number)

            # print(f"\n\nspy probs: {self.spy_probability}\n\n")

            # sort the spy_probability by probability (ascending order):
            ascending_spy_probability = self.sort_dict_by_value(self.spy_probability)
            # print(f"ascending_spy_probability: {ascending_spy_probability}")
            # print(f"self.spy_list: {self.spy_list}")
            # print(f"self.spy_probability: {self.spy_probability}")
            # # add players that have lowest prob of being a spy to the team:
            # for player, probability in ascending_spy_probability.items():
            #
            #     if player == self.player_number:
            #         pass
            #
            #     # append this player to the team that has the
            #     team.append(player)
            #
            #     # if len(team) < team_size:
            #     if len(team) == team_size:
            #         break
            #
            # print(f"selected resistance team: {team}, team_size: {team_size}, len(team): {len(team)}\n\n")
            # return team

            # probs = list(ascending_spy_probability.items())
            i = 0
            while len(team) < team_size:

                # player = probs[i][0]
                player = ascending_spy_probability[i][0]

                if player == self.player_number or player in team:
                    # player = probs[i + 1][0]
                    player = ascending_spy_probability[i + 1][0]

                # append this player to the team that has the
                team.append(player)

            # print(f"selected RESISTANCE team: {team}, team_size: {team_size}, len(team): {len(team)}")
            return team

        # return team

    def vote(self, mission, proposer): # cast vote regarding team print
        '''
        mission is a list of agents to be sent on a mission. must find prob of success for mission
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''

        # always vote for missions where this agent is the leader
        if self.player_number == proposer:
            return True

        # if spy
        if self.am_spy():
            # for all players on currrent mission:
            for player in mission:
                if player in self.spy_list:
                    # vote for this team if it contains any spy
                    # self.vote_approve_history[self.player_number] += 1
                    print(f"SPY votes: against mission")
                    return True

                else:
                    # vote against team if no spies on team
                    # self.vote_reject_history[self.player_number] += 1
                    print(f"SPY votes: for mission")
                    return False

        # if resistance
        else:
            # # if any one of the proposed team is the most likely spy then vote against the team
            # number_spies = self.spy_count[self.number_of_players]
            # ascending_spy_probabilities = sorted(self.spy_probability.items(), key = lambda x: x[1], reverse = True)
            # most_likely_spies_tuple = ascending_spy_probabilities[:number_spies]
            # most_likely_spies = self.get_likely_spies(most_likely_spies_tuple)

            # if any one of the proposed team is the most likely spy then vote against the team
            number_spies = self.spy_count[self.number_of_players]
            ascending_spy_probabilities = self.sort_dict_by_value(self.spy_probability) # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # descending_spy_probabilities = ascending_spy_probabilities.reverse()
            ascending_spy_probabilities.reverse()
            # print(f"ascending_spy_probabilities: {ascending_spy_probabilities}")
            most_likely_spies_tuple = ascending_spy_probabilities[:number_spies]
            # print(f"most_likely_spies_tuple: {most_likely_spies_tuple}")
            most_likely_spies = self.get_likely_spies(most_likely_spies_tuple)

            # print(f"most_likely_spies: {most_likely_spies}")

            # vote for any mission where none of the players on the mission have the hightest prob of being a spy
            for player in mission:
                if player in most_likely_spies:
                    # self.vote_reject_history[self.player_number] += 1
                    print(f"RESISTANCE votes: against mission")
                    return False
                else:
                    # self.vote_approve_history[self.player_number] += 1
                    print(f"RESISTANCE votes: for mission")
                    return True

    def vote_outcome(self, mission, proposer, votes): # calculate P(spy(a) | V) here
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.

        votes is actually a list of agents that voted for the current mission

        don't update self.spy_probability[agent] here - at least not using the current method
        '''

        '''
        If proposer is likely spy and agent for agent in mission voted for mission, update prob that agent is also a spy
        '''

        for agent in self.all_players:

            if agent in votes:

                print(f"agent {agent} votes: APPROVE")
                if self.spy_probability[proposer] > 0.5:
                    self.spy_probability[agent] = (self.prob_vote_approve_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_approve[agent] # these are not disjoint
                # print(f"spy probs in vote outcome: {self.spy_probability}")

                # increment the number of mission approvals for this agent
                self.vote_approve_history[agent] += 1

                # update the marginal distribution for voting approve:
                self.prob_vote_approve[agent] = self.prob_vote_approve_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_approve_given_not_spy[agent]*(1 - self.spy_probability[agent])

                # # update the marginal distribution for voting approve:
                # self.prob_vote_approve[agent] += self.prob_vote_approve_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_approve_given_not_spy[agent]*(1 - self.spy_probability[agent])


            # if the agent voted to reject the team:
            if agent not in votes:

                print(f"agent {agent} votes: REJECT")

                # increment the number of mission betrayals for this agent
                self.vote_reject_history[agent] += 1

                # update the marginal distribution for voting reject:
                self.prob_vote_reject[agent] = self.prob_vote_reject_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_reject_given_not_spy[agent]*(1 - self.spy_probability[agent])

                # # update the marginal distribution for voting reject:
                # self.prob_vote_reject[agent] += self.prob_vote_reject_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_reject_given_not_spy[agent]*(1 - self.spy_probability[agent])

    def betray(self, mission, proposer): # play success/play sabotage
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise.
        Only spies are permitted to betray the mission.
        '''

        # return self.prob_sabotage
        if self.am_spy():
            # return True
            return random.random() < 0.9 # betray with probability 0.6 if spy
        else:
            return False # play for mission success if resistance

    def mission_outcome(self, mission, proposer, num_fails, mission_success):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        num_fails is the number of people on the mission who betrayed the mission,
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It is not expected or required for this function to return anything.

        need to rank the probability of the given team suceeding
        '''

        # if the mission was sabotaged
        if not mission_success:

            print(" ------------------------------------ MISSION FAILUE ------------------------------------")

            # for all players on this mission, at least one of these are spies
            for agent in mission:

                # # update the suspicion estimate for all players on the team: P(spy(a) | Z) = P(Z | spy(a)) * P(spy(a)) / P(Z)
                # self.spy_probability[agent] = (self.prob_betray_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_sabotage[agent] # these are not disjoint

                # update the suspicion estimate for all players on the team: P(spy(a) | Z) = P(Z | spy(a)) * P(spy(a)) / P(Z)
                self.spy_probability[agent] = (self.prob_betray_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_sabotage[agent] # these are not disjoint
                # print(f"spy probs in mission outcome: {self.spy_probability}")

                # update unconditinal probability of sabotage
                self.prob_sabotage[agent] = self.prob_betray_mission_given_spy[agent]*self.spy_probability[agent] + self.prob_betray_mission_given_not_spy[agent]*(1 - self.spy_probability[agent])

        # if the mission was a success:
        else:

            print(" ------------------------------------ MISSION SUCCESS ------------------------------------")

            # for all players on this mission:
            for agent in mission:

                # update marginal distribution for play mission probability: don't actually use this anywhere
                self.prob_play_mission[agent] = self.prob_play_mission_given_spy[agent]*self.spy_probability[agent] + self.prob_play_mission_given_not_spy[agent]*(1 - self.spy_probability[agent])


        self.current_mission += 1

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''

        # pass
        #
        # if self.am_spy():
        #     print("\n----------------- SPY -----------------")
        #     print(f"missions failed: {missions_failed}")
        #     print(f"rounds complete: {rounds_complete}")
        #     print(f"this agent: {self.player_number}")
        #     print(f"spies: {self.spy_list}")
        #     print("sorted spy probabilities for all agents:")
        #     print(f"{self.sort_dict_by_value(self.spy_probability)}")
        #     print("----------------- SPY -----------------")
        #
        # else:
        #     print("\n----------------- RESISTANCE -----------------")
        #     print(f"missions failed: {missions_failed}")
        #     print(f"rounds complete: {rounds_complete}")
        #     print(f"this agent: {self.player_number}")
        #     print(f"spies: {self.spy_list}")
        #     print("sorted spy probabilities for all agents:")
        #     print(f"{self.sort_dict_by_value(self.spy_probability)}")
        #     print("----------------- RESISTANCE -----------------\n")

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
