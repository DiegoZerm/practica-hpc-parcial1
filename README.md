# EC. Primer Parcial — Proyecto Práctico HPC

**Asignatura:** Cómputo de Alto Rendimiento

**Integrantes:**
1. Diego Cortes Zermeño (@DiegoZerm)
2. Cesar Ivan Ramirez Castañon (@tprogcesarramirez-dotcom)
3. Irving Nahir Ferrusca Jaimez (@irvingjaimez)

## Descripción

Este proyecto compara la ejecución **secuencial** y **paralela** de un programa en Python que procesa una cantidad considerable de datos: se evalúa la función

$$f(x) = \sqrt{x} + x^2 + \sin(x) + \cos(x) + \ln(x)$$

sobre un vector de **25 000 000 de elementos** (200 MB en `float64`).

La versión **secuencial** recorre todo el vector en un solo proceso. La versión **paralela** divide el vector en bloques con `np.array_split` y los distribuye entre **1, 2 y 4 workers** usando `multiprocessing.Pool` + `pool.map`, ejecutando **3 repeticiones por configuración** para promediar los tiempos. Con los promedios se calculan el **Speedup** ($S_p = T_1 / T_p$) y la **Eficiencia** ($E_p = S_p / p$), y se generan automáticamente las gráficas de rendimiento.

## Cómo ejecutar

```bash
pip install -r requirements.txt
jupyter notebook notebook_hpc.ipynb
```

Luego: **Run → Run All Cells** y guardar con `Ctrl+S`.

La ejecución completa tarda aproximadamente **2–3 minutos**. Al finalizar se registran en el cuaderno la tabla de métricas y las gráficas, y se genera el archivo `hpc_performance_results.png`.

## Hardware utilizado

- **Procesador:** AMD Ryzen 7 7435HS
- **Núcleos / hilos:** 8 núcleos físicos / 16 hilos lógicos (1 socket)
- **RAM:** 15 GiB (DDR, ~11 GiB disponibles durante la corrida)
- **Sistema operativo:** Linux Mint 22.2 «Zara» — kernel 7.0.0-38-generic (x86_64)

## Resultados

| Configuración | Prueba 1 | Prueba 2 | Prueba 3 | Promedio (s) | Speedup | Eficiencia |
|---|---|---|---|---|---|---|
| Secuencial | 10.9243 | 10.8759 | 10.8811 | **10.8938** | – | – |
| 1 worker | 12.0673 | 11.9101 | 11.9410 | **11.9728** | 1.00 | 100 % |
| 2 workers | 6.4301 | 6.3903 | 6.3231 | **6.3812** | 1.88 | 93.81 % |
| 4 workers | 3.6270 | 3.5649 | 3.5509 | **3.5809** | 3.34 | 83.59 % |

*Speedup y Eficiencia calculados contra el tiempo de 1 worker (11.9728 s), según la definición del cuaderno.*

![Gráficas de rendimiento](hpc_performance_results.png)

## Análisis de resultados

> Todos los tiempos corresponden a la corrida en el equipo descrito arriba.

### ¿La ejecución paralela fue más rápida que la secuencial?

**Sí con 2 y 4 workers; no con 1 worker.** Con 2 workers el tiempo bajó de 10.8938 s a 6.3812 s (−41.4 %) y con 4 workers a 3.5809 s (−67.1 %). Con 1 worker, en cambio, tardó 11.9728 s: **9.9 % más lenta que la secuencial**, porque el `Pool` debe crear el proceso, serializar y enviar el chunk de datos y recolectar el resultado, y ese *overhead* no se recupera con un solo proceso trabajando.

### ¿Qué número de workers obtuvo el menor tiempo?

**4 workers: 3.5809 s** (pruebas: 3.6270, 3.5649 y 3.5509 s). Es **3.04× más rápido** que la secuencial y **2.90×** más rápido que 1 worker, con un Speedup de 3.3435 y una Eficiencia de 83.59 %.

### ¿Duplicar el número de workers duplicó el rendimiento? ¿Por qué?

**No.** De 1 → 2 workers el Speedup fue **1.88** (no 2.0) y de 1 → 4 workers fue **3.34** (no 4.0); la eficiencia cayó de 100 % → 93.81 % → 83.59 %.

Por la **Ley de Amdahl**, $S(p) = \frac{1}{s + (1-s)/p}$, con $p = 4$ y $S = 3.3435$ la fracción serial estimada es $s \approx 6.5\%$; con $p = 2$ el ajuste da $s \approx 6.6\%$ (consistente). Esa porción no paralelizable —lanzar el `Pool`, copiar los bloques a cada proceso y sumar los parciales (generar el vector y dividirlo ocurren antes de iniciar la medición, así que no cuentan)— limita el rendimiento máximo. A esto se suma el **overhead de `multiprocessing`**: crear los procesos, copiar/serializar cada bloque por el *pipe* (pickle) y devolver los resultados por IPC. Por eso duplicar procesos nunca duplica el rendimiento.

