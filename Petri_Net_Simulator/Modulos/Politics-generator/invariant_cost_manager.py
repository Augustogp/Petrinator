import re
import numpy as np
import math

class Invariant_Cost_Manager:

    def __init__(self,num_transitions,TInvs):
        self.cost_vector = [5] * num_transitions
        '''
        self.cost_vector[0] = 0
        self.cost_vector[1] = 5
        self.cost_vector[2] = 5
        self.cost_vector[3] = 5
        self.cost_vector[4] = 5
        self.cost_vector[5] = 3
        self.cost_vector[6] = 1
        self.cost_vector[7] = 2
        self.cost_vector[8] = 1
        self.cost_vector[9] = 1
        self.cost_vector[10] = 0
        self.cost_vector[11] = 1
        self.cost_vector[12] = 6
        self.cost_vector[13] = 15
        self.cost_vector[14] = 3
        self.cost_vector[15] = 8
        self.cost_vector[16] = 6
        self.cost_vector[17] = 8
        self.cost_vector[18] = 5
        self.cost_vector[19] = 0
        '''

        print(self.cost_vector)
        self.mean_cost = 0
        self.historic_costs = []
        self.createRegEx(TInvs)
        self.TInvs = list(TInvs.values())
        self.partial_inv = ""
        self.inv_counters = [0] * len(self.regex_list)
        self.inv_counters_acum = [0] * len(self.regex_list)
        self.patterns = []
        for string in self.regex_list:
            self.patterns.append(re.compile(string))

        for invariant in range(len(self.TInvs)):
            cost_inv = self.get_inv_cost(invariant)
            print("Costo invariante %d: %d" %(invariant,cost_inv))

    def updateCost(self,transition):
        self.checkCounters()
        cost_list = []
        for inv in range(len(self.TInvs)):
            if (transition+1) in self.TInvs[inv]:
                cost_list.append(self.get_inv_cost(inv))
        cost = np.mean(cost_list)
        if len(self.historic_costs) == 0:
            return 0
        self.mean_cost = np.mean(self.historic_costs[-5:])
        reward = (cost - self.mean_cost) / 100
        return reward

    def checkCounters(self):
        new_str = ""
        for pattern_idx in range(len(self.patterns)):
            match = self.patterns[pattern_idx].match(self.partial_inv)
            if match:
                self.inv_counters[pattern_idx] += 1
                self.historic_costs.append(self.get_inv_cost(int(pattern_idx)))
                for group in match.groups():
                    if group is not None: new_str += group
                self.partial_inv = new_str
                break
        
    def get_inv_cost(self, inv):
        acum = 0
        for transition in self.TInvs[inv]:
            acum += self.cost_vector[transition-1]
        return acum

    def createRegEx(self,TInv):
        self.regex_list = []
        for key in TInv:
            invariant = TInv[key]
            regex = "(.*)"
            for transition in range(len(invariant)):
                regex += ",T" + str(invariant[transition] - 1) + ","
                if transition < len(invariant) - 1:
                    regex += "(.*?)"
            regex += "(.*)"
            self.regex_list.append(regex)