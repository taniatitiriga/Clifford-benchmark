from qiskit.quantum_info import Clifford, random_clifford 
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator 
from qiskit_aer.noise import NoiseModel
from typing import List, Tuple, Dict 
from numpy import random

class Benchmarker:
    def __init__ (self, nr_qbits: int = 1, seed: int = None, depth: int = 1, shots: int = 1, noise_model: NoiseModel = None):
        self.nr_qbits = nr_qbits if nr_qbits > 0 else 1
        self.seed = seed
        self.depth = depth if depth > 0 else 1 # nr of gates to apply (including recovery)
        self.shots = shots if shots > 0 else 1 # nr of times to repeat
        self.noise_model = noise_model

    def run_benchmark(self) -> float:
        g = self.Generator(nr_qbits=self.nr_qbits, seed=self.seed)
        e = self.Executor(nr_qbits=self.nr_qbits, noise_model=self.noise_model)

        gates, recovery = g.gen_seq(self.depth - 1) # make space for recovery gate

        measurements = e.run_seq(gates, recovery, shots=self.shots)
        prob = e.eval(measurements)

        return prob


    class Generator:
        def __init__ (self, nr_qbits: int = 1, seed: int = None):
            self.nr_qbits = nr_qbits if nr_qbits > 0 else 1
            self.rng = random.default_rng(seed)

        def gen_rand (self) -> Clifford:
            # generate one random clifford [qiskit placeholder]
            c = random_clifford(self.nr_qbits, seed=self.rng)
            assert isinstance(c, Clifford) == True
            return c

        def gen_seq (self, m: int) -> Tuple[List[Clifford], Clifford]:
            # generate a sequence of m cliffords + the recovery
            if m <= 0:
                raise ValueError("sequence length <= 0")
            
            seq = [] # random sequence of Cliffords
            composed_seq = Clifford(QuantumCircuit(self.nr_qbits)) # initialized to identity

            for _ in range(m):
                c = self.gen_rand()
                seq.append(c)
                composed_seq = composed_seq.compose(c)
            
            recovery = composed_seq.adjoint() # inverse
            assert isinstance(recovery, Clifford) == True
            return seq, recovery


    class Executor:
        def __init__ (self, nr_qbits:  int = 1, noise_model: NoiseModel = None):
            self.nr_qbits = nr_qbits if nr_qbits > 0 else 1
            self.sim = AerSimulator(noise_model=noise_model)

        def run_seq(self, sequence: List[Clifford], recovery: Clifford, shots: int=1024) -> Dict[str, int]:
            # simulates in qiskit aer
            qc = QuantumCircuit(self.nr_qbits, self.nr_qbits)
            qbit_index = list(range(self.nr_qbits)) # qubits the gates are applied to: all
            
            for gate in sequence:
                qc.append(gate.to_instruction(), qbit_index)
            qc.append(recovery.to_instruction(), qbit_index)
            
            qc.measure(qbit_index, qbit_index)
            
            result = self.sim.run(transpile(qc, self.sim), shots=shots).result()
            counts = result.get_counts(qc) # qiskit histogram
            return counts
        
        def eval(self, counts: Dict[str, int]) -> float:
            # simple success / trials evaluation
            target = '0' * self.nr_qbits # qiskit formatting for |00..0>
            trials = sum(counts.values())

            if trials == 0: return 0.0
            trials_success = counts.get(target, 0)

            return trials_success / trials