from numpy.core.fromnumeric import transpose
import numpy as np


class Environment:
    
    def __init__(self, I_minus, I_plus, Inhibition, Marking,cost_vector,use_w_not_inv = True):
        
        if(use_w_not_inv != None):
            self.use_w_not_inv = use_w_not_inv

        self.action_space = range(len(I_minus))
        
        self._step_penalization = 0

        self.marking = np.array(Marking)

        self._policy_table = []
        self.map_p_to_conflicts = {}
        self.create_policy(I_minus)
        
        self.state = [0] * len(self.map_p_to_conflicts)
        self.state = self.set_new_state()
        
        self.total_reward = 0

        self.inhibition_matrix = np.array(Inhibition)
        self.H_transposed = np.array(transpose(Inhibition))

        self.I_minus = np.array(I_minus)
        self.I_plus = np.array(I_plus)
        self.initial_marking = np.array(Marking)

        self.cost_vector = cost_vector
        self.mean_cost = 0
        self.historic_costs = []
        self.beta = 0
        
        self.createVarEcuExt()

        
        print("h:")
        print(self.H_transposed)
        #self.score = 0

    def reset(self):
        self.marking = self.initial_marking
                
    def createVarEcuExt(self):
        self.createQ()
        self.createB()
        self.createE()
        self.createExt()

    def createQ(self):
        self.Q = [0] * len(self.I_plus)
        for i in range(len(self.marking)):
            aux = 0
            if(self.marking[i] == 0):
                aux = 1
            self.Q[i] = aux

    def createB(self):
        self.B = np.dot(self.H_transposed,self.Q)
        self.fixB()
    
    def fixB(self):
        for t in range(len(self.B)):
            for p in range(len(self.marking)):
                if(self.H_transposed[t][p] > 0):
                    if(self.marking[p] > 0):
                        self.B[t] = 0
                        break
                else:
                    self.B[t] = 1
    
    def createE(self):
        self.E = np.array([0] * len(self.I_minus[0]))
        for i in range(len(self.E)):
            if(self.checkFireT(i)):
                self.E[i] = 1
            else:
                self.E[i] = 0
    
    def checkFireT(self,transition):
        test_mark = np.array([0] * len(self.marking))
        test_mark = self.marking - np.dot(self.I_minus,self.createFiringVector(transition))
        for i in range(len(test_mark)):
            if(test_mark[i] < 0):
                return False
        return True

    def createFiringVector(self,transition):
        sigma = np.array([0] * len(self.I_minus[0]))
        sigma[transition] = 1
        return sigma

    def createExt(self):
        self.Ext = np.logical_and(self.E,self.B)
        self.Ext = self.Ext.astype(int)
        print("Print Ext")
        print(self.Ext)

    def fireNet(self,transition):
        print("Se dispara %d" %(transition))
        fireVector = self.createFiringVector(transition)
        self.marking = self.marking - np.dot(self.I_minus,fireVector)
        self.marking = self.marking + np.dot(self.I_plus,fireVector)
        self.createVarEcuExt()
        return self.updateCost(transition)

    def updateCost(self,transition):
        if((not self.use_w_not_inv) and (not self.check_if_t_is_in_conf(transition))):
            return 0
        self.historic_costs.append(self.cost_vector[transition])
        reward = (self.cost_vector[transition] - self.mean_cost) / 100
        self.mean_cost = self.mean_cost + (self.cost_vector[transition] - self.mean_cost) / len(self.historic_costs)
        beta = int(not(self.cost_vector[transition] < self.mean_cost))
        return reward

    def check_if_t_is_in_conf(self,transition):
        for i in range(len(self._policy_table)):
            if(self._policy_table[i][transition] != 0):
                return True
        return False
                

    def step(self,transition):
        self.fireNet(transition)
        #Metemos las n expresiones regulares, una por cada t inv

    def getExt(self):
        return self.Ext

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
                self.map_p_to_conflicts["%d" %(i)] = len(self.map_p_to_conflicts)
                default_prob = 1.0 / len(list_t)
                for k in range(len(list_t)):
                    self._policy_table[self.map_p_to_conflicts["%d" %(i)]][list_t[k]] = default_prob

    def check_if_conflict(self,place):
        outs = np.flatnonzero(self.I_minus[place])
        return (1 < len(outs)) 
    
    def p_to_conflict(self,place):
        return self.map_p_to_conflicts["%d" %(place)]

    def set_new_state(self):
        p_with_conf = list(self.map_p_to_conflicts.keys())
        j = 0
        for i in p_with_conf:
            print("j: %d e i: %s" %(j,i) )
            self.state[j] = self.marking[int(i)]
            j += 1

    def get_policy_table(self):
        return self._policy_table
        
    '''
    def reset(self):
        self.total_reward = 0
        self.state = [0,0,0]
        self.lives = self.max_life
        self.score = 0
        self.x = randint(int(self.width_px/2), self.width_px) 
        self.y = randint(0, self.height_px-10)
        return self.state

    def step(self, action, animate=False):
        self._apply_action(action, animate)
        done = self.lives <=0 # final
        reward = self.score
        reward += self._step_penalization
        self.total_reward += reward
        return self.state, reward , done

    def _apply_action(self, action, animate=False):
        
        if action == "Arriba":
            self.player1 += abs(self.dy)
        elif action == "Abajo":
            self.player1 -= abs(self.dy)
            
        self.avanza_player()

        self.avanza_frame()

        if animate:
            clear_output(wait=True);
            fig = self.dibujar_frame()
            plt.show()

        self.state = (floor(self.player1/abs(self.dy))-2, floor(self.y/abs(self.dy))-2, floor(self.x/abs(self.dx))-2)
    '''