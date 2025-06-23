# Clifford Benchmarking Playground

A minimal tool for simulating Clifford randomized benchmarking using Qiskit and Qiskit Aer.

## Features
- Generate random Clifford sequences.
- Simulate execution with optional noise models.
- Estimate Quantum Bit Error Rate (QBER) based on simulation outcomes.

## Installation
This project uses [`uv`](https://docs.astral.sh/uv/) for environment management.

```bash
uv venv
uv pip install -e .
```

## Usage
```python
from src.benchmark.benchmarker import Benchmarker

bm = Benchmarker(nr_qubits=2, depth=10, shots=1000)
qber = bm.run_benchmark()
print(f"Estimated QBER: {qber}")
```
