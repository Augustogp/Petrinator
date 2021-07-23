import re
from requirements import Requirements

class Enviroment_Supervisor:

    def __init__(self,TInv,enviroment,requirements,step):
        self._enviroment = enviroment
        self.step = step
        self._requirements = requirements
        self.tInvs = list(TInv.values())
        self.createRegEx(TInv)

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
        for i in range(len(porcentual_count)):
            if(porcentual_count[i] < self._requirements.Inv_Politics[i]):
                for transition in self.tInvs[i]:
                    self._enviroment.cost_vector[transition-1] += 1
            elif(porcentual_count[i] > self._requirements.Inv_Politics[i]):
                for transition in self.tInvs[i]:
                    self._enviroment.cost_vector[transition-1] -= 1        
