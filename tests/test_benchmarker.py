from src.clifford_benchmark.benchmarker import Benchmarker

def test_benchmark_runs() -> None:
    bm = Benchmarker(nr_qubits=1, depth=2, shots=10)
    qber = bm.run_benchmark()
    assert 0.0 <= qber <= 1.0, "Probability should be between 0 and 1"
