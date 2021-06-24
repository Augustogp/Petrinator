import numpy as np
import math

class Agent:
    
    def __init__(self, I, enviroment, policy=None, discount_factor = 0.1, learning_rate = 0.1, ratio_explotacion = 0.5):

       # self.enviroment = enviroment
        # Creamos la tabla de politicas
        if policy is not None:
            self._policy_table = policy
        else:
          #  position = list(game.positions_space.shape)
          #  position.append(len(game.action_space))
           # self._q_table = np.zeros(position)
            self._policy_table = []
            self._policy_table = enviroment.get_policy_table()
            '''
            for i in range(len(I)):
                row = [0] * len(I[0])
                self._policy_table.append(row)
            '''
        self.discount_factor = discount_factor
        self.learning_rate = learning_rate
        self.ratio_explotacion = ratio_explotacion
        self.action_space = list(range(len(I[0])))
        self.set_initial_state(enviroment)

    def set_initial_state(self,enviroment):
        bool_conflict = enviroment.check_if_conflict(0)
        if(bool_conflict):
            self.state = enviroment.p_to_conflict(0)
        else:
            self.state = -1
    
    def get_next_step(self, enviroment):

        self.action_space = enviroment.getExt()
        found = 0
        for i in range(len(self.action_space)):
            if(self.action_space[i] == 1 and found == 0):
                for j in range(len(self._policy_table)):
                    if(self._policy_table[j][i] != 0):
                       enabled_conflict = self.action_space * self._policy_table[j]
                       print("Conflicto habilitado")
                       print(enabled_conflict)
                       vector_choice = [i for i, x in enumerate(enabled_conflict) if x != 0]
                       idx_action = np.random.choice(vector_choice) 
                       #idx_action = np.random.choice(np.flatnonzero(self._policy_table[j]))
                       next_step = list(self._policy_table[j])[idx_action]
                       self.state = j
                       found = 1
                       break
        if(not found):
            print("No encontro conflicto")
            #If it didnt found any transition fireable thats in a conflict, it fires a random one
            idx_action = np.random.choice(np.flatnonzero(self.action_space))
            #next_step = list(self.action_space)[idx_action]
            return idx_action

        # Damos un paso aleatorio...
        # next_step = np.random.choice(list(game.action_space))
        # Ya tenemos esto con lo de arriba 
        
        # o tomaremos el mejor paso...
        if np.random.uniform() <= self.ratio_explotacion:

            enabled_conflict = self.action_space * self._policy_table[j]
            # tomar el maximo
            max_prob = max(enabled_conflict)
            
            vector_choice = [i for i, x in enumerate(enabled_conflict) if x == max_prob]
            '''
            idx_action = np.random.choice(np.flatnonzero(
                self._policy_table[self.state] == max(self._policy_table[self.state])
                ))
            '''
            idx_action = np.random.choice(vector_choice)
            #next_step = list(self._policy_table[self.state])[idx_action]
            print("Encontro conflicto")

        return idx_action
    
    # actualizamos las politicas con las recompensas obtenidas
    '''
    def update(self, enviroment, old_state, action_taken, reward_action_taken, new_state, reached_end):
        idx_action_taken =list(self.action_space).index(action_taken)

        actual_policy_values_options = self._policy_table[old_state]
        actual_policy_value = actual_policy_values_options[idx_action_taken]

        future_policy_value_options = self._q_table[new_state[0], new_state[1], new_state[2]]
        future_max_q_value = reward_action_taken  +  self.discount_factor*future_q_value_options.max()
        if reached_end:
            future_max_q_value = reward_action_taken #maximum reward

        self._q_table[old_state[0], old_state[1], old_state[2], idx_action_taken] = actual_q_value + \
                                              self.learning_rate*(future_max_q_value -actual_q_value)
    '''
    
    def update(self,old_state,action_taken,reward_action_taken):

        if(not self.checkIfNecesary(old_state,action_taken)):
            return

        actual_policy_value = self._policy_table[old_state][action_taken]

        #idx_action_taken =list(self._policy_table[old_state]).index(action_taken)
        print("Probabilidades pre cambio")
        print(self._policy_table)
        print("Probabilidad actual: %f" %(actual_policy_value))

       # actual_policy_values_options = self._policy_table[old_state]
       # actual_policy_value = actual_policy_values_options[idx_action_taken]
        loss = - math.log(actual_policy_value) * reward_action_taken
        print("Reward: %f" %(reward_action_taken))
        print("Loss: %f" %(loss))

        new_policy_value = actual_policy_value - loss
        if(new_policy_value >= 1 or new_policy_value <= 0):
            return
        self._policy_table[old_state][action_taken] = new_policy_value

        vector_non_selected = [i for i, x in enumerate(self._policy_table[self.state]) if x != 0]
        non_selected_count = len(vector_non_selected) - 1
        for i in vector_non_selected:
            if(i != action_taken):
                self._policy_table[old_state][i] = self._policy_table[old_state][i] + loss / non_selected_count
        print("Probabilidades post cambio")
        print(self._policy_table)
        '''
        for i in range(len(self._policy_table[old_state])):
            if beta == 0:
                if(i == action_taken):
                    self._policy_table[old_state][i] = self._policy_table[old_state][i] + 
        '''

    def checkIfNecesary(self,old_state,transition):
        if (self._policy_table[old_state][transition] != 0):
            return True
        else:
            return False

    def print_policy(self):
        for row in np.round(self._policy_table,1):
            for column in row:
                print('[', end='')
                for value in column:
                    print(str(value).zfill(5), end=' ')
                print('] ', end='')
            print('')
            
    def get_policy(self):
        return self._policy_table

    def get_places_with_conflicts(self):
        return self.map_p_to_conflicts.keys()

    def get_state(self):
        return self.state