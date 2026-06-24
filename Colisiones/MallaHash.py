# -*- coding: utf-8 -*-
"""
Created on Fri May 22 16:48:53 2026

@author: María
"""

import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class MallaHash2D:
    def __init__(self, tamanio_celda: float):
        """
        Inicializa la malla uniforme utilizando un diccionario espacial nativo.
        tamanio_celda: El ancho/alto de cada celda de la cuadrícula.
        """
        self.tamanio_celda = tamanio_celda
        # Diccionario clave: (cx, cy) -> valor: [objeto, objeto, ...]
        self.celdas = {}

    def _punto_a_celda(self, x: float, y: float) -> tuple[int, int]:
        """Convierte coordenadas del entorno a coordenadas de celda entera."""
        cx = int(math.floor(x / self.tamanio_celda))
        cy = int(math.floor(y / self.tamanio_celda))
        return cx, cy

    def vaciar_malla(self):
        """Limpia la malla para el siguiente frame de simulación."""
        self.celdas.clear()

    def insertar_objeto(self, objeto, min_x: float, max_x: float, min_y: float, max_y: float):
        """Inserta un objeto en todas las celdas que cubre su AABB."""
        start_cx, start_cy = self._punto_a_celda(min_x, min_y)
        end_cx, end_cy = self._punto_a_celda(max_x, max_y)

        for cx in range(start_cx, end_cx + 1):
            for cy in range(start_cy, end_cy + 1):
                clave = (cx, cy)
                # Crea la lista si la celda está vacía y añade el objeto
                self.celdas.setdefault(clave, []).append(objeto)

    def obtener_posibles_colisiones(self, min_x: float, max_x: float, min_y: float, max_y: float) -> set:
        """Devuelve candidatos recuperando directamente la lista de las celdas implicadas."""
        posibles_colisiones = set()
        start_cx, start_cy = self._punto_a_celda(min_x, min_y)
        end_cx, end_cy = self._punto_a_celda(max_x, max_y)

        for cx in range(start_cx, end_cx + 1):
            for cy in range(start_cy, end_cy + 1):
                posibles_colisiones.update(self.celdas.get((cx, cy), []))

        return posibles_colisiones

if __name__ == "__main__":
    
    random.seed(123)

    TAMANIO_CELDA = 20.0
    malla = MallaHash2D(tamanio_celda=TAMANIO_CELDA)

    objetos = []
    for i in range(12):
        ancho = random.uniform(7, 14)
        alto = random.uniform(7, 14)
        x0 = random.uniform(0, 65)
        y0 = random.uniform(0, 65)

        obj = {"id": i, "min_x": x0, "max_x": x0 + ancho, "min_y": y0, "max_y": y0 + alto}
        objetos.append(obj)
        malla.insertar_objeto(i, obj["min_x"], obj["max_x"], obj["min_y"], obj["max_y"])

    fig, ax = plt.subplots(figsize=(9, 9))

    for obj in objetos:
        rect = patches.Rectangle(
            (obj["min_x"], obj["min_y"]),
            obj["max_x"] - obj["min_x"],
            obj["max_y"] - obj["min_y"],
            linewidth=2, edgecolor="#2b6cb0", facecolor="#ebf8ff", alpha=0.7, zorder=3
        )
        ax.add_patch(rect)

        centro_x = (obj["min_x"] + obj["max_x"]) / 2
        centro_y = (obj["min_y"] + obj["max_y"]) / 2
        ax.text(centro_x, centro_y, f"ID:{obj['id']}", fontsize=10, fontweight="bold",
                color="#2c5282", ha="center", va="center", zorder=4)

    for x in range(-20, 110, int(TAMANIO_CELDA)):
        ax.axvline(x, color="#cbd5e0", linestyle="--", linewidth=1.2, zorder=1)
    for y in range(-20, 110, int(TAMANIO_CELDA)):
        ax.axhline(y, color="#cbd5e0", linestyle="--", linewidth=1.2, zorder=1)

    ax.set_xlim(-10, 90)
    ax.set_ylim(-10, 90)
    ax.set_aspect("equal")
    plt.title("Prueba Visual: Malla Uniforme Virtual (Diccionarios Python)", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.grid(False)

    print("Mostrando el gráfico de la cuadrícula")
    plt.show()

    print("\n" + "="*60)
    print(" CONTENIDO DE LAS CELDAS  (clave_celda -> objetos)")
    print("="*60)
    for clave, ids in malla.celdas.items():
        print(f"  Celda {clave} -> IDs: {ids}")
    print("="*60)