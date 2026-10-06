import time
import math
import multiprocessing as mp
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

def run_parallel(data, num_workers):
    chunk_size = len(data) // num_workers
    chunks = [data[i * chunk_size:(i + 1) * chunk_size] for i in range(num_workers - 1)]
    chunks.append(data[(num_workers - 1) * chunk_size:])
    start = time.perf_counter()
    with mp.Pool(processes=num_workers) as pool:
        results = pool.map(process_chunk, chunks)
    end = time.perf_counter()
    return end - start, sum(results)
