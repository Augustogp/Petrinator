import numpy as np

class Requirements:
    def __init__(self,num_TInv):
        self.Inv_Politics = {}
        list_probabilities = np.random.dirichlet(np.ones(num_TInv),size=1)
        self.Inv_Politics = dict(enumerate(list_probabilities.flatten()))
        print("Probabilidades T INV")
        print(self.Inv_Politics)
        