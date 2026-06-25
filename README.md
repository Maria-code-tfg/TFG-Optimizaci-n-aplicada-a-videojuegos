# TFG - Optimización aplicada a videojuegos

Repositorio con las implementaciones desarrolladas para el Trabajo de Fin de Grado **Optimización aplicada a videojuegos**. El código está organizado en dos bloques principales:

- **Colisiones**: implementación y comparación de volúmenes limitadores y estructuras de partición espacial.
- **Pathfinding**: implementación y comparación de algoritmos de búsqueda de caminos sobre cuadrículas.

El objetivo del repositorio es servir como apoyo reproducible a la memoria del TFG, permitiendo ejecutar ejemplos, pruebas visuales y comparaciones de rendimiento de los algoritmos descritos.

---

## Estructura del repositorio

```text
.
├── Colisiones/
│   ├── Punto.py
│   ├── AABB.py
│   ├── OBB.py
│   ├── Circunferencias.py
│   ├── MallaImplícita.py
│   ├── MallaHash.py
│   ├── Hgrid.py
│   ├── quadtree_punteros2.py
│   ├── quadtreelineal.py
│   ├── test_aabb_circunferencias_obb.py
│   ├── test_tiempos_volumenes.py
│   ├── test_colisiones_escalado.py
│   ├── test_particiones_visual.py
│   └── test_particiones_evolucion.py
│
├── Pathfinding/
│   ├── mapa.py
│   ├── IndexPQ.py
│   ├── Algoritmos_estaticos.py
│   ├── DLite.py
│   ├── AnytimeA.py
│   ├── genera_grafica.py
│   ├── Comparacion Dijkstra vs A nodos.py
│   ├── Comparaciones mapas.py
│   ├── Demo AnytimeA.py
│   └── SImulacion A vs DLite.py
│
├── main.py
└── README.md
```

---

## Requisitos

El código está escrito en **Python 3**. Se recomienda utilizar Python 3.10 o superior.

Librerías utilizadas:

```bash
pip install numpy pandas matplotlib
```

También se recomienda crear un entorno virtual:

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

Después instala las dependencias:

```bash
pip install numpy pandas matplotlib
```

---

## Ejecución rápida

Desde la raíz del repositorio se puede usar el fichero `main.py` como lanzador de los ejemplos principales:

```bash
python main.py --list
```

Esto muestra todos los programas disponibles.

Para ejecutar uno concreto:

```bash
python main.py colisiones-volumenes
```

Otro ejemplo:

```bash
python main.py pathfinding-comparacion
```

El lanzador ejecuta cada script desde su propia carpeta para que funcionen correctamente los imports relativos usados en el proyecto.

---

## Programas disponibles desde `main.py`

| Comando | Fichero ejecutado | Descripción |
|---|---|---|
| `colisiones-volumenes` | `Colisiones/test_aabb_circunferencias_obb.py` | Muestra ejemplos visuales de AABB, circunferencias envolventes y OBB sobre un conjunto de puntos. |
| `colisiones-tiempos-volumenes` | `Colisiones/test_tiempos_volumenes.py` | Compara tiempos de construcción de distintos volúmenes limitadores. |
| `colisiones-escalado` | `Colisiones/test_colisiones_escalado.py` | Evalúa el comportamiento de las estructuras de partición espacial al aumentar el número de objetos. |
| `colisiones-particiones-visual` | `Colisiones/test_particiones_visual.py` | Genera una comparación visual de las particiones espaciales implementadas. |
| `colisiones-particiones-evolucion` | `Colisiones/test_particiones_evolucion.py` | Muestra la evolución de las estructuras de partición al insertar objetos. |
| `pathfinding-comparacion` | `Pathfinding/genera_grafica.py` | Compara Dijkstra y A* sobre cuadrículas aleatorias. |
| `pathfinding-comparacion-nodos` | `Pathfinding/Comparacion Dijkstra vs A nodos.py` | Compara Dijkstra y A* atendiendo al número de nodos explorados. |
| `pathfinding-comparaciones-mapas` | `Pathfinding/Comparaciones mapas.py` | Ejecuta comparaciones sobre distintos mapas o escenarios. |
| `pathfinding-demo-anytime` | `Pathfinding/Demo AnytimeA.py` | Ejecuta una demostración del algoritmo Anytime A*. |
| `pathfinding-simulacion-dlite` | `Pathfinding/SImulacion A vs DLite.py` | Ejecuta una simulación comparando A* y D* Lite en un entorno dinámico. |

---

## Bloque de colisiones

La carpeta `Colisiones` contiene las implementaciones relacionadas con detección de colisiones y partición espacial.

### Ficheros auxiliares

Estos ficheros contienen clases o funciones utilizadas por los scripts de prueba:

- `Punto.py`: clases básicas para representar puntos y vectores en 2D.
- `AABB.py`: cajas alineadas con los ejes.
- `OBB.py`: cajas orientadas.
- `Circunferencias.py`: circunferencias envolventes.
- `MallaImplícita.py`: malla implícita para partición espacial.
- `MallaHash.py`: malla hash.
- `Hgrid.py`: malla jerárquica.
- `quadtree_punteros2.py`: quadtree con estructura enlazada mediante nodos.
- `quadtreelineal.py`: quadtree lineal.

