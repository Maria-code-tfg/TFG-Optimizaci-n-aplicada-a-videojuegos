# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 19:09:14 2026

@author: María
"""

#Hacer la gráfica
import matplotlib.pyplot as plt
import time
import random
import numpy as np

from mapa import Cuadricula
from Algoritmos import dijkstra, A_estrella

def benchmark_pathfinding():
    repeticiones_por_tamano = 10  
    tamanos = range(10, 110, 1)  
    
    stats_dijkstra = []
    stats_astar = []
    eje_x_tamanos = []

    print("Iniciando benchmark de 1000 ejecuciones...")

    for n in tamanos:
        vis_d_acumulados = 0
        vis_a_acumulados = 0
        casos_validos = 0
        
        for _ in range(repeticiones_por_tamano):
            # Generar mapa aleatorio
            matriz = [[1 if random.random() > 0.25 else float('inf') for _ in range(n)] for _ in range(n)]
            inicio, fin = (0, 0), (n-1, n-1)
            matriz[0][0] = 1
            matriz[n-1][n-1] = 1
            
            cuad = Cuadricula(matriz)
            
            d_cost, d_path, d_vis = dijkstra(cuad, inicio, fin)
            a_cost, a_path, a_vis = A_estrella(cuad, inicio, fin)
            
            # Solo contamos si ambos encontraron camino
            if d_cost != float('inf') and a_cost != float('inf'):
                vis_d_acumulados += len(d_vis)
                vis_a_acumulados += len(a_vis)
                casos_validos += 1
        
        if casos_validos > 0:
            eje_x_tamanos.append(n)
            stats_dijkstra.append(vis_d_acumulados / casos_validos)
            stats_astar.append(vis_a_acumulados / casos_validos)
        
        if n % 10 == 0:
            print(f"Procesado hasta tamaño {n}x{n}...")

    # --- GENERAR GRÁFICA DE COMPLEJIDAD ---
    plt.figure(figsize=(10, 6))
    plt.plot(eje_x_tamanos, stats_dijkstra, label='Dijkstra (Nodos en Pop)', color='gold', linewidth=2)
    plt.plot(eje_x_tamanos, stats_astar, label='A* (Nodos en Pop)', color='cyan', linewidth=2)
    
    plt.title('Análisis de Escalabilidad: Dijkstra vs A*', fontsize=14)
    plt.xlabel('Tamaño de la cuadrícula (N x N)', fontsize=12)
    plt.ylabel('Promedio de Nodos Expandidos', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.show()

if __name__ == "__main__":
    benchmark_pathfinding()