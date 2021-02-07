
#initialization
import matplotlib.pyplot as plt
import numpy as np

# importing Qiskit
from qiskit import IBMQ, Aer
from qiskit.providers.ibmq import least_busy
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute

# import basic plot tools
from qiskit.tools.visualization import plot_histogram


'''Solving "lights out" with Grover's alg. Search space: 2^9'''
'''Solve within 28 qubits'''

lights = [0,1,1,1,0,0,1,1,1] #starting pattern

def oracle(circuit, space_register, aux_register, one): #answer also a 9-array. Naive solution. Assumption: 1 is no light, 0 is light

    circuit.cx(space_register[0], aux_register[0])
    circuit.cx(space_register[0], aux_register[1])
    circuit.cx(space_register[0], aux_register[3])

    circuit.cx(space_register[1], aux_register[0])
    circuit.cx(space_register[1], aux_register[1])
    circuit.cx(space_register[1], aux_register[2])
    circuit.cx(space_register[1], aux_register[4])

    circuit.cx(space_register[2], aux_register[1])
    circuit.cx(space_register[2], aux_register[2])
    circuit.cx(space_register[2], aux_register[5])

    circuit.cx(space_register[3], aux_register[0])
    circuit.cx(space_register[3], aux_register[3])
    circuit.cx(space_register[3], aux_register[4])
    circuit.cx(space_register[3], aux_register[6])

    circuit.cx(space_register[4], aux_register[1])
    circuit.cx(space_register[4], aux_register[3])
    circuit.cx(space_register[4], aux_register[4])
    circuit.cx(space_register[4], aux_register[5])
    circuit.cx(space_register[4], aux_register[7])

    circuit.cx(space_register[5], aux_register[2])
    circuit.cx(space_register[5], aux_register[4])
    circuit.cx(space_register[5], aux_register[5])
    circuit.cx(space_register[5], aux_register[8])

    circuit.cx(space_register[6], aux_register[3])
    circuit.cx(space_register[6], aux_register[6])
    circuit.cx(space_register[6], aux_register[7])

    circuit.cx(space_register[7], aux_register[4])
    circuit.cx(space_register[7], aux_register[6])
    circuit.cx(space_register[7], aux_register[7])
    circuit.cx(space_register[7], aux_register[8])

    circuit.cx(space_register[8], aux_register[5])
    circuit.cx(space_register[8], aux_register[7])
    circuit.cx(space_register[8], aux_register[8])
    #And everything.
    circuit.ccx(aux_register[0],aux_register[1],aux_register[9])
    circuit.ccx(aux_register[2],aux_register[9],aux_register[10])
    circuit.ccx(aux_register[3],aux_register[10],aux_register[11])
    circuit.ccx(aux_register[4],aux_register[11],aux_register[12])
    circuit.ccx(aux_register[5],aux_register[12],aux_register[13])
    circuit.ccx(aux_register[6],aux_register[13],aux_register[14])
    circuit.ccx(aux_register[7],aux_register[14],aux_register[15])
    circuit.ccx(aux_register[8],aux_register[15],aux_register[16])


    circuit.cz(aux_register[16], one[0])

    #Uncompute
    circuit.ccx(aux_register[8], aux_register[15], aux_register[16])
    circuit.ccx(aux_register[7], aux_register[14], aux_register[15])
    circuit.ccx(aux_register[6], aux_register[13], aux_register[14])
    circuit.ccx(aux_register[5], aux_register[12], aux_register[13])
    circuit.ccx(aux_register[4], aux_register[11], aux_register[12])
    circuit.ccx(aux_register[3], aux_register[10], aux_register[11])
    circuit.ccx(aux_register[2], aux_register[9], aux_register[10])
    circuit.ccx(aux_register[0], aux_register[1], aux_register[9])
    #order here shouldnt matter
    circuit.cx(space_register[0], aux_register[0])
    circuit.cx(space_register[0], aux_register[1])
    circuit.cx(space_register[0], aux_register[3])

    circuit.cx(space_register[1], aux_register[0])
    circuit.cx(space_register[1], aux_register[1])
    circuit.cx(space_register[1], aux_register[2])
    circuit.cx(space_register[1], aux_register[4])

    circuit.cx(space_register[2], aux_register[1])
    circuit.cx(space_register[2], aux_register[2])
    circuit.cx(space_register[2], aux_register[5])

    circuit.cx(space_register[3], aux_register[0])
    circuit.cx(space_register[3], aux_register[3])
    circuit.cx(space_register[3], aux_register[4])
    circuit.cx(space_register[3], aux_register[6])

    circuit.cx(space_register[4], aux_register[1])
    circuit.cx(space_register[4], aux_register[3])
    circuit.cx(space_register[4], aux_register[4])
    circuit.cx(space_register[4], aux_register[5])
    circuit.cx(space_register[4], aux_register[7])

    circuit.cx(space_register[5], aux_register[2])
    circuit.cx(space_register[5], aux_register[4])
    circuit.cx(space_register[5], aux_register[5])
    circuit.cx(space_register[5], aux_register[8])

    circuit.cx(space_register[6], aux_register[3])
    circuit.cx(space_register[6], aux_register[6])
    circuit.cx(space_register[6], aux_register[7])

    circuit.cx(space_register[7], aux_register[4])
    circuit.cx(space_register[7], aux_register[6])
    circuit.cx(space_register[7], aux_register[7])
    circuit.cx(space_register[7], aux_register[8])

    circuit.cx(space_register[8], aux_register[5])
    circuit.cx(space_register[8], aux_register[7])
    circuit.cx(space_register[8], aux_register[8])

