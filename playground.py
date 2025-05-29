from qiskit.quantum_info import Clifford, random_clifford 
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator 
from typing import List, Tuple, Dict 
from numpy import random

class Handler:
    def __init__ (self, nr_qbits: int = 1, seed: int = None):
        self.nr_qbits = nr_qbits
        self.sim = AerSimulator()
        self.rng = random.default_rng(seed)


    def gen_rand (self) -> Clifford:
        return random_clifford(self.nr_qbits, seed=self.rng)


    def gen_seq (self, m: int) -> Tuple[List[Clifford], Clifford]:
        if m <= 0:
            raise ValueError("m not positive")
        
        seq: List[Clifford] = [] # random sample of Cliffords
        composed_seq = Clifford(QuantumCircuit(self.nr_qbits)) # initialized to identity
        
        for i in range(m):
            c = self.gen_rand()
            seq.append(c)
            composed_seq = c.compose(composed_seq)
        
        recovery: Clifford = composed_seq.adjoint() # inverse
        return seq, recovery


    def run_seq(self, seq: List[Clifford], recovery: Clifford, shots: int=1024) -> Dict[str, int]:
        qc = QuantumCircuit(self.nr_qbits, self.nr_qbits)
        ilist = list(range(self.nr_qbits))
        
        for gate in seq:
            qc.append(gate.to_instruction(), ilist)
        qc.append(recovery.to_instruction(), ilist)
        
        qc.measure(ilist, ilist)
        
        result = self.sim.run(transpile(qc, self.sim), shots=shots).result()
        counts = result.get_counts(qc) # qiskit histogram
        
        # assert isinstance(counts, Dict[str, int])
        return counts


    def eval(self, counts: Dict[str, int]) -> float:
        # simple success / trials evaluation
        target = '0' * self.nr_qbits # qiskit formatting
        
        trials = sum(counts.values())
        if trials == 0: return 0.0
        
        trials_success = counts.get(target, 0)
        return trials_success / trials


if __name__ == "__main__":
    NR_Q = 1
    DEPTH = 2
    SHOTS = 2048
    SEED = 42

    h = Handler(nr_qbits=NR_Q, seed=SEED)
    gates, recovery = h.gen_seq(m=DEPTH)
    
    m = h.run_seq(gates, recovery, shots=SHOTS) # measurements
    
    prob = h.eval(m)
    print(prob)