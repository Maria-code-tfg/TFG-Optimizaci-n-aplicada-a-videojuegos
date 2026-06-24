# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 17:52:51 2026

@author: María
"""
import random
import math
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from Punto import *
from OBB import calcular_obb_minimo
from AABB import AABB_min_max
from Circunferencias import *

def generar_nube_puntos(num_puntos: int, x_min: float, x_max: float, y_min: float, y_max: float) -> list[Punto]:
    """
    Genera una nube de 'num_puntos' puntos aleatorios uniformemente distribuidos
    dentro de un rectángulo definido por (x_min, y_min) y (x_max, y_max).
    Los puntos no tienen ningún orden específico (no es un polígono).
    """
    puntos = []
    for _ in range(num_puntos):
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)
        puntos.append(Punto(x, y))
    return puntos

if __name__ == "__main__":
    random.seed(42)
    
    # Límites del rectángulo (fijos para todas las nubes)
    X_MIN, X_MAX = -50, 50
    Y_MIN, Y_MAX = -50, 50
    
    # Números de puntos a probar: valores pequeños + secuencia de 50 en 50 hasta 1000
    num_puntos_list = [3, 5, 10, 20] + list(range(50, 1050, 50))
    REPETICIONES = 30  # nubes por cada tamaño
    
    print("=== Medición de tiempos de construcción de volúmenes envolventes ===")
    print(f"Puntos por nube: {num_puntos_list}")
    print(f"Repeticiones por cada uno: {REPETICIONES}\n")
    
    # Estructura para almacenar tiempos: {método: {n_puntos: [tiempos_en_ms]}}
    tiempos = {
        'AABB': {n: [] for n in num_puntos_list},
        'Ritter': {n: [] for n in num_puntos_list},
        'PCA': {n: [] for n in num_puntos_list},
        'Welzl': {n: [] for n in num_puntos_list},
        'OBB': {n: [] for n in num_puntos_list}
    }
    
    # Bucle principal
    for n in num_puntos_list:
        print(f"  Probando con {n} puntos...", end='', flush=True)
        for _ in range(REPETICIONES):
            # Generar nube de puntos aleatoria dentro del rectángulo
            nube = generar_nube_puntos(n, X_MIN, X_MAX, Y_MIN, Y_MAX)
            
            # Medir tiempos de construcción (sin intersecciones)
            # AABB
            t0 = time.perf_counter()
            aabb = AABB_min_max(nube)
            t1 = time.perf_counter()
            tiempos['AABB'][n].append((t1 - t0) * 1000)  # ms
            
            # Ritter
            t0 = time.perf_counter()
            ritter = Circunferencia_Ritter(nube)
            t1 = time.perf_counter()
            tiempos['Ritter'][n].append((t1 - t0) * 1000)
            
            # PCA
            t0 = time.perf_counter()
            pca = Circunferencia_Ritter_PCA(nube)
            t1 = time.perf_counter()
            tiempos['PCA'][n].append((t1 - t0) * 1000)
            
            # Welzl (mínima exacta)
            t0 = time.perf_counter()
            welzl = obtener_circunferencia(nube)
            t1 = time.perf_counter()
            tiempos['Welzl'][n].append((t1 - t0) * 1000)
            
            # OBB
            t0 = time.perf_counter()
            obb = calcular_obb_minimo(nube)
            t1 = time.perf_counter()
            tiempos['OBB'][n].append((t1 - t0) * 1000)
        
        print(" hecho")
    
    # --- Procesar resultados ---
    datos = []
    for metodo in tiempos.keys():
        for n in num_puntos_list:
            lista = tiempos[metodo][n]
            if lista:
                media = np.mean(lista)
                std = np.std(lista)
                datos.append({
                    'Metodo': metodo,
                    'NumPuntos': n,
                    'TiempoMedio_ms': media,
                    'Desviacion_ms': std
                })
    
    df = pd.DataFrame(datos)
    
    # Guardar en Excel
    nombre_excel = 'Tiempos_Construccion_NubePuntos_Rectangulo.xlsx'
    with pd.ExcelWriter(nombre_excel, engine='openpyxl') as writer:
        df_pivot = df.pivot(index='NumPuntos', columns='Metodo', values='TiempoMedio_ms')
        df_pivot.to_excel(writer, sheet_name='TiemposMedios')
        
        df_std = df.pivot(index='NumPuntos', columns='Metodo', values='Desviacion_ms')
        df_std.to_excel(writer, sheet_name='Desviaciones')
        
        for sheet in ['TiemposMedios', 'Desviaciones']:
            ws = writer.book[sheet]
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
    
    print(f"\nDatos exportados a '{nombre_excel}'")
    
    # --- GRÁFICOS ---
    
    # 1. Curvas de tiempo medio vs número de puntos (escala lineal en X, log en Y)
    plt.figure(figsize=(12, 6))
    metodos_orden = ['AABB', 'Ritter', 'PCA', 'Welzl', 'OBB']
    colores = ['#2b6cb0', '#319795', '#4a5568', '#e53e3e', '#d69e2e']
    marcadores = ['s', 'o', '^', 'D', 'v']
    
    for i, metodo in enumerate(metodos_orden):
        medias = df[df['Metodo'] == metodo].set_index('NumPuntos')['TiempoMedio_ms'].reindex(num_puntos_list)
        stds = df[df['Metodo'] == metodo].set_index('NumPuntos')['Desviacion_ms'].reindex(num_puntos_list)
        
        plt.errorbar(num_puntos_list, medias, 
                     label=metodo, marker=marcadores[i], color=colores[i], 
                     linewidth=2, capsize=5, capthick=2, markersize=8)
    
    plt.xscale('linear')
    plt.yscale('log')
    plt.xlabel('Número de puntos', fontsize=12)
    plt.ylabel('Tiempo medio de construcción (ms) [escala log]', fontsize=12)
    plt.title('Tiempo de construcción de volúmenes limitadores (nube de puntos)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    ax = plt.gca()
    ax.xaxis.set_major_locator(plt.MaxNLocator(12))
    plt.tight_layout()
    plt.show()
    
    # 2. Gráfico adicional con escala lineal en ambos ejes
    plt.figure(figsize=(12, 6))
    for i, metodo in enumerate(metodos_orden):
        medias = df[df['Metodo'] == metodo].set_index('NumPuntos')['TiempoMedio_ms'].reindex(num_puntos_list)
        stds = df[df['Metodo'] == metodo].set_index('NumPuntos')['Desviacion_ms'].reindex(num_puntos_list)
        plt.errorbar(num_puntos_list, medias, 
                     label=metodo, marker=marcadores[i], color=colores[i], 
                     linewidth=2, capsize=5, capthick=2, markersize=8)
    
    plt.xscale('linear')
    plt.yscale('linear')
    plt.xlabel('Número de puntos', fontsize=12)
    plt.ylabel('Tiempo medio de construcción (ms)', fontsize=12)
    plt.title('Tiempo de construcción (escala lineal)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    ax = plt.gca()
    ax.xaxis.set_major_locator(plt.MaxNLocator(12))
    plt.tight_layout()
    plt.show()
    
    # 3. Diagrama de barras para 100 puntos
    n_fijo = 100
    if n_fijo in num_puntos_list:
        plt.figure(figsize=(8, 5))
        df_fijo = df[df['NumPuntos'] == n_fijo]
        metodos_fijo = df_fijo['Metodo'].tolist()
        tiempos_fijo = df_fijo['TiempoMedio_ms'].tolist()
        stds_fijo = df_fijo['Desviacion_ms'].tolist()
        
        orden = sorted(zip(metodos_fijo, tiempos_fijo, stds_fijo), key=lambda x: x[1])
        metodos_ord, tiempos_ord, stds_ord = zip(*orden)
        
        barras = plt.bar(metodos_ord, tiempos_ord, capsize=5, 
                         color=['#2b6cb0', '#319795', '#4a5568', '#e53e3e', '#d69e2e'],
                         edgecolor='black')
        plt.ylabel('Tiempo medio (ms)', fontsize=12)
        plt.title(f'Tiempo de construcción para {n_fijo} puntos', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        
        for barra in barras:
            altura = barra.get_height()
            plt.annotate(f'{altura:.3f}',
                         xy=(barra.get_x() + barra.get_width()/2, altura),
                         xytext=(0, 3),
                         textcoords="offset points",
                         ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    else:
        print(f"Nota: {n_fijo} no está en la lista, no se genera el diagrama de barras.")
    
    print("\nFin del script.")