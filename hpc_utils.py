"""Funciones de cómputo usadas por notebook_hpc.ipynb.

Viven en un módulo aparte para que los procesos de multiprocessing.Pool
puedan importarlas también en Windows y macOS (método de arranque "spawn").
"""
import math


def f(x):
    """f(x) = sqrt(x) + x^2 + sin(x) + cos(x) + log(x)"""
    return math.sqrt(x) + x ** 2 + math.sin(x) + math.cos(x) + math.log(x)


def process_chunk(data_chunk):
    """Aplica f(x) a cada elemento del bloque y devuelve la suma."""
    total = 0.0
    for x in data_chunk:
        total += f(x)
    return total
