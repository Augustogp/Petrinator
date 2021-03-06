import re
from requirements import Requirements
import matplotlib.pyplot as plt
import numpy as np
import math
from sklearn.metrics import mean_squared_error


class Enviroment_Supervisor:

    def __init__(self,TInv,enviroment,cost_manager,requirements,agent,batch,n_batch_graph=5,num_batches=5,alpha=0.1
                ,initial_step=0.1,discount_factor=0.3,confidence_interval=0.05):
        self._enviroment = enviroment
        self.batch = batch
        self.cost_manager = cost_manager
        self.num_batches = num_batches
        self._requirements = requirements
        self.tInvs = list(TInv.values())
        self.createRegEx(TInv)
        self.agent = agent
        self.n_batch_graph = n_batch_graph
        self.alpha = alpha
        self.initial_step = initial_step
        self.discount_factor = discount_factor
        self.confidence_interval = confidence_interval
        self.reset()


    def reset(self):
        self.batches_dict = {}
        self._historic_counters = []
        self._historic_counters_prom = []      
        for _ in range(len(self.tInvs)):
            self._historic_counters.append([])
            self._historic_counters_prom.append([])
        self.counters_historical_prob = self.create_dictionary_hisotrical_porb()
        self.patterns = []
        for string in self.regex_list:
            self.patterns.append(re.compile(string))
        
        


    def new_batch(self):
        #new_batch = self._enviroment.historic_fires
        new_batch = self._enviroment.cost_manager.inv_counters
        self._enviroment.historic_fires = ""
        for inv in range(len(self._enviroment.cost_manager.inv_counters)):
            self._enviroment.cost_manager.inv_counters_acum[inv] += self._enviroment.cost_manager.inv_counters[inv]         
        self._enviroment.cost_manager.inv_counters = [0] * len(self.regex_list)
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
        num = self.initial_step
        
        for i in range(self.num_batches-1,-1,-1):
            vector[i] = num
            num = num - num * self.discount_factor
        '''
        for i in range(self.num_batches):
            vector[i] = num
            num = num - num * 0.5
        '''
        return vector

    def get_pond_vector_by_perc(self,actual_values):
        diference_vector = [0] * len(actual_values)
        for i in range(len(actual_values)):
            difference = abs(actual_values[i] - self._requirements.Inv_Politics[i])
            if(difference < self.confidence_interval):
                diference_vector[i] = 0
                continue
            else: 
                diference_vector[i] = 1 - math.pow(math.e,(-self.alpha * difference))
            
        return diference_vector
        

    def next_step(self):
        counters_acum = [0] * len(self.regex_list)
        pond_vector_by_batch = self.get_pond_vector_by_batch()
        for n_batch in range(len(self.batches_dict)):

        
            #print("Contadores batch %d" %(n_batch))
            #print(counters)
            porcentual_count = [x / sum(self.batches_dict[n_batch]) for x in self.batches_dict[n_batch]]
            if((self.n_batch_graph - len(self.batches_dict) + n_batch) >= 0):
                counters_acum = np.add(counters_acum,porcentual_count)

            if(n_batch == self.num_batches - 1):
                for i in range(len(self.batches_dict[n_batch])):
                    self._historic_counters[i].append(porcentual_count[i])

            
            pond_vector_by_perc = self.get_pond_vector_by_perc(porcentual_count)

            for i in range(len(porcentual_count)):
                if(porcentual_count[i] < self._requirements.Inv_Politics[i]):
                    for transition in self.tInvs[i]:
                        self.cost_manager.cost_vector[transition-1] -= 1 * pond_vector_by_batch[n_batch] * pond_vector_by_perc[i]
                elif(porcentual_count[i] > self._requirements.Inv_Politics[i]):
                    for transition in self.tInvs[i]:
                        self.cost_manager.cost_vector[transition-1] += 1 * pond_vector_by_batch[n_batch] * pond_vector_by_perc[i]
            #print("Vector costos despues: ")
            #print(self._enviroment.cost_vector)
        for i in range(len(self.regex_list)):
            self._historic_counters_prom[i].append(counters_acum[i]/self.n_batch_graph)

        self._enviroment.cost_manager.inv_counters = [0] * len(self.regex_list)
        # print("Cost vector: ")
        # print(self.cost_manager.cost_vector)
        list_places = list(self.counters_historical_prob.keys())
        for index_row_policy_table in range (len(self.agent._policy_table)): #  [  0.500  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.500  0.000  0.000  0.000  0.000  0.000 ]
            key_place_conflict = list_places[index_row_policy_table]
            vector_transition_conflict = [i for i, x in enumerate(self.agent._policy_table[index_row_policy_table]) if x != 0]
            for index_probability in range(len(vector_transition_conflict)): # [5.0, 5.0] SON INDICES LPM [0, 8]
                self.counters_historical_prob[key_place_conflict] [index_probability].append(self.agent._policy_table[index_row_policy_table][ vector_transition_conflict[index_probability] ])



    def get_linear_regression_param(self,invariant):
        m, b = np.polyfit(range(len(self._historic_counters_prom[invariant])), self._historic_counters_prom[invariant], 1)
        return m, b

    def print_total_fire_proportions(self):
        n_plots = len(self._historic_counters)
        fig, ax = plt.subplots(n_plots)
        for invariant in range(n_plots):
            #ax[invariant].scatter(x = range(len(self._historic_counters[invariant])), y = self._historic_counters[invariant],color='c')
            ax[invariant].axhline(y=self._requirements.Inv_Politics[invariant], color='r', linestyle='-')
            #ax[invariant].plot(range(len(self._historic_counters[invariant])),self._historic_counters[invariant],color='c')
            m, b = self.get_linear_regression_param(invariant)
            ax[invariant].plot(range(len(self._historic_counters_prom[invariant])), m*range(len(self._historic_counters_prom[invariant])) + b,color='k')
            ax[invariant].scatter(x = range(len(self._historic_counters_prom[invariant])), y = self._historic_counters_prom[invariant],color='g')
            ax[invariant].plot(range(len(self._historic_counters_prom[invariant])),self._historic_counters_prom[invariant],color='g')
            vector_true = np.full(len(self._historic_counters_prom[invariant]),self._requirements.Inv_Politics[invariant])
            rmse=math.sqrt(mean_squared_error(vector_true,self._historic_counters_prom[invariant]))
            len_4 = int(len(vector_true)/4)
            rmse_4 = math.sqrt(mean_squared_error(vector_true[-len_4:],self._historic_counters_prom[invariant][-len_4:]))
            ax[invariant].set_title("RMSE: " + str(rmse) + "  RMSE last quarter: " + str(rmse_4))
            print("Invariante " + str(invariant))
            print("Pendiente: " + str(m))
            print("Ordenada: " + str(b))
            print("RMSE: " + str(rmse))
        plt.show()
        plt.close()

        

    def create_dictionary_hisotrical_porb(self):
        counters_historical_prob = dict.fromkeys(self._enviroment.map_p_to_conflicts.keys())  # Create dictionary example: {place_1:None, place_18:None...}
        list_places = list(counters_historical_prob.keys())
        for index_place in range(len(counters_historical_prob)):
            key = list_places[index_place]
            vector_transition_conflict = [i for i, x in enumerate(self.agent._policy_table[index_place]) if x != 0]
            counters_historical_prob[key] = self.create_matrix_inv(len(vector_transition_conflict))
        return counters_historical_prob
    
    def create_matrix_inv(self, row):
        matrix_counters_inv = []
        for i in range(row):
            matrix_counters_inv.append([])
        return matrix_counters_inv

    def print_probability(self):
        list_places_conflict = list(self.counters_historical_prob.keys())
        size_prob = len(self.counters_historical_prob[list_places_conflict[0]][0])
        list_colours = ['-r','-b','-y','-g','-c','-m']
        fig, ax = plt.subplots(len(list_places_conflict),figsize=(10.0,10.0))
        for place_conflict_indx in range (len(list_places_conflict)):
            row_place_conflict = list_places_conflict[place_conflict_indx]
            vector_transition_conflict = [i for i, x in enumerate(self.agent._policy_table[place_conflict_indx]) if x != 0]
            for transition_conflict in range(len(self.counters_historical_prob[row_place_conflict])):
                #ax[place_conflict_indx].scatter(x = range(size_prob), y = self.counters_historical_prob[row_place_conflict][transition_conflict], color='r')
                ax[place_conflict_indx].plot(range(size_prob), self.counters_historical_prob[row_place_conflict][transition_conflict], list_colours[transition_conflict],
                                             label= "T"+ str(1 + vector_transition_conflict[transition_conflict]))
                ax[place_conflict_indx].legend(loc="upper left")