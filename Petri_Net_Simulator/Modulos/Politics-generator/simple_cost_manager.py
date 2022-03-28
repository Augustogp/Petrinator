import re

class Simple_Cost_Manager:

    def __init__(self,num_transitions,TInvs):
        self.cost_vector = [5] * num_transitions
        print(self.cost_vector)
        self.mean_cost = 0
        self.historic_costs = []
        self.createRegEx(TInvs)
        self.partial_inv = ""
        self.inv_counters = [0] * len(self.regex_list)
        self.inv_counters_acum = [0] * len(self.regex_list)
        self.patterns = []
        for string in self.regex_list:
            self.patterns.append(re.compile(string))

    def updateCost(self,transition):

        self.checkCounters()
        self.historic_costs.append(self.cost_vector[transition])
        reward = (self.cost_vector[transition] - self.mean_cost) / 100
        self.mean_cost = self.mean_cost + (self.cost_vector[transition] - self.mean_cost) / len(self.historic_costs)
        return reward

    def checkCounters(self):        
        new_str = ""
        for pattern_idx in range(len(self.patterns)):
            match = self.patterns[pattern_idx].match(self.partial_inv)
            if match:
                self.inv_counters[pattern_idx] += 1
                for group in match.groups():
                    if group is not None: new_str += group
                self.partial_inv = new_str
                break
        
    

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