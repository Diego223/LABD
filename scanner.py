from keys import *
from scannerFunctions import *
from AFD import *
from ExpressionTree import *
from regularExpression import *
import pickle 

lineas = []
    #Lectura de archivo a correr 
archivo = input("Ingrese el numero de archivo yal.run (1.1 | 1.2): ") 
archivo = "slr-" + archivo + ".yal.run"
with open ("tokens.bin", "rb") as f:
    tokenRules = pickle.load(f)
    tokensExp = pickle.load(f)

#Escaneamos archivo buscando tokens que coincidan con las reglas definidas.
with open(archivo, "r") as f:
    lineas = f.readlines()
finds = findAllpro(lineas, tokensExp)
llaves = []
for key, value in finds.items():
    for i in range(len(value)):
        if last(value[i]) == "U":
            llaves.append([key, value[i][0], "TOKEN UNRECOGNIZED", value[i][1], value[i][2]])
        for y in tokenRules.keys():
            if matches(value[i][0], y) and last(value[i]) == "I":
                llaves.append([key, value[i][0], tokenRules[y], value[i][1], value[i][2]])

print("\n\nllaves encontradas\n")
for x in llaves:
    print(x[2], " encontrado en la linea ", x[0])
    print("La llave es: ", x[1])
    print("Inicia en: ", x[3])
    print("Finaliza en: ", x[4], "\n\n")

llaves = [x for x in llaves if x[2] != "TOKEN UNRECOGNIZED"]
with open("read.bin", "wb") as f:
    pickle.dump(llaves, f)
