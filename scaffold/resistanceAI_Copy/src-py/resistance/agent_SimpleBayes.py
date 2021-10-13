from agent import Agent
import random
import numpy as np

'''
Author: Fraser Paterson (22258324)
'''

# NOTES:
# maintain a probability estmate for the probability that each agent is a spy
# adjust with basean update each game

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
        self.name = name # a string representing the agent
        self.spy_probabilities = {} # key is agent, value is prob that this agent is a spy

        # all relevant prior probabilities conditioned on the agent being a spy
        self.prob_vote_approve_given_spy_priors = {}
        self.prob_vote_reject_given_spy_priors = {}
        self.prob_nominate_team_given_spy_priors = {}
        self.prob_play_mission_given_spy_priors = {}
        self.prob_betray_mission_given_spy_priors = {}

        # prior probabilities for all actions:
        self.prob_vote_approve = {}
        self.prob_vote_reject = {}
        self.prob_nominate_team = {}
        self.prob_play_mission = {}
        self.prob_sabotage = {}

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

    def sort_dict_by_value(self, D): # D is empty !!!!
        # print(f"\n\ninside sort_dict_by_value: {D}\n\n")
        sorted_values = sorted(D.values()) # Sort the values
        sorted_dict = {}

        for i in sorted_values:
            for k in D.keys():
                if D[k] == i:
                    sorted_dict[k] = D[k]
                    break

        return sorted_dict

    def dict_max_by_value(self, D):
        # print(f"\n\ninside dict_max_by_value: {D}\n\n")
        sorted = self.sort_dict_by_value(D)
        return (list(sorted)[-1], D[list(sorted)[-1]])

    def am_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def new_game(self, number_of_players, player_number, spy_list): # add leader?
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
            self.spy_probabilities[i] = 1/self.number_of_players

            # self.number_of_players.append(0)
            self.vote_approve_history[i] = 0
            self.vote_reject_history[i] = 0

            # initialize prior conditional prpbabilities:
            self.prob_vote_approve_given_spy_priors[i] = 1/self.number_of_players
            self.prob_vote_reject_given_spy_priors[i] = 1/(self.number_of_players - 1)
            self.prob_nominate_team_given_spy_priors[i] = 1/self.number_of_players
            self.prob_play_mission_given_spy_priors[i] = 1/(self.number_of_players - 1)
            self.prob_betray_mission_given_spy_priors[i] = 1/(self.number_of_players - 1)

            # initialize prior action probabilities:
            self.prob_vote_approve[i] = 1/self.number_of_players
            self.prob_vote_reject[i] = 1/(self.number_of_players - 1)
            self.prob_nominate_team[i] = 1/self.number_of_players
            self.prob_play_mission[i] = 1/(self.number_of_players - 1)
            self.prob_sabotage[i] = 1/(self.number_of_players - 1)

        if self.am_spy():

            # # init the prob that any one player is a spy to the uniform distribution:
            # for agent, spy_probability in self.spy_probabilities.items():
            #
            #     # spies still need to model resistane decison making; for optimal spy-play
            #     self.spy_probabilities[agent] = 1 / self.number_of_players

            return spy_list

        else:

            # # init the prob that any one player is a spy to the uniform distribution:
            # for agent, spy_probability in self.spy_probabilities.items():
            #
            #     self.spy_probabilities[agent] = 1 / self.number_of_players # the prior probability for P(spy(agent))

            return []


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
        team = []

        # if proposer is spy
        if self.am_spy():

            # print(f"\n\nspy probs: {self.spy_probabilities}\n\n")

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

            # always select self as team member:
            team.append(self.player_number)

            # print(f"\n\nspy probs: {self.spy_probabilities}\n\n")

            # sort the spy_probabilities by probability (ascending order):
            ascending_spy_probabilities = self.sort_dict_by_value(self.spy_probabilities)

            # add players that have lowest prob of being a spy to the team:
            for player, probability in ascending_spy_probabilities.items():

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
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''

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
                if player == self.dict_max_by_value(self.spy_probabilities)[0]:
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

        votes is actually a list of agents that voted for the currentmission
        '''

        # print(f"\n\nvotes: {votes}")
        # print(f"type votes: {type(votes)}\n\n")

        # update each agent's history of votes for/against missions
        for agent in self.all_players:

            if agent in votes:

                # increment the number of mission approvals for this agent
                self.vote_approve_history[agent] += 1
                self.spy_probabilities[agent] = (self.prob_vote_approve_given_spy_priors[agent] * self.spy_probabilities[agent]) / self.prob_vote_approve[agent] # Bayesian update for votes
                '''
                Perhaps also store the particular mission?
                '''

            # if the agent voted to reject the team:
            if agent not in votes:

                # increment the number of mission betrayals for this agent
                self.vote_reject_history[agent] += 1
                self.spy_probabilities[agent] = (self.prob_vote_reject_given_spy_priors[agent] * self.spy_probabilities[agent]) / self.prob_vote_reject[agent] # Bayesian update for votes
                '''
                Perhaps also store the particular mission?
                '''

        # # update each agent's history of votes for/against missions
        # for agent_number in votes:
        #
        #     # if the agent voted for the mission
        #     if vote == True:
        #
        #         # increment the number of mission approvals for this agent
        #         self.vote_approve_history[agent] += 1
        #         self.spy_probabilities[agent] = (self.prob_vote_approve_given_spy_priors[agent] * self.spy_probabilities[agent]) / self.prob_vote_approve[agent] # Bayesian update for votes
        #         '''
        #         Perhaps also store the particular mission?
        #         '''
        #
        #     # if the agent voted to reject the team:
        #     else:
        #
        #         # increment the number of mission betrayals for this agent
        #         self.vote_reject_history[agent] += 1
        #         self.spy_probabilities[agent] = (self.prob_vote_reject_given_spy_priors[agent] * self.spy_probabilities[agent]) / self.prob_vote_reject[agent] # Bayesian update for votes
        #         '''
        #         Perhaps also store the particular mission?
        #         '''

        # # update each agent's history of votes for/against missions
        # for agent, vote in votes.items():
        #
        #     # if the agent voted for the mission
        #     if vote == True:
        #
        #         # increment the number of mission approvals for this agent
        #         self.vote_approve_history[agent] += 1
        #         self.spy_probabilities[agent] = (self.prob_vote_approve_given_spy_priors[agent] * self.spy_probabilities[agent]) / self.prob_vote_approve[agent] # Bayesian update for votes
        #         '''
        #         Perhaps also store the particular mission?
        #         '''
        #
        #     # if the agent voted to reject the team:
        #     else:
        #
        #         # increment the number of mission betrayals for this agent
        #         self.vote_reject_history[agent] += 1
        #         self.spy_probabilities[agent] = (self.prob_vote_reject_given_spy_priors[agent] * self.spy_probabilities[agent]) / self.prob_vote_reject[agent] # Bayesian update for votes
        #         '''
        #         Perhaps also store the particular mission?
        #         '''

    def betray(self, mission, proposer): # play success/play sabotage
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise.
        Only spies are permitted to betray the mission.
        '''

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
        '''

        print(f"\n\nmission: {mission}\n\n") # mission is curently a list containing a name and a variable number of ints - not good!

        # if the mission was sabotaged
        if not mission_success:

            # for all players on this mission, at least one of these are spies
            for agent in mission:

                # update the suspicion estimate for all players on the team: P(spy(a) | Z) = P(Z | spy(a)) * P(spy(a)) / P(Z)
                self.spy_probabilities[agent] = (self.prob_betray_mission_given_spy_priors[agent] * self.spy_probabilities[agent]) / self.prob_sabotage[agent] # Bayesian update for mission plays

        # if the mission was a success:
        else:

            # for all players on this mission:
            for agent in mission:

                # update the suspicion estimate for all players on the team: P(spy(a) | P) = P(P | spy(a)) * P(spy(a)) / P(P)
                self.spy_probabilities[agent] = (self.prob_play_mission_given_spy_priors[agent] * self.spy_probabilities[agent]) / self.prob_play_mission[agent] # Bayesian update for mission plays

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

# if __name__ == '__main__':
#     mission_sizes = {
#             5:[2,3,2,3,3], \
#             6:[3,3,3,3,3], \
#             7:[2,3,3,4,5], \
#             8:[3,4,4,5,5], \
#             9:[3,4,4,5,5], \
#             10:[3,4,4,5,5]
#     }
#
#     #number of spies for different game sizes
#     spy_count = {5:2, 6:2, 7:3, 8:3, 9:3, 10:4}
#
#     #e.g. self.betrayals_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail # OG
#     #e.g. self.fails_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail
#
#     # for key : value in fails_required, key = number of players in the game,
#     # val[i] = n where i is the mission number and n is number of betreyals required for mission of size i to fail
#     fails_required = {
#             5:[1,1,1,1,1], \
#             6:[1,1,1,1,1], \
#             7:[1,1,1,2,1], \
#             8:[1,1,1,2,1], \
#             9:[1,1,1,2,1], \
#             10:[1,1,1,2,1]
#     }
#     name = "agent 1"
#
#     agent = SimpleBayesAgent(name, fails_required, mission_sizes)
#     agent.new_game(5, 0, spies):
#     team = agent.propose_mission(3)
#     print(f"\n\nteam: {team}\n\n")


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
