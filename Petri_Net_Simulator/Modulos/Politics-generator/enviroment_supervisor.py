import re
from requirements import Requirements
import matplotlib.pyplot as plt


class Enviroment_Supervisor:

    def __init__(self,TInv,enviroment,requirements,step):
        self._enviroment = enviroment
        self.step = step
        self._requirements = requirements
        self.tInvs = list(TInv.values())
        self.createRegEx(TInv)
        self._historic_counters = []
        for i in range(len(self.tInvs)):
            self._historic_counters.append([])       

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

    def next_step(self):
        patterns = []
        for string in self.regex_list:
            patterns.append(re.compile(string))
        
        res = self._enviroment.historic_fires

        self._enviroment.historic_fires = ""

        counters = [0] * len(self.regex_list)

        while True:
            nuevo_resultado = ""
            for pattern_idx in range(len(patterns)):
                match = patterns[pattern_idx].match(res)
                if match:
                    counters[pattern_idx] += 1; 
                    break
            if not match:
                break
            for group in match.groups():
                if group is not None: nuevo_resultado += group
            res = nuevo_resultado
        
        print("Contadores")
        print(counters)
        porcentual_count = [x / sum(counters) for x in counters]
        print("Resultados buscados")
        print(self._requirements.Inv_Politics)
        print("Contadores expresados en porcentaje")
        print(porcentual_count)
        print("Vector costos antes: ")
        print(self._enviroment.cost_vector)
        for i in range(len(counters)):
            self._historic_counters[i].append(porcentual_count[i])
        for i in range(len(porcentual_count)):
            if(porcentual_count[i] < self._requirements.Inv_Politics[i]):
                for transition in self.tInvs[i]:
                    self._enviroment.cost_vector[transition-1] -= 1
            elif(porcentual_count[i] > self._requirements.Inv_Politics[i]):
                for transition in self.tInvs[i]:
                    self._enviroment.cost_vector[transition-1] += 1
        print("Vector costos despues: ")
        print(self._enviroment.cost_vector)

    def print_total_fire_proportions(self):
        '''
        print("Searched results:")
        print(self._requirements.Inv_Politics)
        porcentual_count = [x / sum(self._historic_counters) for x in self._historic_counters]
        print("Total acumulated fires in %")
        print(porcentual_count)
        '''
        plt.figure()
        n_plots = len(self._historic_counters)
        fig, ax = plt.subplots(n_plots)
        for invariant in range(n_plots):
            ax[invariant].scatter(x = range(len(self._historic_counters[invariant])), y = self._historic_counters[invariant])
            ax[invariant].axhline(y=self._requirements.Inv_Politics[invariant], color='r', linestyle='-')
        plt.show()
        plt.close()
        
