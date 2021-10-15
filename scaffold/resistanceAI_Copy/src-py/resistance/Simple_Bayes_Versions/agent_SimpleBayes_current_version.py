from agent import Agent
import random
import numpy as np

'''
Author: Fraser Paterson (22258324)

NOTES:

# each time the agent performs an action, update P(spy(agent) | action(agent)) via Bayes' Rule:
P(spy(agent) | action(agent)) = ( P(action(agent) | spy(agent)) * P(spy(agent)) ) / P(action(agent))
    - liklyhood = P(action(agent) | spy(agent))
    - prior = P(spy(agent))
    - marginal distribution for the agent's action = P(action(agent))

# update the marginal distribution for the action taken, simultaneously; with the above update:
P(action(agent)) = P(action(agent) | spy(agent))*P(spy(agent)) + P(action(agent) | ~spy(agent))*P(~spy(agent))
'''
'''
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

QUESTIONS:
1. currently the spy probabilities are not in [0, 1] do we have to divide the updated probability by self.number_of_players?
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

        # a string representing the agent
        self.name = name

        # unconditional spy probabilities for all agents
        self.spy_probability = {}

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
        self.number_of_players = number_of_players # the players
        self.player_number = player_number # this agent
        self.spy_list = spy_list # list of spies
        self.all_players = [i for i in range(number_of_players)]

        for i in range(self.number_of_players):
            # the suspicion probabilities for all agents; estimated probability that agent is a spy:
            self.spy_probability[i] = 1/self.number_of_players

            # self.number_of_players.append(0)
            self.vote_approve_history[i] = 0
            self.vote_reject_history[i] = 0

            # init action propbabilities conditioned on is_spy
            # these are not PMFs - do not need to sum to 1
            self.prob_vote_approve_given_spy[i] = 0.5
            self.prob_vote_reject_given_spy[i] = 0.5
            self.prob_nominate_team_given_spy[i] = 0.9
            self.prob_play_mission_given_spy[i] = 0.3
            self.prob_betray_mission_given_spy[i] = 0.7

            self.prob_vote_approve_given_not_spy[i] = 0.5
            self.prob_vote_reject_given_not_spy[i] = 0.5
            self.prob_nominate_team_given_not_spy[i] = 0.5
            self.prob_play_mission_given_not_spy[i] = 1.0
            self.prob_betray_mission_given_not_spy[i] = 0.3

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

            # # init the prob that any one player is a spy to the uniform distribution:
            # for agent, spy_probability in self.spy_probability.items():
            #
            #     # spies still need to model resistane decison making; for optimal spy-play
            #     self.spy_probability[agent] = 1 / self.number_of_players

            return spy_list

        else:

            # # init the prob that any one player is a spy to the uniform distribution:
            # for agent, spy_probability in self.spy_probability.items():
            #
            #     self.spy_probability[agent] = 1 / self.number_of_players # the prior probability for P(spy(agent))

            return []

    def print_all_probs(self):
        # the suspicion probabilities for all agents; estimated probability that agent is a spy:
        print("\n\n\n\n")
        print(f"self.spy_probability: {self.spy_probability}\n")

        # self.number_of_players.append(0)
        print(f"self.vote_approve_history: {self.vote_approve_history}\n")
        print(f"self.vote_reject_history: {self.vote_reject_history}\n")

        # init action propbabilities conditioned on is_spy
        # these are not PMFs - do not need to sum to 1
        print(f"self.prob_vote_approve_given_spy: {self.prob_vote_approve_given_spy}\n")
        print(f"self.prob_vote_reject_given_spy: {self.prob_vote_reject_given_spy}\n")
        print(f"self.prob_nominate_team_given_spy: {self.prob_nominate_team_given_spy}\n")
        print(f"self.prob_play_mission_given_spy: {self.prob_play_mission_given_spy}\n")
        print(f"self.prob_betray_mission_given_spy: {self.prob_betray_mission_given_spy}\n")

        print(f"self.prob_vote_approve_given_not_spy: {self.prob_vote_approve_given_not_spy}\n")
        print(f"self.prob_vote_reject_given_not_spy: {self.prob_vote_reject_given_not_spy}\n")
        print(f"self.prob_nominate_team_given_not_spy: {self.prob_nominate_team_given_not_spy}\n")
        print(f"self.prob_play_mission_given_not_spy: {self.prob_play_mission_given_not_spy}\n")
        print(f"self.prob_betray_mission_given_not_spy: {self.prob_betray_mission_given_not_spy}\n")

        # init spy probabilities conditioned on agent's action
        # perhaps these do not sum to 1
        print(f"self.prob_spy_given_vote_approve: {self.prob_spy_given_vote_approve}\n")
        print(f"self.prob_spy_given_vote_reject: {self.prob_spy_given_vote_reject}\n")
        print(f"self.prob_spy_given_nomination_choices: {self.prob_spy_given_nomination_choices}\n")
        print(f"self.prob_spy_given_play_mission: {self.prob_spy_given_play_mission}\n")
        print(f"self.prob_spy_given_betray_mission: {self.prob_spy_given_betray_mission}\n")

        # init action probabilities:
        print(f"self.prob_vote_approve: {self.prob_vote_approve}\n")
        print(f"self.prob_vote_reject: {self.prob_vote_reject}\n")
        print(f"self.prob_nominate_team: {self.prob_nominate_team}\n")
        print(f"self.prob_play_mission: {self.prob_play_mission}\n")
        print(f"self.prob_sabotage: {self.prob_sabotage}\n")
        print("\n\n\n\n")


    '''
    * always select self as team member
    * if self is spy, randomly select remaining members from resistance
    * If resistance, add remaining members in order of increasing
      probability that these memebers are spies; lowest prob first.
        - maintain dictionary of {player_i: spy_probability_i} and sort this dictionary
    '''
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

            # print(f"\n\nspy probs: {self.spy_probability}\n\n")

            # always select self as team member:
            team.append(self.player_number)

            # always add non-spies to team containing a spy - where selector is spy
            while len(team) < team_size:
                # randomly select resistance members for the rest of the team:
                player = random.choice([agent for agent in range(self.number_of_players)])
                if player not in self.spy_list and player not in team:
                    team.append(player)

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

            print("\n\nspy probabilities for all agents:")
            print(f"{ascending_spy_probability}\n\n")

            # add players that have lowest prob of being a spy to the team:
            for player, probability in ascending_spy_probability.items():

                # append this player to the team that has the
                team.append(player)

                # if len(team) < team_size:
                if len(team) == team_size:
                    break

        return team

    '''
    If the probability of a spy on proposed mission > average probability that spy on mission, decline, else accept?

    * if self is leader always vote yes - we get to chose the mission teammates and get most information thereby
    * if self not leader than decision function of if spy or resistance
    * spy proposer only votes for missions where known spy is on mision
    * resistance proposer only votes for teams where none of the players on the proposed team
      are the most likely to be spies.

    CURRENTLY: only vote for missions wehere the spy knows a spy is on the mission
    '''
    def vote(self, mission, proposer): # cast vote regarding team
        '''
        mission is a list of agents to be sent on a mission. must find prob of success for mission
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''

        # rank mission success:
        prob_mission_success = 0
        for agent in mission:
            prob_mission_success += self.spy_probability[agent]

        # prob_mission_success = prob_mission_success / self.team_size

        # always vote for missions where this agent is the leader
        # if self.name == proposer:
        if self.name == self.player_number:
            return True

        # if resistance member
        if not self.am_spy():

            # vote for any mission where none of the players on the mission have the hightest prob of being a spy
            for player in mission:
                # print(f"\n\nplayer: {player}, type: {type(player)}\n\n")

                # if any one of the proposed team is the most likely spy then vote against the team
                if player == self.dict_max_by_value(self.spy_probability)[0]:
                    self.vote_reject_history[self.player_number] += 1
                    return False

            # if none of the proposed team members are the most likely spy then vote for the team
            self.vote_approve_history[self.player_number] += 1
            return True

        # if spy
        else:
            # for all players on currrent mission:
            for player in mission:
                # print(f"\n\nplayer: {player}, type: {type(player)}\n\n")
                # if one of these players is a spy
                # if player.am_spy() == True:
                if player in self.spy_list:
                    # vote for this team
                    self.vote_approve_history[self.player_number] += 1
                    return True

            # vote against team if no spies on team
            self.vote_reject_history[self.player_number] += 1
            return False

    '''
    mission = [a, b, ..., n]
    proposer = i
    votes = {0: T/F, 1: T/F, ..., n: T/F}

    if proposer proposed a mission with a known spy then proposer is almost certainly a spy.

    we update each agent's history of votes for/against missions using P(A|S) and P(R|S)

    We update the prior for each agent a: P(spy(a)) using P(spy(a) | vote(a)) calculated via Bayes rule

    '''
    def vote_outcome(self, mission, proposer, votes): # calculate P(spy(a) | V) here
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.

        votes is actually a list of agents that voted for the current mission
        '''

        # print(f"\n\nvotes: {votes}")
        # print(f"type votes: {type(votes)}\n\n")

        # update each agent's history of votes for/against missions

        # increment the number of mission approvals for this agent
        self.vote_approve_history[proposer] += 1

        # update the unconditional probability that this proposer is a spy
        self.spy_probability[proposer] = (self.prob_vote_approve_given_spy[proposer] * self.spy_probability[proposer]) / self.prob_vote_approve[proposer] # players on the mission did not necessarily vote for te misson to take place

        # update the marginal distribution for voting approve:
        self.prob_vote_approve[proposer] = self.prob_vote_approve_given_spy[proposer]*self.spy_probability[proposer] + self.prob_vote_approve_given_not_spy[proposer]*(1 - self.spy_probability[proposer])

        for agent in self.all_players:

            ''' do the update for the proposer? '''

            if agent in votes and agent != proposer:

                # increment the number of mission approvals for this agent
                self.vote_approve_history[agent] += 1

                # update the unconditional probability that this agent is a spy
                self.spy_probability[agent] = (self.prob_vote_approve_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_approve[agent] # players on the mission did not necessarily vote for te misson to take place

                # # update the conditional probability that this agent is a spy:
                # self.prob_spy_given_vote_approve[agent] = (self.prob_vote_approve_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_approve[agent]
                #
                # # update the probability that the agent would take this action iven they are a spy
                # self.prob_vote_approve_given_spy[agent] = (self.prob_spy_given_vote_approve[agent] * self.prob_vote_approve[agent]) / self.spy_probability[agent]
                #
                # # Update the probability of voting to accept a team
                # self.prob_vote_approve[agent] = (self.prob_vote_approve_given_spy[agent] * self.spy_probability[agent]) / self.prob_spy_given_vote_approve[agent]

                ''' Version 1 '''
                # # update the marginal distribution for voting approve:
                # self.prob_vote_approve[agent] = self.prob_vote_approve_given_spy[agent]*self.spy_probability[agent] + (1 - self.prob_vote_approve_given_spy[agent])*(1 - self.spy_probability[agent])

                ''' Version 2 '''
                # update the marginal distribution for voting approve:
                self.prob_vote_approve[agent] = self.prob_vote_approve_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_approve_given_not_spy[agent]*(1 - self.spy_probability[agent])


            # if the agent voted to reject the team:
            if agent not in votes and agent != proposer:

                # increment the number of mission betrayals for this agent
                self.vote_reject_history[agent] += 1

                # update the unconditional probability that this agent is a spy
                self.spy_probability[agent] = (self.prob_vote_reject_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_reject[agent]

                # # update the conditional probability that this agent is a spy:
                # self.prob_spy_given_vote_reject[agent] = (self.prob_vote_reject_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_reject[agent]
                #
                # # update the probability that the agent would take this action iven they are a spy
                # self.prob_vote_reject_given_spy[agent] = (self.prob_spy_given_vote_reject[agent] * self.prob_vote_reject[agent]) / self.spy_probability[agent]
                #
                # # Update the probability of voting to reject a team
                # self.prob_vote_reject[agent] = (self.prob_vote_reject_given_spy[agent] * self.spy_probability[agent]) / self.prob_spy_given_vote_reject[agent]

                ''' Version 1 '''
                # # update the marginal distribution for voting reject:
                # self.prob_vote_reject[agent] = self.prob_vote_reject_given_spy[agent]*self.spy_probability[agent] + (1 - self.prob_vote_reject_given_spy[agent])*(1 - self.spy_probability[agent])

                ''' Version 2 '''
                # update the marginal distribution for voting reject:
                self.prob_vote_reject[agent] = self.prob_vote_reject_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_reject_given_not_spy[agent]*(1 - self.spy_probability[agent])

        # # update each agent's history of votes for/against missions
        # for agent in self.all_players:
        #
        #     ''' do the update for the proposer? '''
        #
        #     if agent in votes:
        #
        #         # increment the number of mission approvals for this agent
        #         self.vote_approve_history[agent] += 1
        #
        #         # update the unconditional probability that this agent is a spy
        #         self.spy_probability[agent] = (self.prob_vote_approve_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_approve[agent] # players on the mission did not necessarily vote for te misson to take place
        #
        #         # # update the conditional probability that this agent is a spy:
        #         # self.prob_spy_given_vote_approve[agent] = (self.prob_vote_approve_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_approve[agent]
        #         #
        #         # # update the probability that the agent would take this action iven they are a spy
        #         # self.prob_vote_approve_given_spy[agent] = (self.prob_spy_given_vote_approve[agent] * self.prob_vote_approve[agent]) / self.spy_probability[agent]
        #         #
        #         # # Update the probability of voting to accept a team
        #         # self.prob_vote_approve[agent] = (self.prob_vote_approve_given_spy[agent] * self.spy_probability[agent]) / self.prob_spy_given_vote_approve[agent]
        #
        #         ''' Version 1 '''
        #         # # update the marginal distribution for voting approve:
        #         # self.prob_vote_approve[agent] = self.prob_vote_approve_given_spy[agent]*self.spy_probability[agent] + (1 - self.prob_vote_approve_given_spy[agent])*(1 - self.spy_probability[agent])
        #
        #         ''' Version 2 '''
        #         # update the marginal distribution for voting approve:
        #         self.prob_vote_approve[agent] = self.prob_vote_approve_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_approve_given_not_spy[agent]*(1 - self.spy_probability[agent])
        #
        #
        #     # if the agent voted to reject the team:
        #     if agent not in votes:
        #
        #         # increment the number of mission betrayals for this agent
        #         self.vote_reject_history[agent] += 1
        #
        #         # update the unconditional probability that this agent is a spy
        #         self.spy_probability[agent] = (self.prob_vote_reject_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_reject[agent]
        #
        #         # # update the conditional probability that this agent is a spy:
        #         # self.prob_spy_given_vote_reject[agent] = (self.prob_vote_reject_given_spy[agent] * self.spy_probability[agent]) / self.prob_vote_reject[agent]
        #         #
        #         # # update the probability that the agent would take this action iven they are a spy
        #         # self.prob_vote_reject_given_spy[agent] = (self.prob_spy_given_vote_reject[agent] * self.prob_vote_reject[agent]) / self.spy_probability[agent]
        #         #
        #         # # Update the probability of voting to reject a team
        #         # self.prob_vote_reject[agent] = (self.prob_vote_reject_given_spy[agent] * self.spy_probability[agent]) / self.prob_spy_given_vote_reject[agent]
        #
        #         ''' Version 1 '''
        #         # # update the marginal distribution for voting reject:
        #         # self.prob_vote_reject[agent] = self.prob_vote_reject_given_spy[agent]*self.spy_probability[agent] + (1 - self.prob_vote_reject_given_spy[agent])*(1 - self.spy_probability[agent])
        #
        #         ''' Version 2 '''
        #         # update the marginal distribution for voting reject:
        #         self.prob_vote_reject[agent] = self.prob_vote_reject_given_spy[agent]*self.spy_probability[agent] + self.prob_vote_reject_given_not_spy[agent]*(1 - self.spy_probability[agent])



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
            return random.random() < 0.7 # betray with probability 0.7 if spy
        else:
            return False # play for mission success if resistance

    '''
    update the suspicion estimates for all players on the mission, based upon the success/failure of the mission

    for all players:
        if the player was on the mission, find:
            - P(spy|mission failure)
            - P(spy|mission success)
    '''
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

        # print(f"\n\nmission: {mission}\n\n") # mission is curently a list containing a name and a variable number of ints - not good!

        # if the mission was sabotaged
        if not mission_success:

            # for all players on this mission, at least one of these are spies
            for agent in mission:

                # update the suspicion estimate for all players on the team: P(spy(a) | Z) = P(Z | spy(a)) * P(spy(a)) / P(Z)
                self.spy_probability[agent] = (self.prob_betray_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_sabotage[agent]

                # # update the conditional probability that this agent is a spy:
                # self.prob_spy_given_betray_mission[agent] = (self.prob_betray_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_sabotage[agent]
                #
                # # update the probability that the agent would take this action iven they are a spy
                # self.prob_betray_mission_given_spy[agent] = (self.prob_spy_given_betray_mission[agent] * self.prob_sabotage[agent]) / self.spy_probability[agent]
                #
                # # Update the probability of voting to accept a team
                # self.prob_sabotage[agent] = (self.prob_betray_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_spy_given_betray_mission[agent]

                ''' Version 1 '''
                # # update marginal distribution for sabotage probability:
                # self.prob_sabotage[agent] = self.prob_betray_mission_given_spy[agent]*self.spy_probability[agent] + (1 - self.prob_betray_mission_given_spy[agent])*(1 - self.spy_probability[agent])

                ''' Version 2 '''
                # update marginal distribution for sabotage probability:
                self.prob_sabotage[agent] = self.prob_betray_mission_given_spy[agent]*self.spy_probability[agent] + self.prob_betray_mission_given_not_spy[agent]*(1 - self.spy_probability[agent])


        # if the mission was a success:
        else:

            # for all players on this mission:
            for agent in mission:

                # update the suspicion estimate for all players on the team: P(spy(a) | P) = P(P | spy(a)) * P(spy(a)) / P(P)
                self.spy_probability[agent] = (self.prob_play_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_play_mission[agent]

                # # update the conditional probability that this agent is a spy:
                # self.prob_spy_given_play_mission[agent] = (self.prob_play_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_play_mission[agent]
                #
                # # update the probability that the agent would take this action iven they are a spy
                # self.prob_play_mission_given_spy[agent] = (self.prob_spy_given_play_mission[agent] * self.prob_play_mission[agent]) / self.spy_probability[agent]
                #
                # # Update the probability of voting to accept a team
                # self.prob_play_mission[agent] = (self.prob_play_mission_given_spy[agent] * self.spy_probability[agent]) / self.prob_spy_given_play_mission[agent]

                ''' Version 1 '''
                # # update marginal distribution for play mission probability:
                # self.prob_sabotage[agent] = self.prob_play_mission_given_spy[agent]*self.spy_probability[agent] + (1 - self.prob_play_mission_given_spy[agent])*(1 - self.spy_probability[agent])

                ''' Version 2 '''
                # update marginal distribution for play mission probability:
                self.prob_sabotage[agent] = self.prob_play_mission_given_spy[agent]*self.spy_probability[agent] + self.prob_play_mission_given_not_spy[agent]*(1 - self.spy_probability[agent])

        self.current_mission += 1

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        pass
        # print(f"Number of completed rounds:   {rounds_complete}")
        # print(f"Number of sabotaged missions: {missions_failed}")

    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        pass
        # if spies_win:
        #     print("\n\nThe spies win!")
        #     print(f"they were: {spies}\n\n")
        # else:
        #     print("\n\nthe resistance wins!")
        #     print(f"The spies were: {spies}\n\n")

    '''
    N = round number
    P = Number of players
    S = number of spies
    M = number of missions participated in
    F = number of times been on failed mission
    A = number of times has proposed missions.
    B = Number of times has proposed failed missions

    State = [N, P, S, M, F, A, B]

    Actions = {
        Play Mission = {Play Betray Mission, Play Succed Mission,}
        Propose Team,
        Vote on team = {Accept Team, Reject Team}
    }

    Reward(resistance) = +1 for winning the round, 0 otherwise
    Reward(spy) = +1 for winning the round, 0 otherwise

    V(S) = number of rounds won for all states prior to S. more rounds won prior to S -> greater V(S)
    '''
