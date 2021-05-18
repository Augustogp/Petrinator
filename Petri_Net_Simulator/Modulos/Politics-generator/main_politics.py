import numpy as np
import os 
import json
import socket
import sys

#socket
host = "127.0.0.1"
port = int(sys.argv[1])
socket_cli =  socket.socket()
socket_cli.connect((host, port))

traces_log2 = sys.argv[2]

defaultLogPath = os.path.expanduser("~") + r"\logs\transitions.txt"
currentDirectory = os.getcwd()
matrix_structure_files = currentDirectory.rsplit("\\",3)[0]

def main():
    traces_log = open(defaultLogPath,"r")
    print(defaultLogPath)
    print(traces_log.read())
    traces_log.close()

    salida = open("salida_python.txt","w")
    salida.write(traces_log2)
    salida.close()
    
    json_matrices = open(matrix_structure_files + "\\matrices.json","r")
    matrices = json.loads(json_matrices.read())
    matrix_i = matrices["Incidencia"]
    print(matrix_i)
    matrix_i_plus = matrices["I+"]
    print(matrix_i_plus)
    matrix_i_minus = matrices["I-"]
    print(matrix_i_minus)
    matrix_inhibition = matrices["Inhibicion"]
    print(matrix_inhibition)
    
    
main()
