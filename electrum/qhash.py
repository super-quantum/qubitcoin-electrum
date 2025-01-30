import math
from qulacs import QuantumState, ParametricQuantumCircuit
from .crypto import sha256


TOTAL_BITS = 16
FRACTION_BITS = 15


def toFixed(x: float) -> int:
    fraction_mult = 1 << FRACTION_BITS
    return int(x * fraction_mult + 0.5 if x >= 0 else x * fraction_mult - 0.5)


NUM_QUBITS = 16
NUM_LAYERS = 2

circuit = ParametricQuantumCircuit(NUM_QUBITS)
for l in range(NUM_LAYERS):
    for i in range(NUM_QUBITS):
        circuit.add_parametric_RY_gate(i, 0)
    for i in range(NUM_QUBITS):
        circuit.add_parametric_RZ_gate(i, 0)
    for i in range(NUM_QUBITS - 1):
        circuit.add_CNOT_gate(i, i + 1)

state = QuantumState(NUM_QUBITS)


def qhash(x: bytes) -> bytes:
    in_hash = sha256(x)
    # print(f"in_hash: {in_hash.hex()}")
    for i in range(circuit.get_parameter_count()):
        nibble = in_hash[i // 2] >> (4 * (1 - i % 2)) & 0x0F
        # print(f"nibble: {nibble}")
        circuit.set_parameter(
            i, (-nibble if i // 16 % 2 == 0 else nibble) * math.pi / 8
        )
    # print(circuit.to_json())
    state.set_zero_state()
    circuit.update_quantum_state(state)
    exps = [2 * state.get_zero_probability(i) - 1 for i in range(NUM_QUBITS)]
    fixed_exps = [toFixed(exp) for exp in exps]
    # print(f"exps: {exps}")
    # print(f"fixed_exps: {fixed_exps}")
    data = list[int]()
    for exp in fixed_exps:
        for i in range(TOTAL_BITS // 8):
            data.append(exp >> (8 * i) & 0xFF)
    # print(f"data: {data}")
    res = sha256(in_hash + bytes(data))
    # print(f"QHASH: res: {res.hex()}")
    return res