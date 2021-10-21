from agent import Agent
import random
import numpy as np

'''
Author: Fraser Paterson (22258324)
'''

current_mission = 0

class RuleBookAgent(Agent):
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

        self.current_mission = 0 # the number of elapsed missions

        # a string representing the agent
        self.name = name

        self.mission_outcome_list = []

        # unconditional spy probabilities for all agents
        self.frequency_been_on_failed_missions = {}

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
            prob_success += self.frequency_been_on_failed_missions[player]

        return (1 - prob_success/len(team))

    def sort_dict_by_value(self, D):
        sorted_values = sorted(D.values()) # Sort the values
        sorted_dict = {}

        for i in sorted_values:
            for k in D.keys():
                if D[k] == i:
                    sorted_dict[k] = D[k]
                    break

        return sorted_dict

    def dict_max_by_value(self, D):
        sorted = self.sort_dict_by_value(D)
        return (list(sorted)[-1], D[list(sorted)[-1]])

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

        for i in range(self.number_of_players):
            # the suspicion probabilities for all agents; estimated probability that agent is a spy:
            self.frequency_been_on_failed_missions[i] = 0

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

        # # the number of betrayals required for the current mission to fail
        # fails_required = self.fails_required[self.number_of_players][self.current_mission]

        # the proposed team members
        team = []

        # if proposer is spy
        if self.am_spy():

            # print(f"\n\nspy probs: {self.frequency_been_on_failed_missions}\n\n")

            # always select self as team member:
            team.append(self.player_number)

            # always add non-spies to team containing a spy - where selector is spy
            while len(team) < team_size:
                player = random.choice([spy for spy in range(self.spy_list)])
                # # randomly select resistance members for the rest of the team:
                # player = random.choice([agent for agent in range(self.number_of_players)])
                # if player not in self.spy_list and player not in team:
                #     team.append(player)

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

            # print(f"\n\nspy probs: {self.frequency_been_on_failed_missions}\n\n")

            # sort the frequency_been_on_failed_missions by probability (ascending order):
            ascending_frequency_been_on_failed_missions = self.sort_dict_by_value(self.frequency_been_on_failed_missions)

            # add players that have lowest prob of being a spy to the team:
            for player, frequency in ascending_frequency_been_on_failed_missions.items():

                # append this player to the team that has the
                team.append(player)

                # if len(team) < team_size:
                if len(team) == team_size:
                    break

        return team

    def vote(self, mission, proposer): # cast vote regarding team print
        '''
        mission is a list of agents to be sent on a mission. must find prob of success for mission
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''

        # rank mission success:
        prob_mission_success = 0
        for agent in mission:
            prob_mission_success += self.frequency_been_on_failed_missions[agent]

        # prob_mission_success = prob_mission_success / self.team_size

        # always vote for missions where this agent is the leader
        # if self.name == proposer:
        if self.name == self.player_number:
            return True

        # if spy
        if self.am_spy():

            return True

            # # if any one of the proposed team is the most likely spy then vote against the team
            # number_spies = self.spy_count[self.number_of_players]
            # ascending_spy_frequencies = sorted(self.frequency_been_on_failed_missions.items(), key = lambda x: x[1], reverse = True)
            # # most_likely_spies = ascending_spy_frequencies[:number_spies]
            # most_likely_spies = ascending_spy_frequencies[:number_spies + 1]
            # if agent in most_likely_spies:
            #     self.vote_approve_history[self.player_number] += 1
            #     return True # add probability in later
            # else:
            #     self.vote_reject_history[self.player_number] += 1
            #     return False # add probability in later

        # if resistance
        else:

            # vote for any mission where none of the players on the mission have the hightest prob of being a spy
            for player in mission:
                # print(f"\n\nplayer: {player}, type: {type(player)}\n\n")

                # if any one of the proposed team is the most likely spy then vote against the team
                number_spies = self.spy_count[self.number_of_players]
                ascending_spy_frequencies = sorted(self.frequency_been_on_failed_missions.items(), key = lambda x: x[1], reverse = True)
                most_likely_spies = ascending_spy_frequencies[:number_spies]
                if player in most_likely_spies:
                    return False
                else:
                    return True

    def vote_outcome(self, mission, proposer, votes): # calculate P(spy(a) | V) here
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.

        votes is actually a list of agents that voted for the current mission

        don't update self.frequency_been_on_failed_missions[agent] here - at least not using the current method
        '''

        for agent in self.all_players:
            pass

            # if agent in votes:
            #
            #     # increment the number of mission approvals for this agent
            #     self.vote_approve_history[agent] += 1
            #
            #     # update the marginal distribution for voting approve:
            #     self.prob_vote_approve[agent] = self.prob_vote_approve_given_spy[agent]*self.frequency_been_on_failed_missions[agent] + self.prob_vote_approve_given_not_spy[agent]*(1 - self.frequency_been_on_failed_missions[agent])
            #
            #
            # # if the agent voted to reject the team:
            # if agent not in votes:
            #
            #     # increment the number of mission betrayals for this agent
            #     self.vote_reject_history[agent] += 1
            #
            #     # update the marginal distribution for voting reject:
            #     self.prob_vote_reject[agent] = self.prob_vote_reject_given_spy[agent]*self.frequency_been_on_failed_missions[agent] + self.prob_vote_reject_given_not_spy[agent]*(1 - self.frequency_been_on_failed_missions[agent])

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
            return True
            # return random.random() < 0.7 # betray with probability 0.7 if spy
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

            # print("MISSION FAILUE")

            # for all players on this mission, at least one of these are spies
            for agent in mission:

                # increment the frequency wth which the agents on this mission have been on failed missions
                self.frequency_been_on_failed_missions[agent] += 1

        # if the mission was a success:
        else:

            pass

        self.current_mission += 1

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''

        if self.am_spy():
            print("\n\n----------------- SPY -----------------")
            print(f"missions failed: {missions_failed}")
            print(f"rounds complete: {rounds_complete}")
            print(f"this agent: {self.player_number}")
            print(f"spies: {self.spy_list}")
            print("failed mission frequencies for all agents:")
            # print(f"{ sorted(self.frequency_been_on_failed_missions.items(), key = lambda x: x[1], reverse = True)}")
            print(f"{self.frequency_been_on_failed_missions}")
            # print(f"sum: {self.sum_distribution(self.sort_dict_by_value(self.frequency_been_on_failed_missions))}")
            print("----------------- SPY -----------------\n")
        else:
            print("\n----------------- RESISTANCE -----------------")
            print(f"missions failed: {missions_failed}")
            print(f"rounds complete: {rounds_complete}")
            print(f"this agent: {self.player_number}")
            print(f"spies: {self.spy_list}")
            print("failed mission frequencies for all agents:")
            # print(f"{ sorted(self.frequency_been_on_failed_missions.items(), key = lambda x: x[1], reverse = True)}")
            print(f"{self.frequency_been_on_failed_missions}")
            # print(f"sum: {self.sum_distribution(self.sort_dict_by_value(self.frequency_been_on_failed_missions))}")
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
