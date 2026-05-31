# -*- coding: utf-8 -*-
"""
Created on Fri May 22 20:48:56 2026

@author: María
"""

import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class MallaImplicita2D:
    def __init__(self, grid_width: int, grid_height: int, tamanio_celda: float, num_objetos: int):
        """
        Inicializa una malla implícita utilizando máscaras de bits.
        grid_width: Número de columnas de la malla.
        grid_height: Número de filas de la malla.
        tamanio_celda: Tamaño (ancho/alto) de cada celda geométrica.
        num_objetos: Cantidad total de objetos en la simulación (para dimensionar los bits).
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.tamanio_celda = tamanio_celda
        self.num_objetos = num_objetos
        self.rowBitArray = [0] * self.grid_height # bitarray para cada fila
        self.columnBitArray = [0] * self.grid_width # bitarray para cada columna

    def _punto_a_celda(self, x: float, y: float) -> tuple[int, int]:
        """Convierte coordenadas reales a índices discretos de fila/columna."""
        cx = int(math.floor(x / self.tamanio_celda))
        cy = int(math.floor(y / self.tamanio_celda))
        if not (0 <= cx < self.grid_width and 0 <= cy < self.grid_height):
            raise ValueError(
                f"Coordenadas ({x}, {y}) fuera de los límites de la malla "
                f"({self.grid_width}x{self.grid_height} celdas de {self.tamanio_celda} unidades)."
            )
        return cx, cy

    def insertar_objeto(self, id_objeto: int, min_x: float, max_x: float, min_y: float, max_y: float):
        """Registra el objeto en todas las filas y columnas que intersecta."""
        x1, y1 = self._punto_a_celda(min_x, min_y)
        x2, y2 = self._punto_a_celda(max_x, max_y)
        
        # Definimos la máscara del objeto
        mascara_objeto = 1 << id_objeto
        
        # Activar el bit del objeto en todas las columnas que cruza
        for cx in range(x1, x2 + 1):
            self.columnBitArray[cx] |= mascara_objeto
            
        # Activar el bit del objeto en todas las filas que cruza
        for cy in range(y1, y2 + 1):
            self.rowBitArray[cy] |= mascara_objeto

    def obtener_posibles_colisiones(self, min_x: float, max_x: float, min_y: float, max_y: float, id_excluir: int = -1) -> list[int]:
        """
        Busca qué objetos comparten celdas usando la propiedad distributiva de bits
        """
        x1, y1 = self._punto_a_celda(min_x, min_y)
        x2, y2 = self._punto_a_celda(max_x, max_y)
        
        # Combinar todas las filas que pisa el objeto usando OR (|)
        mergedRowArray = 0
        for cy in range(y1, y2 + 1):
            mergedRowArray |= self.rowBitArray[cy]
            
        # Combinar todas las columnas que pisa el objeto usando OR (|)
        mergedColumnArray = 0
        for cx in range(x1, x2 + 1):
            mergedColumnArray |= self.columnBitArray[cx]
            
        objectsMask = mergedRowArray & mergedColumnArray

        # Extraer IDs excluyendo el objeto consultado
        resultados = []
        for i in range(self.num_objetos):
            if i != id_excluir and (objectsMask & (1 << i)):
                resultados.append(i)
        return resultados



if __name__ == "__main__":
    random.seed(42) # Semilla fija para reproducibilidad
    
    # Parámetros de nuestra cuadrícula implícita
    GRID_ANCHO = 5  # 5 columnas
    GRID_ALTO = 5   # 5 filas
    TAMANIO_CELDA = 20.0
    NUM_OBJETOS = 6 # Mantenemos pocos objetos para que el binario impreso sea legible
    
    malla = MallaImplicita2D(GRID_ANCHO, GRID_ALTO, TAMANIO_CELDA, NUM_OBJETOS)
    
    # Generar objetos cuadrados dentro de los límites del mundo (0 a 100)
    objetos = []
    for i in range(NUM_OBJETOS):
        w = random.uniform(8, 15)
        h = random.uniform(8, 15)
        x0 = random.uniform(5, 80)
        y0 = random.uniform(5, 80)
        
        obj = {"id": i, "min_x": x0, "max_x": x0 + w, "min_y": y0, "max_y": y0 + h}
        objetos.append(obj)
        malla.insertar_objeto(i, obj["min_x"], obj["max_x"], obj["min_y"], obj["max_y"])

    # GRÁFICO
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Dibujar las líneas de la cuadrícula
    for x in range(GRID_ANCHO + 1):
        ax.axvline(x * TAMANIO_CELDA, color="#cbd5e0", linestyle="--", linewidth=1.2)
    for y in range(GRID_ALTO + 1):
        ax.axhline(y * TAMANIO_CELDA, color="#cbd5e0", linestyle="--", linewidth=1.2)
        
    # Dibujar los objetos cuadrados
    colores = ["#e53e3e", "#3182ce", "#38a169", "#d69e2e", "#805ad5", "#319795"]
    for obj in objetos:
        color = colores[obj["id"] % len(colores)]
        rect = patches.Rectangle(
            (obj["min_x"], obj["min_y"]), 
            obj["max_x"] - obj["min_x"], 
            obj["max_y"] - obj["min_y"], 
            linewidth=2, edgecolor=color, facecolor=color, alpha=0.15, zorder=3
        )
        ax.add_patch(rect)
        
        # ID en el centro
        cx = (obj["min_x"] + obj["max_x"]) / 2
        cy = (obj["min_y"] + obj["max_y"]) / 2
        ax.text(cx, cy, f"ID:{obj['id']}", fontsize=11, fontweight="bold", color=color, ha="center", va="center")

    # Imprimir máscaras de las columnas en el eje X (abajo)
    for col in range(GRID_ANCHO):
        # Convertimos el entero a una cadena binaria de longitud NUM_OBJETOS (ej: "010110")
        # Invertimos el texto binario [::-1] para que el bit de la ID:0 quede a la izquierda y sea intuitivo leerlo
        bin_str = f"{malla.columnBitArray[col]:0{NUM_OBJETOS}b}"[::-1]
        posX = (col * TAMANIO_CELDA) + (TAMANIO_CELDA / 2)
        ax.text(posX, -6, bin_str, fontsize=10, fontfamily="monospace", ha="center", color="#4a5568", 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='#cbd5e0'))

    # Imprimir máscaras de las filas en el eje Y (a la derecha) [cite: 185, 188, 189, 192, 194]
    for fila in range(GRID_ALTO):
        bin_str = f"{malla.rowBitArray[fila]:0{NUM_OBJETOS}b}"[::-1]
        posY = (fila * TAMANIO_CELDA) + (TAMANIO_CELDA / 2)
        ax.text(GRID_ANCHO * TAMANIO_CELDA + 2, posY, bin_str, fontsize=10, fontfamily="monospace", va="center", color="#4a5568",
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='#cbd5e0'))

    # Ajustes de la ventana
    ax.set_xlim(-5, (GRID_ANCHO * TAMANIO_CELDA) + 20)
    ax.set_ylim(-10, (GRID_ALTO * TAMANIO_CELDA) + 5)
    ax.set_aspect("equal")
    plt.title("Malla Implícita 2D utilizando Arreglos de Bits", fontsize=13, fontweight="bold", pad=20)
    plt.grid(False)
    
    # Consultar todos los objetos y acumular pares candidatos únicos
    print("="*60)
    print(" CONSULTA DE COLISIONES UTILIZANDO PROPIEDADES DE BITS")
    print("="*60)
    pares_detectados = set()
    for obj in objetos:
        vecinos = malla.obtener_posibles_colisiones(
            obj["min_x"], obj["max_x"], obj["min_y"], obj["max_y"],
            id_excluir=obj["id"]
        )
        if vecinos:
            print(f"Objeto ID:{obj['id']} -> candidatos: {vecinos}")
            for v in vecinos:
                pares_detectados.add(tuple(sorted((obj["id"], v))))
        else:
            print(f"Objeto ID:{obj['id']} -> sin candidatos")
    print(f"\nPares candidatos totales: {sorted(pares_detectados)}")
    print("="*60)

    plt.show()