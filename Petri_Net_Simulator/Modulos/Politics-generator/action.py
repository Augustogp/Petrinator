import numpy as np

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

def action(learner, enviroment, enviroment_supervisor, max_iterations = 3000, rounds=1, discount_factor = 0.1, learning_rate = 0.1,
         ratio_explotacion=0.9):
        
    
    max_points= -9999
    first_max_reached = 0
    total_rw=0
    steps=[]

    for cicle in range(0, rounds):
        enviroment.reset()
        #state = learner.get_state()
        reward, done = None, None
        
        itera=0
        while (done != True) and (itera < max_iterations):
            next_action = learner.get_next_step(enviroment)
            old_state = learner.get_state()
            reward = enviroment.fireNet(next_action)
            if itera > 1 and old_state != -1:
                learner.update(old_state, next_action, reward)
                if is_integer(float(itera)/enviroment_supervisor.step):
                    enviroment_supervisor.next_step()
            itera+=1
        
        steps.append(itera)
        '''
        total_rw+=game.total_reward
        if game.total_reward > max_points:
            max_points=game.total_reward
            first_max_reached = cicle
        
        if cicle %500==0 and cicle >1 and not animate:
            print("-- Partidas[", cicle, "] Avg.Puntos[", int(total_rw/cicle),"]  AVG Steps[", int(np.array(steps).mean()), "] Max Score[", max_points,"]")
                
    if cicle>1:
        print('Partidas[',cicle,'] Avg.Puntos[',int(total_rw/cicle),'] Max score[', max_points,'] en partida[',first_max_reached,']')
        '''
    #learner.print_policy()
    
    return learner, enviroment