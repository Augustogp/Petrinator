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
from enviroment_supervisor import Enviroment_Supervisor



defaultLogPath = os.path.expanduser("~") + r"\logs\transitions.txt"
currentDirectory = os.getcwd()
matrix_structure_files = currentDirectory.rsplit("\\",3)[0]

def main():

    print("Estoy en python")

    json_matrices = open(matrix_structure_files + "\\matrices.json","r")
  #  print("Json bien hecho " + json_matrices.read())
    matrices = json.loads(json_matrices.read())
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
    num_transitions = len(matrix_i[0])

    tInvTraces = {"TInv1":[0,1,3,5],"TInv2":[0,2,4,5],"TInv3":[6,7,8,9]}

    
    transitions_weight = {}
    for i in range(1,num_transitions+1):
        transitions_weight["T%d" %(i)] = random.randint(0,10)
    

    enviroment = Environment(matrix_i_minus,matrix_i_plus,matrix_inhibition,marking,list(transitions_weight.values()),use_w_not_inv=False)
    agent = Agent(matrix_i_minus,enviroment,ratio_explotacion=0.3)
    #agent.print_policy()
    print("Policies:")
    print(agent.get_policy())
    print("Action space:")
    print(agent.action_space)
    print(enviroment.map_p_to_conflicts)    
    
    enviroment_supervisor = Enviroment_Supervisor(tInvTraces,enviroment,500)


    action.action(agent,enviroment,enviroment_supervisor)
    print("Pesos transiciones")
    print(transitions_weight)
    print("Policies:")
    agent.print_policy(enviroment)

    
main()