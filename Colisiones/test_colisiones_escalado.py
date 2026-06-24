# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 17:57:29 2026

@author: María
"""

import random
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
import sys



from Punto import *
from OBB import calcular_obb_minimo
from AABB import AABB_min_max
from Circunferencias import *

def generar_poligono_simple(num_vertices: int, centro_x: float, centro_y: float,
                            semi_ancho: float, semi_alto: float) -> list[Punto]:
    """
    Genera un polígono simple (sin auto-intersecciones) cuyos vértices se
    distribuyen aleatoriamente dentro de un rectángulo centrado en (centro_x, centro_y)
    con el semiancho y semialto indicados. Luego se ordenan radialmente respecto
    al centroide para asegurar simplicidad.
    """
    puntos = []
    for _ in range(num_vertices):
        x = random.uniform(centro_x - semi_ancho, centro_x + semi_ancho)
        y = random.uniform(centro_y - semi_alto, centro_y + semi_alto)
        puntos.append(Punto(x, y))

    # Ordenación radial respecto al centroide
    cx = sum(p.x for p in puntos) / num_vertices
    cy = sum(p.y for p in puntos) / num_vertices
    def angulo_centroide(p):
        return math.atan2(p.y - cy, p.x - cx)
    puntos.sort(key=angulo_centroide)
    return puntos

def interseccion_real_poligonos(poly1: list[Punto], poly2: list[Punto]) -> bool:
    """
    Comprueba con un algoritmo naíf si dos polígonos simples se intersecan.
    """
    n1=len(poly1)
    n2=len(poly2)
    for i in range(n1):
        for j in range(n2):
            if segmentos_se_cortan([poly1[i],poly1[(i+1)%n1]],[poly2[j],poly2[(j+1)%n2]]):
                return True
    if punto_en_poligono(poly2[0], poly1):
        return True
    if punto_en_poligono(poly1[0], poly2):
        return True
    return False 

if __name__ == "__main__":
    random.seed(136)
    
    # Escalas fijas (semianchos y semialtos) para probar distintos tamaños
    escalas = [5, 10, 15, 20, 25, 30, 35, 40]
    CASOS_POR_ESCALA = 50
    NUM_CASOS_TOTAL = len(escalas) * CASOS_POR_ESCALA
    print(f"Ejecutando simulación con escalas {escalas} y {CASOS_POR_ESCALA} casos por escala (total {NUM_CASOS_TOTAL} escenarios)...")
    
    datos_brutos = []
    
    contadores_colisiones = {
        'Colisión Real': 0,
        'OBB': 0,
        'AABB': 0,
        'Circunferencia (Welzl)': 0,
        'Circunferencia (PCA)': 0,
        'Circunferencia (Ritter)': 0
    }
    
    metricas = {
        'OBB':            {'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0},
        'AABB':           {'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0},
        'Circunferencia (Welzl)': {'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0},
        'Circunferencia (PCA)':   {'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0},
        'Circunferencia (Ritter)':{'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0}
    }
    
    caso_id = 0
    for escala in escalas:
        for _ in range(CASOS_POR_ESCALA):
            caso_id += 1
            v_A = random.randint(3, 20)
            v_B = random.randint(3, 20)
            
            cx_A = random.uniform(-50, 50)
            cy_A = random.uniform(-50, 50)
            cx_B = random.uniform(-50, 50)
            cy_B = random.uniform(-50, 50)
            
            poly_A = generar_poligono_simple(v_A, cx_A, cy_A, escala, escala)
            poly_B = generar_poligono_simple(v_B, cx_B, cy_B, escala, escala)
            
            real_col = interseccion_real_poligonos(poly_A, poly_B)
            if real_col: contadores_colisiones['Colisión Real'] += 1
                
            obb_A = calcular_obb_minimo(poly_A)
            obb_B = calcular_obb_minimo(poly_B)
            obb_col = obb_A.test_interseccion(obb_B)
            if obb_col: contadores_colisiones['OBB'] += 1
                
            aabb_A = AABB_min_max(poly_A)
            aabb_B = AABB_min_max(poly_B)
            aabb_col = aabb_A.test_intersección(aabb_B)
            if aabb_col: contadores_colisiones['AABB'] += 1
                
            esf_rit_A = Circunferencia_Ritter(poly_A)
            esf_rit_B = Circunferencia_Ritter(poly_B)
            rit_col = esf_rit_A.test_intersección(esf_rit_B)
            if rit_col: contadores_colisiones['Circunferencia (Ritter)'] += 1
                
            esf_pca_A = Circunferencia_Ritter_PCA(poly_A)
            esf_pca_B = Circunferencia_Ritter_PCA(poly_B)
            pca_col = esf_pca_A.test_intersección(esf_pca_B)
            if pca_col: contadores_colisiones['Circunferencia (PCA)'] += 1
                
            esf_wzl_A = obtener_circunferencia(poly_A)
            esf_wzl_B = obtener_circunferencia(poly_B)
            wzl_col = esf_wzl_A.test_intersección(esf_wzl_B)
            if wzl_col: contadores_colisiones['Circunferencia (Welzl)'] += 1
                
            tests = {
                'OBB': obb_col,
                'AABB': aabb_col,
                'Circunferencia (Welzl)': wzl_col,
                'Circunferencia (PCA)': pca_col,
                'Circunferencia (Ritter)': rit_col
            }
            
            for modelo, resultado in tests.items():
                if real_col:
                    if resultado: metricas[modelo]['VP'] += 1
                    else: metricas[modelo]['FN'] += 1
                else:
                    if resultado: metricas[modelo]['FP'] += 1
                    else: metricas[modelo]['VN'] += 1
                    
            datos_brutos.append({
                'Caso': caso_id,
                'Escala': escala,
                'Colision_Real': 'Sí' if real_col else 'No',
                'OBB_Detecta': 'Sí' if obb_col else 'No',
                'AABB_Detecta': 'Sí' if aabb_col else 'No',
                'Circunferencia_Welzl_Detecta': 'Sí' if wzl_col else 'No',
                'Circunferencia_PCA_Detecta': 'Sí' if pca_col else 'No',
                'Circunferencia_Ritter_Detecta': 'Sí' if rit_col else 'No'
            })

    # Exportación a Excel
    df_brutos = pd.DataFrame(datos_brutos)
    
    resumen_listado = []
    for modelo, m in metricas.items():
        total = NUM_CASOS_TOTAL
        precision = ((m['VP'] + m['VN']) / total) * 100
        tasa_fp = (m['FP'] / total) * 100
        
        resumen_listado.append({
            'Modelo Envolvente': modelo,
            'Precisión Global (%)': round(precision, 2),
            'Verdaderos Positivos (VP)': m['VP'],
            'Verdaderos Negativos (VN)': m['VN'],
            'Falsos Positivos (FP)': m['FP'],
            'Tasa Falsos Positivos (%)': round(tasa_fp, 2),
            'Falsos Negativos (FN)': m['FN']
        })
    df_resumen = pd.DataFrame(resumen_listado)
    
    nombre_archivo = 'Comparativa_Bounding_Volumes_Escalado.xlsx'
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        df_resumen.to_excel(writer, sheet_name='Resumen_Metricas', index=False)
        df_brutos.to_excel(writer, sheet_name='Datos_Brutos', index=False)
        
        for sheet in ['Resumen_Metricas', 'Datos_Brutos']:
            ws = writer.book[sheet]
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    print(f"Tabla de datos exportada a '{nombre_archivo}'")

    # --- GRÁFICOS ADICIONALES POR ESCALA ---
    
    # 1. Agrupar datos por escala y contar colisiones para cada método
    df_brutos['Escala'] = df_brutos['Escala'].astype(int)
    agrupado = df_brutos.groupby('Escala').agg({
        'Colision_Real': lambda x: (x == 'Sí').sum(),
        'OBB_Detecta': lambda x: (x == 'Sí').sum(),
        'AABB_Detecta': lambda x: (x == 'Sí').sum(),
        'Circunferencia_Welzl_Detecta': lambda x: (x == 'Sí').sum(),
        'Circunferencia_PCA_Detecta': lambda x: (x == 'Sí').sum(),
        'Circunferencia_Ritter_Detecta': lambda x: (x == 'Sí').sum()
    }).reset_index()
    
    agrupado.columns = ['Escala', 'Real', 'OBB', 'AABB', 'Welzl', 'PCA', 'Ritter']
    
    # 2. Subplots: un diagrama de barras por escala
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()

    metodos = ['Real', 'OBB', 'AABB', 'Welzl', 'PCA', 'Ritter']
    etiquetas_metodos = ['Real', 'OBB', 'AABB', 'Circ.\nWelzl', 'Circ.\nPCA', 'Circ.\nRitter']
    colores_metodos = ['#2b6cb0', '#319795', '#4a5568', '#718096', '#a0aec0', '#cbd5e0']
    
    for idx, escala in enumerate(escalas):
        ax = axes[idx]
        datos_esc = agrupado[agrupado['Escala'] == escala]
        valores = [datos_esc[m].values[0] for m in metodos]

        barras = ax.bar(etiquetas_metodos, valores, color=colores_metodos, edgecolor='black')
        ax.set_title(f'Escala = {escala}', fontsize=10)
        ax.set_ylabel('Colisiones', fontsize=9)
        ax.set_ylim(0, CASOS_POR_ESCALA + 5)

        for barra in barras:
            alto = barra.get_height()
            ax.annotate(f'{alto}',
                        xy=(barra.get_x() + barra.get_width() / 2, alto),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center',
                        va='bottom',
                        fontsize=8)

        ax.tick_params(axis='x', rotation=0, labelsize=8)
    
    for j in range(idx + 1, len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle('Colisiones detectadas por método en cada escala', fontsize=14)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.show()
    
    # 3. Diagrama de barras global
    modelos = ['Real', 'OBB', 'AABB', 'Circ.\nWelzl', 'Circ.\nPCA', 'Circ.\nRitter']
    valores = list(contadores_colisiones.values())
    
    plt.figure(figsize=(10, 6))

    barras = plt.bar(
        modelos,
        valores,
        color=['#2b6cb0', '#319795', '#4a5568', '#718096', '#a0aec0', '#cbd5e0'],
        edgecolor='black',
        zorder=3
    )

    plt.title(
        f"Total de colisiones detectadas (todas las escalas)\nMuestra Total: {NUM_CASOS_TOTAL} escenarios",
        fontsize=13,
        pad=15
    )
    plt.ylabel("Número total de colisiones", fontsize=11, labelpad=10)
    plt.xlabel("Técnicas de volúmenes envolventes", fontsize=11, labelpad=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)

    for barra in barras:
        alto = barra.get_height()
        plt.annotate(f'{alto}',
                     xy=(barra.get_x() + barra.get_width() / 2, alto),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center',
                     va='bottom',
                     fontsize=10,
                     weight='bold')

    plt.ylim(0, max(valores) * 1.15)
    plt.tight_layout()
    plt.show()