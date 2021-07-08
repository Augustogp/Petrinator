import numpy as np
import os 
import json
import socket
import sys
import traceback
import random
from agent import Agent
from enviroment import Environment
import action

#socket
host = "127.0.0.1"
port = int(sys.argv[1])
socket_cli =  socket.socket()
socket_cli.connect((host, port))

json_matrices2 = str(sys.argv[2])

json_traces = str(sys.argv[3])

defaultLogPath = os.path.expanduser("~") + r"\logs\transitions.txt"
currentDirectory = os.getcwd()
matrix_structure_files = currentDirectory.rsplit("\\",3)[0]

def main():

    print("Estoy en python")
    
    print("json_matrices2 " + json_matrices2)

    print("json type " + str(type(json_matrices2)))

    #json_matrices = open(matrix_structure_files + "\\matrices.json","r")
  #  print("Json bien hecho " + json_matrices.read())
    matrices = json.loads(json_matrices2)
    matrix_i = matrices["Incidencia"]
    print("Matriz Incidencia")
    print(matrix_i)
    matrix_i_plus = matrices["I+"]
    print("Matriz I +")
    print(matrix_i_plus)
    matrix_i_minus = matrices["I-"]
    print("Matriz I -")
    print(matrix_i_minus)
    matrix_inhibition = matrices["Inhibicion"]
    print("Matriz Inhibicion")
    print(matrix_inhibition)
    marking = matrices["Marcado"]
    print("Marcado")
    print(marking)
    tInvTraces = json.loads(json_traces)
    num_transitions = len(matrix_i[0])
    
    transitions_weight = {}
    for i in range(1,num_transitions+1):
        transitions_weight["T%d" %(i)] = random.randint(0,10)
    print(transitions_weight)
    
    '''
    transitions_weight["T1"] = 2
    transitions_weight["T2"] = 2
    transitions_weight["T3"] = 2
    transitions_weight["T4"] = 2
    transitions_weight["T5"] = 2
    transitions_weight["T6"] = 0
    transitions_weight["T7"] = 1
    transitions_weight["T8"] = 1
    transitions_weight["T9"] = 1
    transitions_weight["T10"] = 1
    transitions_weight["T11"] = 1
    transitions_weight["T12"] = 0
    
    transitions_weight["T13"] = 2
    transitions_weight["T14"] = 0
    '''
    
    transitions_weight["T1"] = 0
    transitions_weight["T2"] = 2
    transitions_weight["T3"] = 2
    transitions_weight["T4"] = 1
    transitions_weight["T5"] = 2
    transitions_weight["T6"] = 1
    transitions_weight["T7"] = 1
    transitions_weight["T8"] = 2
    transitions_weight["T9"] = 1
    transitions_weight["T10"] = 2
    transitions_weight["T11"] = 0
    transitions_weight["T12"] = 1
    transitions_weight["T13"] = 3
    transitions_weight["T14"] = 1
    transitions_weight["T15"] = 1
    transitions_weight["T16"] = 3
    transitions_weight["T17"] = 2
    transitions_weight["T18"] = 2
    transitions_weight["T19"] = 2
    transitions_weight["T20"] = 0
    
    print(tInvTraces)
    tinv_weights = {}
    for key in tInvTraces:
       tinv_weights[key] = 0
    for key in tinv_weights:
        for i in range(1,num_transitions+1):
            if i in tInvTraces[key]:
                tinv_weights[key] += transitions_weight["T%d" %(i)]
    print(tinv_weights)

    enviroment = Environment(matrix_i_minus,matrix_i_plus,matrix_inhibition,marking,list(transitions_weight.values()),use_w_not_inv=False)
    agent = Agent(matrix_i_minus,enviroment,ratio_explotacion=0.3)
    #agent.print_policy()
    print("Policies:")
    print(agent.get_policy())
    print("Action space:")
    print(agent.action_space)
    print(enviroment.map_p_to_conflicts)

    action.action(agent,enviroment)
    print("Pesos transiciones")
    print(transitions_weight)
    print("Policies:")
    agent.print_policy(enviroment)
    

    
main()
