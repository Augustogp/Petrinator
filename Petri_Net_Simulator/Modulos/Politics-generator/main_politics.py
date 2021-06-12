import numpy as np
import os 
import json
import socket
import sys
import traceback
import random
from agent import Agent

#socket
host = "127.0.0.1"
port = int(sys.argv[1])
socket_cli =  socket.socket()
socket_cli.connect((host, port))

traces_log2 = sys.argv[2]

json_matrices2 = str(sys.argv[3])

json_traces = str(sys.argv[4])

defaultLogPath = os.path.expanduser("~") + r"\logs\transitions.txt"
currentDirectory = os.getcwd()
matrix_structure_files = currentDirectory.rsplit("\\",3)[0]

def main():

    print("Estoy en python")
    
    print("traces_string " + traces_log2)
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
    tInvTraces = json.loads(json_traces)
    num_transitions = len(matrix_i[0])
    
    transitions_weight = {}
    for i in range(1,num_transitions+1):
        transitions_weight["T%d" %(i)] = random.randint(0,10)
    print(transitions_weight)
    
    print(tInvTraces)
    tinv_weights = {}
    for key in tInvTraces:
       tinv_weights[key] = 0
    for key in tinv_weights:
        for i in range(1,num_transitions+1):
            if i in tInvTraces[key]:
                tinv_weights[key] += transitions_weight["T%d" %(i)]
    print(tinv_weights)

    agent = Agent(matrix_i_minus)
    print(agent.get_policy())

    

    
main()
