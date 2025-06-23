from qiskit.quantum_info import Clifford, random_clifford
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from typing import Dict, List
from collections.abc import Iterable
from numpy import random


class Benchmarker:
    def __init__(
        self,
        nr_qubits: int = 1,
        seed: int | None = None,
        depth: int = 1,
        shots: int = 1,
        noise_model: NoiseModel | None = None,
    ):
        self.nr_qubits = nr_qubits if nr_qubits > 0 else 1
        self.seed = seed
        self.depth = depth if depth > 0 else 1  # number of gates to apply (including recovery)
        self.shots = shots if shots > 0 else 1  # number of times to repeat experiment
        self.noise_model = noise_model

    def run_benchmark(self) -> float:
        """
        Runs a Clifford benchmark.

        Returns:
            float: Quantum bit error rate estimation.
        """
        
        g = self.Generator(nr_qubits=self.nr_qubits, seed=self.seed)
        e = self.Executor(nr_qubits=self.nr_qubits, noise_model=self.noise_model)

        gates = g.generate_benchmark_sequence(
            self.depth - 1
        )  # make space for the recovery gate

        measurements = e.run_sequence(gates, shots=self.shots)
        qber = e.get_qber(measurements)

        return qber

    class Generator:
        def __init__(self, nr_qubits: int = 1, seed: int | None = None):
            self.nr_qubits = nr_qubits if nr_qubits > 0 else 1
            self.rng = random.default_rng(seed)

        def generate_random_clifford(self) -> Clifford:
            """
            Generates a random Clifford gate.

            Returns:
                Clifford: The random gate.
            """
            
            gate = random_clifford(self.nr_qubits, seed=self.rng)
            assert isinstance(gate, Clifford), "Generated item is not a Clifford gate"
            return gate

        def generate_benchmark_sequence(
            self, n: int
        ) -> List[Clifford]:
            """
            Generates a benchmark sequence for Clifford randomized benchmarking of n random Clifford gates and the recovery gate.
            
            Args:
                n (int): Number of random Clifford gates.
            
            Returns:
                List[Clifford]: The list of n+1 gates.
            """
            
            if n <= 0:
                raise ValueError("Sequence length <= 0")

            clifford_sequence = []
            composed_sequence = Clifford(
                QuantumCircuit(self.nr_qubits)
            )  # initialized to identity

            for _ in range(n):
                c = self.generate_random_clifford()
                clifford_sequence.append(c)
                composed_sequence = composed_sequence.compose(c)

            recovery_gate = composed_sequence.adjoint()  # inverse
            
            assert isinstance(recovery_gate, Clifford)
            clifford_sequence.append(recovery_gate)
            
            return clifford_sequence

    class Executor:
        def __init__(self, nr_qubits: int = 1, noise_model: NoiseModel | None = None):
            self.nr_qubits = nr_qubits if nr_qubits > 0 else 1
            self.sim = AerSimulator(noise_model=noise_model)

        def run_sequence(
            self, sequence: Iterable[Clifford], shots: int = 1024
        ) -> Dict[str, int]:
            """
            Runs a Clifford RB sequence. Simulated in Qiskit Aer.
            
            Args:
                sequence(Iterable[Clifford]): Full sequence to run, including recovery gate.
                shots (int): Number of times to run the experiment.
                
            Returns:
                Dict[str, int]: Qiskit histogram of results from .get_counts()
            """
            
            qc = QuantumCircuit(self.nr_qubits, self.nr_qubits)
            qubit_index_list = list(
                range(self.nr_qubits)
            )  # qubits the gates are applied to: all

            for gate in sequence:
                qc.append(gate.to_instruction(), qubit_index_list)

            qc.measure(qubit_index_list, qubit_index_list)

            result = self.sim.run(transpile(qc, self.sim), shots=shots).result()
            counts = result.get_counts(qc)  # qiskit histogram
            
            assert isinstance(counts, dict), "counts is not a dict"
            assert all(isinstance(k, str) for k in counts.keys()), "Not all keys are strings"
            assert all(isinstance(v, int) for v in counts.values()), "Not all values are ints"
            return counts

        def get_qber(self, counts: Dict[str, int]) -> float:
            """
            Computes QBER based on results histogram
            
            Args:
                counts (Dict[str, int]): Histogram of results where values represent measured state.
                
            Returns:
                float: Simple success / trials estimation (temporary).
            """
            
            target = "0" * self.nr_qubits  # qiskit formatting for |00..0>
            trials = sum(counts.values())

            if trials == 0:
                return 0.0
            trials_success = counts.get(target, 0)

            return trials_success / trials
