# -*- coding: utf-8 -*-
"""
Created on Fri May 22 16:48:53 2026

@author: María
"""

import math
from Punto import Punto
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Simula overflow de int32 con signo, igual que la aritmética C++ del libro
_MASK32 = 0xFFFFFFFF


class MallaHash2D:
    def __init__(self, tamanio_celda: float, num_buckets: int = 1024):
        """
        Inicializa la malla uniforme conceptual.
        tamanio_celda: El ancho/alto de cada celda de la cuadrícula.
        num_buckets: Cantidad fija de posiciones en la tabla Hash.
        """
        self.tamanio_celda = tamanio_celda
        self.num_buckets = num_buckets

        # Cada bucket es una lista de entradas [ [(cx, cy), [obj, ...]], ... ]
        self.buckets = [[] for _ in range(self.num_buckets)]

        self.h1 = 0x8da6b343
        self.h2 = 0xd8163841

    def _calcular_indice_hash(self, cx: int, cy: int) -> int:
        """
        Traduce las coordenadas discretas de la celda (cx, cy) a un índice
        de bucket en el rango [0, num_buckets - 1].
        """
        n = (self.h1 * cx + self.h2 * cy) & _MASK32
        if n >= 0x80000000:
            n -= 0x100000000
        n = n % self.num_buckets
        if n < 0:
            n += self.num_buckets
        return n

    def _punto_a_celda(self, x: float, y: float) -> tuple[int, int]:
        """Convierte coordenadas del entorno a coordenadas de celda entera."""
        cx = int(math.floor(x / self.tamanio_celda))
        cy = int(math.floor(y / self.tamanio_celda))
        return cx, cy

    def _buscar_entrada_celda(self, idx: int, cx: int, cy: int):
        """
        Recorre el bucket idx buscando la entrada cuya clave sea exactamente (cx, cy).
        Devuelve la entrada [clave, lista_objetos] o None si no existe.
        """
        for entrada in self.buckets[idx]:
            if entrada[0] == (cx, cy):
                return entrada
        return None

    def vaciar_malla(self):
        """Limpia la malla para el siguiente frame de simulación."""
        for i in range(self.num_buckets):
            self.buckets[i].clear()

    def insertar_objeto(self, objeto, min_x: float, max_x: float, min_y: float, max_y: float):
        """Inserta un objeto en todas las celdas que cubre su AABB."""
        start_cx, start_cy = self._punto_a_celda(min_x, min_y)
        end_cx, end_cy = self._punto_a_celda(max_x, max_y)

        for cx in range(start_cx, end_cx + 1):
            for cy in range(start_cy, end_cy + 1):
                idx = self._calcular_indice_hash(cx, cy)
                entrada = self._buscar_entrada_celda(idx, cx, cy)
                if entrada is None:
                    # Nueva celda en este bucket, añadir entrada con su clave
                    self.buckets[idx].append([(cx, cy), [objeto]])
                else:
                    # La celda ya tiene entrada, agregar objeto a su lista
                    entrada[1].append(objeto)

    def obtener_posibles_colisiones(self, min_x: float, max_x: float, min_y: float, max_y: float) -> set:
        """Devuelve candidatos a colisión filtrando por clave exacta de celda para descartar falsos positivos de hash."""
        posibles_colisiones = set()
        start_cx, start_cy = self._punto_a_celda(min_x, min_y)
        end_cx, end_cy = self._punto_a_celda(max_x, max_y)

        for cx in range(start_cx, end_cx + 1):
            for cy in range(start_cy, end_cy + 1):
                idx = self._calcular_indice_hash(cx, cy)
                entrada = self._buscar_entrada_celda(idx, cx, cy)
                if entrada is not None:
                    posibles_colisiones.update(entrada[1])

        return posibles_colisiones


if __name__ == "__main__":
    
    random.seed(123)

    # Celdas de 20x20 unidades y tabla hash pequeña (32 buckets) para ver colisiones
    TAMANIO_CELDA = 20.0
    malla = MallaHash2D(tamanio_celda=TAMANIO_CELDA, num_buckets=32)

    # Generar 12 objetos cuadrados aleatorios (AABB)
    objetos = []
    for i in range(12):
        ancho = random.uniform(7, 14)
        alto = random.uniform(7, 14)
        x0 = random.uniform(0, 65)
        y0 = random.uniform(0, 65)

        obj = {
            "id": i,
            "min_x": x0,
            "max_x": x0 + ancho,
            "min_y": y0,
            "max_y": y0 + alto
        }
        objetos.append(obj)
        malla.insertar_objeto(i, obj["min_x"], obj["max_x"], obj["min_y"], obj["max_y"])

    # Visualización
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
    plt.title("Prueba Visual: Malla Uniforme Virtual (Spatial Hashing)", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.grid(False)

    print("Mostrando el gráfico de la cuadrícula")
    plt.show()

    print("\n" + "="*60)
    print(" CONTENIDO DE LOS BUCKETS  (clave_celda -> objetos)")
    print("="*60)
    for idx, bucket in enumerate(malla.buckets):
        if bucket:
            print(f"Bucket {idx:2d}:")
            for (cx, cy), ids in bucket:
                print(f"  Celda ({cx:2d},{cy:2d}) -> IDs: {ids}")
    print("="*60)
