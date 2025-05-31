from qiskit.quantum_info import Clifford, random_clifford 
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator 
from typing import List, Tuple, Dict 
from numpy import random
from benchmarker import Benchmarker


if __name__ == "__main__":
    NR_Q = 1
    DEPTH = 8
    SHOTS = 1024
    SEED = 42

    b = Benchmarker(nr_qbits=NR_Q, seed=SEED, depth=DEPTH, shots=SHOTS)
    print(b.run_benchmark())
