class Invariant_Cost_Manager:

    def __init__(self,num_transitions,TInvs):
        self.cost_vector = [5] * num_transitions
        print(self.cost_vector)
        self.mean_cost = 0
        self.historic_costs = []
        self.TInvs = list(TInvs.values())

    def updateCost(self,transition):
        self.historic_costs.append(self.cost_vector[transition])
        reward = (self.cost_vector[transition] - self.mean_cost) / 100
        self.mean_cost = self.mean_cost + (self.cost_vector[transition] - self.mean_cost) / len(self.historic_costs)
        return reward