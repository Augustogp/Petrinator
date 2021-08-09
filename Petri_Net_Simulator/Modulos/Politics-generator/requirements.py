import numpy as np

class Requirements:
    def __init__(self,num_TInv):
        self.Inv_Politics = {}
        list_probabilities = np.random.dirichlet(np.ones(num_TInv),size=1)
        self.Inv_Politics = dict(enumerate(list_probabilities.flatten()))
        for i in range(len(self.Inv_Politics)):
            self.Inv_Politics[i] = 1/len(self.Inv_Politics)
        self.Inv_Politics[0] = 0.2
        self.Inv_Politics[1] = 0.3
        self.Inv_Politics[2] = 0.5
        #self.Inv_Politics[3] = 0.2
        print("Probabilidades T Inv")
        print(self.Inv_Politics)
        