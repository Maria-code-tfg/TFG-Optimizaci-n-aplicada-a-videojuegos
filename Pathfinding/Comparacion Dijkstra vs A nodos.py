# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 15:17:04 2026

@author: María
"""

import random
import matplotlib.pyplot as plt
import numpy as np

from mapa import Cuadricula
from Algoritmos import dijkstra, A_estrella

  
def comparar_en_main():
    SIZE = 30
    PROB_MURO = 0.25
    
    matriz_aleatoria = [[1 if random.random() > PROB_MURO else float('inf') 
                         for _ in range(SIZE)] for _ in range(SIZE)]
    
    inicio = (3, 4)
    fin = (SIZE - 1, SIZE - 1)
    
    matriz_aleatoria[inicio[1]][inicio[0]] = 1
    matriz_aleatoria[fin[1]][fin[0]] = 1
    
    cuad = Cuadricula(matriz_aleatoria)
    
    d_cost, d_path, d_vis = dijkstra(cuad, inicio, fin)
    a_cost, a_path, a_vis = A_estrella(cuad, inicio, fin)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    img_base = np.array([[0 if v == float('inf') else 0.9 for v in fila] for fila in cuad.matriz])

    config = [
        (ax1, d_path, d_vis, "Dijkstra", "gold"),
        (ax2, a_path, a_vis, "A-Estrella (A*)", "cyan")
    ]

    for ax, path, vis, titulo, color_vis in config:
        ax.imshow(img_base, cmap='gray', origin='upper')
        
        if vis:
            vx, vy = zip(*vis)
            ax.scatter(vx, vy, color=color_vis, s=15, alpha=0.3, label='Nodos explorados')
        
        if path:
            px, py = zip(*path)
            ax.plot(px, py, color='red', linewidth=3, label='Camino óptimo')
        
        ax.scatter(inicio[0], inicio[1], color='green', s=150, marker='s', label='Inicio', zorder=5)
        ax.scatter(fin[0], fin[1], color='blue', s=150, marker='x', label='Meta', zorder=5)
        
        visitados_count = len(vis) if vis else 0
        ax.set_title(f"{titulo}\nNodos visitados: {visitados_count}")
        ax.legend(loc='upper right')
        ax.axis('off')

    plt.suptitle("Comparativa de Eficiencia: Dijkstra vs A*", fontsize=16)
    plt.tight_layout()
    plt.show()

    print(f"\n{'ALGORITMO':<15} | {'NODOS VISITADOS':<15} | {'COSTE TOTAL':<12}")
    print("-" * 50)
    print(f"{'Dijkstra':<15} | {len(d_vis):<15} | {d_cost:<12}")
    print(f"{'A*':<15} | {len(a_vis):<15} | {a_cost:<12}")


if __name__ == "__main__":
    comparar_en_main()