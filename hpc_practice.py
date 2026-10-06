import time
import math
import numpy as np

def process_chunk(data_chunk):
    """Procesa un bloque de datos aplicando operaciones matemáticas pesadas."""
    total = 0.0
    for x in data_chunk:
        total += math.sqrt(x) + math.sin(x) * math.cos(x)
    return total

def generate_data(n_elements=20_000_000):
    """Genera un arreglo de datos para procesar."""
    return np.arange(1, n_elements + 1, dtype=np.float64)

def run_sequential(data):
    start = time.perf_counter()
    result = process_chunk(data)
    end = time.perf_counter()
    return end - start, result
