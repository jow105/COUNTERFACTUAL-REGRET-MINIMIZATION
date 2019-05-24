#####################################################################
# Before implementing CFR, it will be helpful to take a look
# at the helper methods in game.py. These are the methods you
# need to interact with when you traverse the game tree in
# CFR.
#####################################################################
import sys
import random
from game import Game


######################################################
# Add any classes or helper functions you want here
######################################################

def rand_select(dist):
    r = random.uniform(0,1)
    total = 0
    for (action,prob) in dist:
        total += prob
        if total >= r:
            return action

def zipWith_probabilities(game, node):
    actions = range(game.get_num_actions_node(node))
    probabilities = []
    if(game.get_current_player(node) == -1):
        for action in actions:
            probabilities.append(game.get_nature_probability(node,action))
    else:
        num_actions = game.get_num_actions_node(node)
        p = 1.0/((float)(num_actions))
        for _ in xrange(num_actions):
            probabilities.append(p)
    return zip(actions,probabilities)

def init_action_values(game,d):
    for node in xrange(game.get_num_nodes()):
        if(not game.is_leaf(node) and game.get_current_player(node) != -1):
            d[node] = [0]*game.get_num_actions_node(node)
    return d

def init_regret_values(game,d):
    for node in xrange(game.get_num_nodes()):
        if(not game.is_leaf(node) and game.get_current_player(node) != -1):
            p = game.get_current_player(node)
            infoset_id = game.get_node_infoset(node)
            d[p][infoset_id] = [0]*game.get_num_actions_infoset(p,infoset_id)
    return d

def normalize_regret(regret):
    # regret = [0,1,2,1,3,0,0]
    temp = regret
    for i in xrange(len(temp)):
        if(temp[i] < 0):
            temp[i] = 0

    total = 0
    for i in xrange(len(temp)):
        total += temp[i]

    normalized = [0]*len(temp)
    for i in xrange(len(temp)):
        normalized[i] = ((float)(temp[i]))/((float)(total))

    return normalized

def normalize(L):
    temp = L
    total = 0
    for i in xrange(len(L)):
        total += L[i]

    for i in xrange(len(L)):
        temp[i] = ((float)(temp[i]))/((float)(total))

    return temp

def no_regrets(regret):
    no_regrets = 0
    for i in xrange(len(regret)):
        if(regret[i] <= 0):
            no_regrets += 1
    return (no_regrets == len(regret))

# game will be an instance of Game, which is defined in game.py
# num_iterations is the number of PureCFR/MCCFR iterations you should perform.
# An iteration of PureCFR/MCCFR is one traversal of the entire game tree for each player
def solve_game(game, num_iterations):
#############################
    # The goal of your algorithm is to fill
    # strategy_profile with equilibrium strategies.
    # strategy_profile[p][i][a] should return
    # the probability of player p choosing the particular
    # action a at information set i in the equilibrium
    # you compute.
    #
    # An example set of values for a small game with 2
    # information sets for each player would be:
    #    strategy_profile[0][0] = [0.375, 0.625]
    #    strategy_profile[0][1] = [1,0]
    #
    #    strategy_profile[1][0] = [0.508929, 0.491071]
    #    strategy_profile[1][1] = [0.666667, 0.333333]
    strategy_profile = {0:{}, 1:{}}

    #######################
    # Implement PureCFR or MCCFR in here
    #######################

    for info_id in xrange(game.get_num_infosets(0)):
        strategy_profile[0][info_id] = [0]*game.get_num_actions_infoset(0,info_id)

    for info_id in xrange(game.get_num_infosets(1)):
        strategy_profile[1][info_id] = [0]*game.get_num_actions_infoset(1,info_id)

    action_value = {}
    regret = {0:{}, 1:{}}

    action_value = init_action_values(game,action_value)
    regret = init_regret_values(game,regret)

    def PureCFR(node,player):
        if(game.is_leaf(node)):
            if(player == 0):
                return game.get_leaf_utility(node)
            if(player == 1):
                return -1*game.get_leaf_utility(node)
        else:
            if(game.get_current_player(node) == -1):
                # sample action a from chance distribution
                dist = zipWith_probabilities(game,node)
                action = rand_select(dist)
                return PureCFR(game.get_child_id(node,action),player)
            elif(game.get_current_player(node) != player):
                # set probabilities for actions in proportion to positive regret
                # sample action a
                # if all regrets are 0 or all negative
                action = None
                # print "regret = " + str(regret)
                # print "infoset = " + str(game.get_node_infoset(node))
                # print "node = " + str(node)
                # print "player = " + str(player)

                curr_regrets = regret[game.get_current_player(node)][game.get_node_infoset(node)]

                # print "curr_regrets = " + str(curr_regrets)
                # print "--------------------------------------------"

                if(no_regrets(curr_regrets)):
                    dist = zipWith_probabilities(game,node)
                    action = rand_select(dist)
                else:
                    action_probs = normalize_regret(curr_regrets)
                    dist = zip(range(game.get_num_actions_node(node)),action_probs)
                    action = rand_select(dist)

                strategy_profile[game.get_current_player(node)][game.get_node_infoset(node)][action] += 1
                return PureCFR(game.get_child_id(node,action),player)
            else:
                # set probabilities for actions in proportion to positive regret
                # sample action a
                a = None
                curr_regrets = regret[player][game.get_node_infoset(node)]
                if(no_regrets(curr_regrets)):
                    dist = zipWith_probabilities(game,node)
                    a = rand_select(dist)
                else:
                    action_probs = normalize_regret(curr_regrets)
                    dist = zip(range(game.get_num_actions_node(node)),action_probs)
                    a = rand_select(dist)

                for action in xrange(game.get_num_actions_node(node)):
                    action_value[node][action] = PureCFR(game.get_child_id(node,action),player)

                for action in xrange(game.get_num_actions_node(node)):
                    regret[player][game.get_node_infoset(node)][action] += (action_value[node][action] - action_value[node][a])
                
                return action_value[node][a]

    for i in xrange(num_iterations):
        for player in [0,1]:
            PureCFR(game.get_root(),player)

    for info_id in xrange(game.get_num_infosets(0)):
        strategy_profile[0][info_id] = normalize(strategy_profile[0][info_id])

    for info_id in xrange(game.get_num_infosets(1)):
        strategy_profile[1][info_id] = normalize(strategy_profile[1][info_id])

    return strategy_profile




if __name__ == "__main__":
    # feel free to add any test code you want in here. It will not interfere with our testing of your code.
    # currently, this file can be invoked with:
    # python cfr.py <path/to/gamefile> <num PureCFR/MCCFR iterations>

    filename = sys.argv[1]
    iterations = int(sys.argv[2])

    game = Game()
    game.read_game_file(filename)

    strategy_profile = solve_game(game, iterations)
    print "Expected Value: " + str(game.compute_strategy_profile_ev(strategy_profile))
    print "Exploitability: " + str(game.compute_strategy_profile_exp(strategy_profile))