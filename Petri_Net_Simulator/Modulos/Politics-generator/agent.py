import numpy as np

class Agent:
    
    def __init__(self, I, policy=None, discount_factor = 0.1, learning_rate = 0.1, ratio_explotacion = 0.9):

        # Creamos la tabla de politicas
        if policy is not None:
            self._policy_table = policy
        else:
          #  position = list(game.positions_space.shape)
          #  position.append(len(game.action_space))
           # self._q_table = np.zeros(position)
            self._policy_table = []
            '''
            for i in range(len(I)):
                row = [0] * len(I[0])
                self._policy_table.append(row)
            '''
        self.map_conflicts = {} 
        self.create_policy(I)
        self.discount_factor = discount_factor
        self.learning_rate = learning_rate
        self.ratio_explotacion = ratio_explotacion
        self.action_space = list(range(len(I[0])))

    def create_policy(self, Iminus):
        for i in range(len(Iminus)):
            con = 0
            list_t = []
            for j in range(len(Iminus[0])):
                if(Iminus[i][j] > 0):
                    con += 1
                    list_t.append(j)
                    #self._policy_table[i][j] = 1
            if(con > 1):
                row = [0] * len(Iminus[0])
                self._policy_table.append(row)
                self.map_conflicts["%d" %(i)] = len(self.map_conflicts)
                default_prob = 1.0 / len(list_t)
                for k in range(len(list_t)):
                    self._policy_table[self.map_conflicts["%d" %(i)]][list_t[k]] = default_prob



    
    def get_next_step(self, state, game):
        
        # Damos un paso aleatorio...
        next_step = np.random.choice(list(game.action_space))
        
        # o tomaremos el mejor paso...
        if np.random.uniform() <= self.ratio_explotacion:
            # tomar el maximo
            idx_action = np.random.choice(np.flatnonzero(
                    self._q_table[state[0],state[1],state[2]] == self._q_table[state[0],state[1],state[2]].max()
                ))
            next_step = list(game.action_space)[idx_action]

        return next_step
    '''
    # actualizamos las politicas con las recompensas obtenidas
    def update(self, game, old_state, action_taken, reward_action_taken, new_state, reached_end):
        idx_action_taken =list(game.action_space).index(action_taken)

        actual_q_value_options = self._q_table[old_state[0], old_state[1], old_state[2]]
        actual_q_value = actual_q_value_options[idx_action_taken]

        future_q_value_options = self._q_table[new_state[0], new_state[1], new_state[2]]
        future_max_q_value = reward_action_taken  +  self.discount_factor*future_q_value_options.max()
        if reached_end:
            future_max_q_value = reward_action_taken #maximum reward

        self._q_table[old_state[0], old_state[1], old_state[2], idx_action_taken] = actual_q_value + \
                                              self.learning_rate*(future_max_q_value -actual_q_value)
    '''
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