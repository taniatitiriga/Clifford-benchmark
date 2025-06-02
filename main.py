from qiskit.quantum_info import Clifford, random_clifford 
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator 
from qiskit_aer.noise import NoiseModel, ReadoutError
from typing import List, Tuple, Dict 
from numpy import random
from benchmarker import Benchmarker


if __name__ == "__main__":
    NR_Q = 1
    DEPTH = 2
    SHOTS = 2048
    SEED = 42
    
    noise_model = NoiseModel()
    readout_err = ReadoutError([[0.98, 0.02],
                            [0.02, 0.98]])

    noise_model.add_readout_error(readout_err, [0])
    noise_model.add_readout_error(readout_err, [1])
    
    for depth in range(2, 10):
        b = Benchmarker(nr_qbits=NR_Q, seed=SEED, depth=depth, shots=SHOTS, noise_model=noise_model)
        print(f"depth (seq + recovery): {depth}, result: {b.run_benchmark()}")


    # g = b.Generator()
    # for _ in range(10):
    #     s, r = g.gen_seq(DEPTH)
    #     print("Sequence")
    #     for gate in s:
    #         print(gate)
    #     print(f"Recovery gate: {r}")
