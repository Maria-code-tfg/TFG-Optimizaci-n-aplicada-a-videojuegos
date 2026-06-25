# -*- coding: utf-8 -*-
"""
Lanzador principal para los ejemplos del repositorio del TFG.

Uso:
    python main.py --list
    python main.py colisiones-volumenes
    python main.py pathfinding-comparacion
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

PROGRAMAS = {
    "colisiones-volumenes": {
        "path": ROOT / "Colisiones" / "test_aabb_circunferencias_obb.py",
        "descripcion": "Ejemplo visual de AABB, circunferencias envolventes y OBB.",
    },
    "colisiones-tiempos-volumenes": {
        "path": ROOT / "Colisiones" / "test_tiempos_volumenes.py",
        "descripcion": "Comparación de tiempos de construcción de volúmenes limitadores.",
    },
    "colisiones-escalado": {
        "path": ROOT / "Colisiones" / "test_colisiones_escalado.py",
        "descripcion": "Comparación de estructuras de partición espacial al aumentar el número de objetos.",
    },
    "colisiones-particiones-visual": {
        "path": ROOT / "Colisiones" / "test_particiones_visual.py",
        "descripcion": "Comparación visual de estructuras de partición espacial.",
    },
    "colisiones-particiones-evolucion": {
        "path": ROOT / "Colisiones" / "test_particiones_evolucion.py",
        "descripcion": "Evolución de las estructuras de partición al insertar objetos.",
    },
    "pathfinding-comparacion": {
        "path": ROOT / "Pathfinding" / "genera_grafica.py",
        "descripcion": "Comparación de escalabilidad entre Dijkstra y A*.",
    },
    "pathfinding-comparacion-nodos": {
        "path": ROOT / "Pathfinding" / "Comparacion Dijkstra vs A nodos.py",
        "descripcion": "Comparación de Dijkstra y A* según nodos explorados.",
    },
    "pathfinding-comparaciones-mapas": {
        "path": ROOT / "Pathfinding" / "Comparaciones mapas.py",
        "descripcion": "Comparaciones de pathfinding sobre distintos mapas.",
    },
    "pathfinding-demo-anytime": {
        "path": ROOT / "Pathfinding" / "Demo AnytimeA.py",
        "descripcion": "Demostración del algoritmo Anytime A*.",
    },
    "pathfinding-simulacion-dlite": {
        "path": ROOT / "Pathfinding" / "SImulacion A vs DLite.py",
        "descripcion": "Simulación comparativa entre A* y D* Lite.",
    },
}


def listar_programas() -> None:
    """Muestra los programas disponibles."""
    print("Programas disponibles:\n")
    for nombre, datos in PROGRAMAS.items():
        print(f"  {nombre}")
        print(f"      {datos['descripcion']}")
        print(f"      Fichero: {datos['path'].relative_to(ROOT)}\n")


def ejecutar_programa(nombre: str) -> int:
    """Ejecuta el programa indicado desde su propia carpeta."""
    datos = PROGRAMAS.get(nombre)
    if datos is None:
        print(f"Error: no existe el programa '{nombre}'.\n")
        listar_programas()
        return 1

    script = datos["path"]
    if not script.exists():
        print(f"Error: no se ha encontrado el fichero {script.relative_to(ROOT)}")
        return 1

    print(f"Ejecutando: {script.relative_to(ROOT)}")
    print("-" * 60)

    resultado = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(script.parent),
        check=False,
    )
    return resultado.returncode


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lanzador de ejemplos del repositorio del TFG Optimización aplicada a videojuegos."
    )
    parser.add_argument(
        "programa",
        nargs="?",
        help="Nombre del programa a ejecutar. Usa --list para ver las opciones.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Muestra todos los programas disponibles.",
    )
    return parser


def main() -> int:
    parser = construir_parser()
    args = parser.parse_args()

    if args.list or args.programa is None:
        listar_programas()
        return 0

    return ejecutar_programa(args.programa)


if __name__ == "__main__":
    raise SystemExit(main())
