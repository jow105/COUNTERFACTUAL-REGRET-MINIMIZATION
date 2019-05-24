#####################################################################
# Before implementing CFR, it will be helpful to take a look
# at the helper methods in game.py. These are the methods you
# need to interact with when you traverse the game tree in
# CFR.
#####################################################################
import sys
from game import Game


######################################################
# Add any classes or helper functions you want here
######################################################

def init_action_ev(game,d):
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

def init_prob(game,d):
    for node in xrange(game.get_num_nodes()):
        if(not game.is_leaf(node) and game.get_current_player(node) != -1):
            p = game.get_current_player(node)
            infoset_id = game.get_node_infoset(node)
            d[p][infoset_id] = [0]*game.get_num_actions_infoset(p,infoset_id)
    return d

def init_seen(game,d):
    for node in xrange(game.get_num_nodes()):
        if(not game.is_leaf(node) and game.get_current_player(node) != -1):
            p = game.get_current_player(node)
            infoset_id = game.get_node_infoset(node)
            d[p][infoset_id] = 0
    return d

def equal_probs(game,node):
    actions = range(game.get_num_actions_node(node))
    probabilities = []
    p = 1.0/((float)(len(actions)))
    for _ in xrange(len(actions)):
        probabilities.append(p)
    return probabilities

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

def set_zero_regrets(game,regret):
    for node in xrange(game.get_num_nodes()):
        if(not game.is_leaf(node) and game.get_current_player(node) != -1):
            p = game.get_current_player(node)
            infoset_id = game.get_node_infoset(node)
            for action in xrange(len(regret[p][infoset_id])):
                if(regret[p][infoset_id][action] < 0):
                    regret[p][infoset_id][action] = 0
            return regret

def zero_regrets(regret):
    no_regrets = 0
    for i in xrange(len(regret)):
        if(regret[i] <= 0):
            no_regrets += 1
    return (no_regrets == len(regret))

# game will be an instance of Game, which is defined in game.py
# num_iterations is the number of CFR+ iterations you should perform.
# An iteration of CFR+ is one traversal of the entire game tree for each player.
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
    # Implement CFR+ in here
    #######################

    for info_id in xrange(game.get_num_infosets(0)):
        strategy_profile[0][info_id] = [0]*game.get_num_actions_infoset(0,info_id)

    for info_id in xrange(game.get_num_infosets(1)):
        strategy_profile[1][info_id] = [0]*game.get_num_actions_infoset(1,info_id)

    # maps node to list of action expected values
    action_ev = {}
    # maps regret to player to information set to regrets for each information set
    regret = {0:{}, 1:{}}
    prob = {0:{}, 1:{}}
    seen = {0:{}, 1:{}}

    action_ev = init_action_ev(game,action_ev)
    regret = init_regret_values(game,regret)
    prob = init_prob(game,prob)

    def CFR(node,reach,p,iteration):
        if(game.is_leaf(node)):
            if(player == 0):
                return game.get_leaf_utility(node)*reach
            if(player == 1):
                return -1*game.get_leaf_utility(node)*reach
        else:
            ev = 0
            if(game.get_current_player(node) == -1):
                for action in xrange(game.get_num_actions_node(node)):
                    ev += CFR(game.get_child_id(node,action),reach*game.get_nature_probability(node,action),p,iteration)
            else:
                # print "node = " + str(node)
                # print "regret = " + str(regret)
                # print "p = " + str(p)
                # if(zero_regrets(regret[0][game.get_node_infoset(node)])):
                #     prob[0][game.get_node_infoset(node)] = equal_probs(game,node)
                # if(zero_regrets(regret[1][game.get_node_infoset(node)])):
                #     prob[1][game.get_node_infoset(node)] = equal_probs(game,node)
                if(zero_regrets(regret[game.get_current_player(node)][game.get_node_infoset(node)])):
                    prob[game.get_current_player(node)][game.get_node_infoset(node)] = equal_probs(game,node)
                else:
                    if(seen[game.get_current_player(node)][game.get_node_infoset(node)] == 0):
                        # prob[0][game.get_node_infoset(node)] = normalize_regret(regret[0][game.get_node_infoset(node)])
                        # prob[1][game.get_node_infoset(node)] = normalize_regret(regret[1][game.get_node_infoset(node)])
                        prob[game.get_current_player(node)][game.get_node_infoset(node)] = normalize_regret(regret[game.get_current_player(node)][game.get_node_infoset(node)])

                if(game.get_current_player(node) == p):
                    seen[p][game.get_node_infoset(node)] = 1
                    for action in xrange(game.get_num_actions_node(node)):
                        action_ev[node][action] = CFR(game.get_child_id(node,action),reach,p,iteration)
                        ev += prob[p][game.get_node_infoset(node)][action]*action_ev[node][action]
                    for action in xrange(game.get_num_actions_node(node)):
                        regret[p][game.get_node_infoset(node)][action] += (action_ev[node][action] - ev)
                else:
                    seen[game.get_current_player(node)][game.get_node_infoset(node)] = 1
                    for action in xrange(game.get_num_actions_node(node)):
                        strategy_profile[game.get_current_player(node)][game.get_node_infoset(node)][action] += iteration*reach*prob[game.get_current_player(node)][game.get_node_infoset(node)][action]
                        ev += CFR(game.get_child_id(node,action),reach*prob[game.get_current_player(node)][game.get_node_infoset(node)][action],p,iteration)
            return ev

    for i in xrange(num_iterations):
        for player in [0,1]:
            seen = init_seen(game,seen)
            CFR(game.get_root(),1,player,i+1)
            seen = init_seen(game,seen)
        # set regrets below 0 to 0
        regret = set_zero_regrets(game,regret)

    for info_id in xrange(game.get_num_infosets(0)):
        strategy_profile[0][info_id] = normalize(strategy_profile[0][info_id])

    for info_id in xrange(game.get_num_infosets(1)):
        strategy_profile[1][info_id] = normalize(strategy_profile[1][info_id])

    return strategy_profile




if __name__ == "__main__":
    # feel free to add any test code you want in here. It will not interfere with our testing of your code.
    # currently, this file can be invoked with:
    # python cfr.py <path/to/gamefile> <num CFR+ iterations>

    filename = sys.argv[1]
    iterations = int(sys.argv[2])

    game = Game()
    game.read_game_file(filename)

    strategy_profile = solve_game(game, iterations)
    print "Expected Value: " + str(game.compute_strategy_profile_ev(strategy_profile))
    print "Exploitability: " + str(game.compute_strategy_profile_exp(strategy_profile))
