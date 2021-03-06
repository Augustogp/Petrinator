from numpy.core.numeric import NaN
from enviroment import Environment
import numpy as np
import math

class Agent:
    
    #t_selection_metod = 0 -> max value; t_selection_metod = 1 -> probabilities
    def __init__(self, I, enviroment, policy=None, discount_factor = 0.1, 
                learning_rate = 0.1, ratio_explotacion = 0.5, t_selection_metod = 0):

       # self.enviroment = enviroment
        # Creamos la tabla de politicas
        if policy is not None:
            self._policy_table = policy
        else:

            self._policy_table = []
            self._policy_table = enviroment.get_policy_table()
            self._conflicts = self.set_conflicts()
            '''
            for i in range(len(I)):
                row = [0] * len(I[0])
                self._policy_table.append(row)
            '''
        self.discount_factor = discount_factor
        self.t_selection_method = t_selection_metod
        self.learning_rate = learning_rate
        self.ratio_explotacion = ratio_explotacion
        self.action_space = list(range(len(I[0])))
        self.set_initial_state(enviroment)
        self._historic_rewards = []
        for i in range(len(self._policy_table[0])):
            self._historic_rewards.append([])

    def reset(self,enviroment):
        self._policy_table = enviroment.get_policy_table()
        self.set_initial_state(enviroment)
        self._historic_rewards = []
        for i in range(len(self._policy_table[0])):
            self._historic_rewards.append([])

    def set_conflicts(self):
        conflicts = {}
        for i in range(len(self._policy_table)):
            conflicts["%d" %(i)] = [i for i, x in enumerate(self._policy_table[i]) if x != 0]
        return conflicts

    def set_initial_state(self,enviroment):
        bool_conflict = enviroment.check_if_conflict(0)
        if(bool_conflict):
            self.state = enviroment.p_to_conflict(0)
        else:
            self.state = -1
    
    def get_next_step(self, enviroment):

        self.action_space = enviroment.getExt()
        found = 0
        t_in_conf = []
        vector_t = [i for i, x in enumerate(self.action_space) if x != 0]
        for i in vector_t:
            if(self.action_space[i] > 0):
                for j in range(len(self._policy_table)):
                    if(self._policy_table[j][i] != 0):
                       if i not in t_in_conf:
                            t_in_conf.append(i)

                       self.state = j
                       found = 1
                       
        # Damos un paso aleatorio...
        # next_step = np.random.choice(list(game.action_space))
        # Ya tenemos esto con lo de arriba 
        
        # o tomaremos el mejor paso...
        
        if found and np.random.uniform() >= self.ratio_explotacion:

            if self.t_selection_method == 0:
                idx_action = self.select_by_max_value(t_in_conf)
            else:
                idx_action = self.select_by_prob(t_in_conf)
        else:
            idx_action = np.random.choice(np.flatnonzero(self.action_space))

        return idx_action
        
    def select_by_max_value(self, t_in_conf):
        idx_conf_action = np.random.choice(t_in_conf)
        max_prob_transition = 0
        for i in range(len(self._conflicts)):
            if idx_conf_action in self._conflicts["%d" %(i)]:
                
                # Max Value
                enabled_conflict = self.action_space * self._policy_table[i]
                max_prob = max(enabled_conflict)
                if(max_prob > max_prob_transition):
                    max_prob_transition = max_prob
                    vector_choice = [i for i, x in enumerate(enabled_conflict) if x == max_prob]
                    idx_action = np.random.choice(vector_choice)
        return idx_action
    
    def select_by_prob(self,t_in_conf):
        idx_conf_action = np.random.choice(t_in_conf)
        dict_probs = {}
        conf_belongs = []
        for i in range(len(self._conflicts)):
            if idx_conf_action in self._conflicts["%d" %(i)]:
                conf_belongs.append(i)

        # Probabilities        
        conf_choice = np.random.choice(conf_belongs)
        enabled_conflict = self.action_space * self._policy_table[conf_choice]
        for t in range(len(self._policy_table[conf_choice])):
            if enabled_conflict[t] != 0:
                dict_probs[t] = self._policy_table[conf_choice][t]
        sum = np.sum(list(dict_probs.values()))
        for t in dict_probs.keys():
            dict_probs[t] = dict_probs[t] / sum
        idx_action = np.random.choice(list(dict_probs.keys()),p=list(dict_probs.values()))
        return idx_action
    
    # actualizamos las politicas con las recompensas obtenidas
    def update(self,old_state,action_taken,reward_action_taken):

        if(not self.checkIfNecesary(old_state,action_taken)):
            return

        vector_conflicts_with_t = self.get_rows_by_index_with_t_as_conf(action_taken)

        self._historic_rewards[action_taken].append(reward_action_taken)

        for conflict in vector_conflicts_with_t:

            actual_policy_value = self._policy_table[conflict][action_taken]

            aux_policy_values = self._policy_table[conflict].copy()

            loss = - math.log(actual_policy_value) * reward_action_taken


            new_policy_value = actual_policy_value - loss
            if(new_policy_value >= 1 or new_policy_value <= 0):
                continue
            self._policy_table[conflict][action_taken] = new_policy_value

            vector_non_selected = [i for i, x in enumerate(self._policy_table[conflict]) if x != 0]
            
            non_selected_count = len(vector_non_selected) - 1
            for i in vector_non_selected:
                if(i != action_taken):
                    self._policy_table[conflict][i] = self._policy_table[conflict][i] + loss / non_selected_count
                    if(self._policy_table[conflict][i] <= 0):
                        self._policy_table[conflict] = aux_policy_values
                        break
            #print("Probabilidades post cambio")
            #print(self._policy_table)


    def get_rows_by_index_with_t_as_conf(self,t):
        rows = []
        for row in range(len(self._policy_table)):
            if(self._policy_table[row][t] != 0):
                rows.append(row)
        return rows

    def checkIfNecesary(self,old_state,transition):
        if (self._policy_table[old_state][transition] != 0):
            return True
        else:
            return False

    def print_policy(self,enviroment):
        acum = 0
        places_in_conf = list(enviroment.map_p_to_conflicts.keys())
        print("     ",end="")
        for i in range(1,len(self._policy_table[0])+1):
            val = "T" + str(i)
            print("%6s" %(val), end = " ") 
        print()   
        for place in range(len(self._policy_table)):
            print(int(places_in_conf[place]) + 1,end = ": [ ")
            for transition in range(len(self._policy_table[0])):
                print("%6.3f" %(self._policy_table[place][transition]), end=" ")
            print("]")
        print("     ",end="")
        for i in range(len(self._policy_table[0])):
            print("%6d" %(enviroment.count_t_fires[i]), end=" ")
            acum += enviroment.count_t_fires[i]
        print("\nacum: %d " %(acum))
            
    def get_policy(self):
        return self._policy_table

    def get_places_with_conflicts(self):
        return self.map_p_to_conflicts.keys()

    def get_state(self):
        return self.state