Normalmente no se ejecutan directamente, sino que son importados por los ficheros de prueba.

### Scripts principales

- `test_aabb_circunferencias_obb.py`: genera un conjunto de puntos aleatorio y representa distintos volúmenes limitadores.
- `test_tiempos_volumenes.py`: mide tiempos de cálculo de los volúmenes limitadores.
- `test_colisiones_escalado.py`: compara el rendimiento de las estructuras de partición espacial.
- `test_particiones_visual.py`: muestra visualmente cómo particionan el espacio las estructuras implementadas.
- `test_particiones_evolucion.py`: ilustra la evolución de las estructuras al añadir objetos.

---

## Bloque de pathfinding

La carpeta `Pathfinding` contiene implementaciones de algoritmos de búsqueda de caminos sobre cuadrículas.

### Formato de los mapas

Los mapas se representan como una matriz de Python, es decir, una lista de listas:

```python
matriz = [
    [1, 1, 1, 1],
    [1, float('inf'), float('inf'), 1],
    [1, 1, 1, 1],
]
```

El significado usado en los ejemplos es:

- `1`: celda transitable con coste 1.
- `float('inf')`: obstáculo o celda no transitable.
- Las posiciones se indican mediante tuplas `(x, y)`.
- El inicio y el final también son tuplas, por ejemplo:

```python
inicio = (0, 0)
final = (3, 2)
```

La clase `Cuadricula`, definida en `mapa.py`, encapsula la matriz y ofrece métodos para obtener vecinos y consultar costes.

### Ficheros auxiliares

- `mapa.py`: clase `Cuadricula`, que representa el mapa.
- `IndexPQ.py`: cola de prioridad indexada usada por los algoritmos.
- `Algoritmos_estaticos.py`: implementación de Dijkstra y A*.
- `DLite.py`: implementación de D* Lite.
- `AnytimeA.py`: implementación de Anytime A*.

### Scripts principales

- `genera_grafica.py`: genera una comparación de escalabilidad entre Dijkstra y A*.
- `Comparacion Dijkstra vs A nodos.py`: compara el número de nodos explorados por Dijkstra y A*.
- `Comparaciones mapas.py`: ejecuta comparaciones en distintos mapas.
- `Demo AnytimeA.py`: demostración de Anytime A*.
- `SImulacion A vs DLite.py`: simulación comparativa entre A* y D* Lite.

---

## Ejemplo mínimo de uso de pathfinding

```python
from Pathfinding.mapa import Cuadricula
from Pathfinding.Algoritmos_estaticos import dijkstra, A_estrella

matriz = [
    [1, 1, 1, 1],
    [1, float('inf'), float('inf'), 1],
    [1, 1, 1, 1],
]

mapa = Cuadricula(matriz)
inicio = (0, 0)
final = (3, 2)

distancia_dijkstra, camino_dijkstra, visitados_dijkstra = dijkstra(mapa, inicio, final)
distancia_a, camino_a, visitados_a = A_estrella(mapa, inicio, final)

print("Dijkstra:", distancia_dijkstra, camino_dijkstra)
print("A*:", distancia_a, camino_a)
```

---

## Ejemplo mínimo de uso de volúmenes limitadores

```python
from Colisiones.Punto import Punto
from Colisiones.AABB import AABB_min_max
from Colisiones.Circunferencias import Circunferencia_Ritter
from Colisiones.OBB import calcular_obb_minimo

puntos = [
    Punto(0, 0),
    Punto(2, 1),
    Punto(3, 4),
    Punto(1, 5),
]

aabb = AABB_min_max(puntos)
circunferencia = Circunferencia_Ritter(puntos)
obb = calcular_obb_minimo(puntos)

print("AABB:", aabb)
print("Circunferencia:", circunferencia)
print("OBB:", obb)
```

---

## Notas de uso

Algunos scripts generan ventanas con gráficas mediante `matplotlib`. Por tanto, al ejecutarlos se abrirá una ventana interactiva con la visualización correspondiente.

Los scripts de comparación pueden tardar más que los ejemplos visuales, ya que realizan varias ejecuciones para obtener medidas medias.

Si se ejecuta desde un IDE, conviene establecer como directorio de trabajo la raíz del repositorio o utilizar directamente `main.py`.

---

## Relación con la memoria del TFG

Este repositorio acompaña a la memoria del TFG y contiene las implementaciones usadas para estudiar:

- Volúmenes limitadores: AABB, OBB y circunferencias envolventes.
- Técnicas de partición espacial: mallas, malla hash, malla jerárquica y quadtrees.
- Algoritmos de pathfinding: Dijkstra, A*, D* Lite y Anytime A*.
- Comparaciones empíricas mediante simulaciones y gráficas.

---

## Autoría

Trabajo realizado por María para el TFG **Optimización aplicada a videojuegos**.
