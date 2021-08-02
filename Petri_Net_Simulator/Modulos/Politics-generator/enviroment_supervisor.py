import re
from requirements import Requirements
import matplotlib.pyplot as plt


class Enviroment_Supervisor:

    def __init__(self,TInv,enviroment,requirements,batch,num_batches=5):
        self._enviroment = enviroment
        self.batch = batch
        self.batches_dict = {}
        self.num_batches = num_batches
        self._requirements = requirements
        self.tInvs = list(TInv.values())
        self.createRegEx(TInv)
        self._historic_counters = []
        for i in range(len(self.tInvs)):
            self._historic_counters.append([])      

    def new_batch(self):
        new_batch = self._enviroment.historic_fires
        self._enviroment.historic_fires = ""
        vector_batches_len = len(self.batches_dict)
        if(vector_batches_len < self.num_batches):
            self.batches_dict[vector_batches_len] = new_batch
        else:
            for batch in range(len(self.batches_dict)):
                if(batch == self.num_batches - 1):
                    self.batches_dict[batch] = new_batch
                else:
                    self.batches_dict[batch] = self.batches_dict[batch + 1]
        if(len(self.batches_dict) == self.num_batches):
            self.next_step()

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

    def get_pond_vector_by_batch(self):
        vector = [0] * self.num_batches
        #Closer to 0 means older
        num = 0.5
        for i in range(self.num_batches-1,-1,-1):
            vector[i] = num
            num = num - num * 0.2
        return vector

    def get_pond_vector_by_perc(self,actual_values):
        diference_vector = [0] * len(actual_values)
        for i in range(len(actual_values)):
            diference_vector[i] = abs(actual_values[i] - self._requirements.Inv_Politics[i])
            if(diference_vector[i] < 0.10):
                diference_vector[i] = 0
        return diference_vector
        

    def next_step(self):
        counters_vect = []
        pond_vector_by_batch = self.get_pond_vector_by_batch()
        for n_batch in range(len(self.batches_dict)):
            
            patterns = []
            for string in self.regex_list:
                patterns.append(re.compile(string))
            
            res = self.batches_dict[n_batch]

            #self._enviroment.historic_fires = ""

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
            if(n_batch == self.num_batches - 1):
                for i in range(len(counters)):
                    self._historic_counters[i].append(porcentual_count[i])

            pond_vector_by_perc = self.get_pond_vector_by_perc(porcentual_count)

            for i in range(len(porcentual_count)):
                if(porcentual_count[i] < self._requirements.Inv_Politics[i]):
                    for transition in self.tInvs[i]:
                        self._enviroment.cost_vector[transition-1] -= 1 * pond_vector_by_batch[n_batch] * pond_vector_by_perc[i]
                elif(porcentual_count[i] > self._requirements.Inv_Politics[i]):
                    for transition in self.tInvs[i]:
                        self._enviroment.cost_vector[transition-1] += 1 * pond_vector_by_batch[n_batch] * pond_vector_by_perc[i]
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
        