### ¿Por qué el problema seleccionado puede paralelizarse?

Es un caso de ***embarrassingly parallel***: cada $f(x)$ se calcula de forma **independiente**, sin dependencias entre iteraciones, sin datos compartidos y sin sincronización entre workers durante el cálculo (solo hay una reducción al final con `sum`). Basta dividir el vector con `np.array_split` y aplicar `pool.map`, sin riesgo de condiciones de carrera.

### ¿En qué momento agregar más workers deja de ser beneficioso?

Cuando el **overhead marginal supera la ganancia de cómputo**. Señales observadas:

1. La eficiencia ya decae desde 2 workers (100 % → 93.81 % → 83.59 %): cada worker adicional aporta menos tiempo ahorrado.
2. Al superar los **8 núcleos físicos** los procesos compiten por CPU e hiperhilos, con contención de la caché L3 compartida (16 MiB).
3. Cuando el chunk de trabajo se hace pequeño respecto al costo de crear el proceso y copiar los datos, el speedup se estanca o invierte.

En este experimento, con 8 workers la curva ya estaría en zona de rendimientos decrecientes; con 4 aún conviene porque el cómputo (~10.9 s secuenciales) domina sobre el overhead (~1.1 s: 11.97 s con 1 worker contra 10.89 s secuencial).

### ¿Qué limitaciones tiene el hardware utilizado?

- **CPU:** AMD Ryzen 7 7435HS — 8 núcleos físicos / 16 hilos lógicos. Solo se usaron **4 workers = la mitad de los núcleos físicos**, por lo que el hardware no se explota al completo. Las frecuencias de turbo (hasta 4.55 GHz) no se sostienen en cargas multihilo prolongadas.
- **RAM:** 15 GiB totales, ~11 GiB disponibles. El vector de 25 000 000 `float64` ocupa 200 MB y, al repartirse entre procesos, `multiprocessing` duplica esa memoria al copiar los chunks.
- **Thermal / frecuencia:** ~59–62 °C del sensor ACPI durante la corrida en un **portátil**, sujeto a limitaciones de potencia y a *thermal throttling* en cargas sostenidas; el *governor* del CPU osciló entre `powersave` y `performance`, lo que cambia los MHz disponibles entre corridas y explica parte de la varianza entre repeticiones.
- **Procesos de fondo:** el entorno de escritorio Linux Mint compite por núcleos y añade ruido a las mediciones (varianza de ±0.1 s entre repeticiones).

### ¿Este experimento representa HPC o solamente demuestra principios utilizados en HPC? Justifiquen.

**Demuestra principios de HPC; no es un sistema HPC.**

- **Sí aplica principios de HPC:** descomposición de datos en bloques, ejecución concurrente en múltiples procesos, medición de **Speedup** y **Eficiencia**, identificación de la fracción serial y del *overhead*, y evaluación del escalamiento —las métricas clásicas de la disciplina.
- **No es HPC real:** se ejecuta en **una sola computadora** (shared-memory, un nodo), sin clúster multinodo, sin memoria distribuida, sin interconexión de baja latencia (InfiniBand/RoCE), sin MPI ni escalado a miles de núcleos, sin gestor de colas/particiones, sin I/O paralelo distribuido y con un dataset de 200 MB lejos de las escalas típicas de HPC (GB–TB).

La frontera es la escala: HPC exige clústeres, paralelismo a gran escala y gestión de recursos; este ejercicio es un **laboratorio controlado de un nodo** que ilustra las métricas y el razonamiento que sí se usan en HPC.

## Conclusión

El experimento confirma empíricamente las leyes del paralelismo: con 4 workers se alcanzó un Speedup de 3.34× y una Eficiencia de 83.59 %, pero duplicar procesos nunca duplicó el rendimiento porque la fracción serial y el overhead de `multiprocessing` imponen un techo —exactamente lo que predice la Ley de Amdahl. Este trabajo demuestra los **principios fundamentales de HPC** (paralelismo de datos, métricas de speedup/eficiencia y análisis de escalamiento) en un entorno real, pero **no constituye HPC**: un entorno de producción multinodo sustituye la memoria compartida de una sola máquina por memoria distribuida sobre un clúster, comunica los nodos a través de interconexiones de baja latencia con MPI, y añade gestores de colas, I/O paralelo y escalado a miles de núcleos, donde el costo de comunicación entre nodos —no el de un *pipe* local— se convierte en la limitación dominante. Los mismos principios miden ambos mundos; cambia la escala y el precio de cada ciclo de comunicación.
