import numpy as np
import matplotlib.pyplot as plt
import math
from sklearn.metrics import mean_squared_error



def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

def action(learner, enviroment, enviroment_supervisor, max_iterations = 3000, rounds=1, discount_factor = 0.1, learning_rate = 0.1,
         ratio_explotacion=0.9):
        
    historic_counters_acum = []
    historic_counters_prom = []
    for _ in range(len(enviroment_supervisor.tInvs)):
            historic_counters_acum.append([])
            historic_counters_prom.append([])
    m_acum = [0] * len(enviroment_supervisor.tInvs)
    b_acum = [0] * len(enviroment_supervisor.tInvs)
    m_prom = [0] * len(enviroment_supervisor.tInvs)
    b_prom = [0] * len(enviroment_supervisor.tInvs)


    for cicle in range(0, rounds):
        enviroment.reset()
        learner.reset(enviroment)
        enviroment_supervisor.reset()
        #state = learner.get_state()
        reward, done = None, None
        
        itera=0
        while (done != True) and (itera < max_iterations):
            next_action = learner.get_next_step(enviroment)
            old_state = learner.get_state()
            reward = enviroment.fireNet(next_action)
            if itera > 1 and old_state != -1:
                learner.update(old_state, next_action, reward)
                if is_integer(float(itera)/enviroment_supervisor.batch):
                    enviroment_supervisor.new_batch()
                    #learner.print_policy(enviroment)
            itera+=1
        if cicle == 0:
            for invariant in range(len(enviroment_supervisor._historic_counters)):
                historic_counters_acum[invariant] = [0] *len(enviroment_supervisor._historic_counters_prom[invariant])
        for invariant in range(len(enviroment_supervisor._historic_counters)):
            historic_counters_acum[invariant] = np.add(historic_counters_acum[invariant],enviroment_supervisor._historic_counters_prom[invariant])
            m, b = enviroment_supervisor.get_linear_regression_param(invariant)
            print("M[%d] in cicle %d is: %f" %(invariant,cicle,m))
            print("B[%d] in cicle %d is: %f" %(invariant,cicle,b))
            m_acum[invariant] += m
            b_acum[invariant] += b

    for invariant in range(len(enviroment_supervisor._historic_counters)):
        historic_counters_prom[invariant] = np.divide(historic_counters_acum[invariant], rounds)
        m_prom[invariant] = m_acum[invariant] / rounds
        b_prom[invariant] = b_acum[invariant] / rounds

    n_plots = len(enviroment_supervisor._historic_counters)
    fig, ax = plt.subplots(n_plots)
    for invariant in range(n_plots):
        ax[invariant].axhline(y=enviroment_supervisor._requirements.Inv_Politics[invariant], color='r', linestyle='-')
        ax[invariant].plot(range(len(historic_counters_prom[invariant])), m_prom[invariant]*range(len(historic_counters_prom[invariant])) + b_prom[invariant],color='k')
        ax[invariant].scatter(x = range(len(historic_counters_prom[invariant])), y = historic_counters_prom[invariant],color='g')
        ax[invariant].plot(range(len(historic_counters_prom[invariant])),historic_counters_prom[invariant],color='g')
        vector_true = np.full(len(historic_counters_prom[invariant]),enviroment_supervisor._requirements.Inv_Politics[invariant])
        rmse=math.sqrt(mean_squared_error(vector_true,historic_counters_prom[invariant]))
        string_pendiente = "{:.2e}".format(m_prom[invariant])
        ax[invariant].set_title("RMSE: %.5f    Ordenada: %.3f   Pendiente: %s " %(rmse,b_prom[invariant],string_pendiente))
        print("Invariante " + str(invariant))
        print("Pendiente: " + str(m_prom[invariant]))
        print("Ordenada: " + str(b_prom[invariant]))
        print("RMSE: " + str(rmse))
    plt.show()
    plt.close()

        
    
    
    return learner, enviroment