def OR(circuit, qub1, qub2, qub3):
    circuit.cx(qub1, qub3)
    circuit.cx(qub2, qub3)
    circuit.ccx(qub1, qub2, qub3)

def UNOR(circuit, qub1, qub2, qub3):
    circuit.ccx(qub1, qub2, qub3)
    circuit.cx(qub2, qub3)
    circuit.cx(qub1, qub3)

def invert_about_avg(circuit, register, aux_reg, one):#aux are purely ancillary here, starting at [9] cuz the rest are for lights
    #Naive implementation, might improve later
    #OR Across all gates in reg (save in aux 9),
    circuit.h(register)

    OR(circuit, register[0], register[1], aux_reg[9])
    OR(circuit, register[2], aux_reg[9], aux_reg[10])
    OR(circuit, register[3], aux_reg[10], aux_reg[11])
    OR(circuit, register[4], aux_reg[11], aux_reg[12])
    OR(circuit, register[5], aux_reg[12], aux_reg[13])
    OR(circuit, register[6], aux_reg[13], aux_reg[14])
    OR(circuit, register[7], aux_reg[14], aux_reg[15])
    OR(circuit, register[8], aux_reg[15], aux_reg[16])

    circuit.cz(aux_reg[16], one[0])
    #Uncompute ORs

    UNOR(circuit, register[8], aux_reg[15], aux_reg[16])
    UNOR(circuit, register[7], aux_reg[14], aux_reg[15])
    UNOR(circuit, register[6], aux_reg[13], aux_reg[14])
    UNOR(circuit, register[5], aux_reg[12], aux_reg[13])
    UNOR(circuit, register[4], aux_reg[11], aux_reg[12])
    UNOR(circuit, register[3], aux_reg[10], aux_reg[11])
    UNOR(circuit, register[2], aux_reg[9], aux_reg[10])
    UNOR(circuit, register[0], register[1], aux_reg[9])


    circuit.h(register)


def week2a_ans_func(arr):

    space_reg = QuantumRegister(9)

    aux_reg = QuantumRegister(17)

    one_qubit = QuantumRegister(1)

    classical_reg = ClassicalRegister(9)

    qc = QuantumCircuit(space_reg, aux_reg, one_qubit, classical_reg)

    qc.x(one_qubit)
    #Initialize the aux_reg to lights layout
    for i in range (0,9):
        if not arr[i]:
            qc.x(aux_reg[i])
            print (i)

    #hadamard on the space_reg
    qc.h(space_reg)

    #Repeat computation about 15/20 times
    for i in range(0, 15):
        oracle(qc, space_reg, aux_reg, one_qubit)
        invert_about_avg(qc, space_reg, aux_reg, one_qubit)

    #measure space_reg
    qc.measure(space_reg, classical_reg)
    qc = qc.reverse_bits()

    #uncompute aux_reg
    for i in range (0,9):
        if not arr[i]:
            qc.x(aux_reg[i])

    return qc

qcir = week2a_ans_func(lights)

backend = Aer.get_backend('qasm_simulator')

shots = 1024
job_exp = execute(qcir, backend=backend, shots=shots)

results = job_exp.result()
answer = results.get_counts(qcir)

print(answer)

maxx = 0
max_thing = ""
for i in answer:
    if answer[i] > maxx:
        maxx = answer[i]
        max_thing = i
print(max_thing)
print(maxx)
'''Result: 110010101 correct answer. Hit rate 984/1024 = 96% accuracy'''