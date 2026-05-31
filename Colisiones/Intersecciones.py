# -*- coding: utf-8 -*-
"""
Created on Mon May 18 14:53:46 2026

@author: María
"""

import random
import math
import pandas as pd
import matplotlib.pyplot as plt

from Punto import *
from OBB import calcular_obb_minimo
from AABB import AABB_min_max
from Esferas import *

def generar_poligono_simple(num_vertices: int, x_min: float, x_max: float, y_min: float, y_max: float) -> list[Punto]:
    """
    Genera un polígono simple (sin auto-intersecciones) ordenando
    puntos aleatorios radialmente respecto a su centroide.
    """
    puntos = [Punto(random.uniform(x_min, x_max), random.uniform(y_min, y_max)) for _ in range(num_vertices)]
    
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
    # Si no hay lados que se corten, se comprueba si un punto del primero está contenido
    # en el segundo y viceversa para ver si un polígono está contenido en el otro.
    if punto_en_poligono(poly2[0], poly1):
        return True
    if punto_en_poligono(poly1[0], poly2):
        return True
    return False 

if __name__ == "__main__":
    random.seed(42)
    
    NUM_CASOS = 500
    print(f"Ejecutando simulación geométrica de {NUM_CASOS} escenarios...")
    
    # Listas para almacenar los datos brutos de la simulación
    datos_brutos = []
    
    # Colisiones totales detectadas por cada método
    contadores_colisiones = {
        'Colisión Real': 0,
        'OBB': 0,
        'AABB': 0,
        'Esfera (Welzl)': 0,
        'Esfera (PCA)': 0,
        'Esfera (Ritter)': 0
    }
    
    # Estructura para almacenar matrices de confusión masivas
    metricas = {
        'OBB':            {'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0},
        'AABB':           {'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0},
        'Esfera (Welzl)': {'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0},
        'Esfera (PCA)':   {'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0},
        'Esfera (Ritter)':{'VP': 0, 'FP': 0, 'VN': 0, 'FN': 0}
    }
    
    for i in range(NUM_CASOS):
        v_A = random.randint(4, 20)
        v_B = random.randint(4, 20)
        
        # Offset variable para cubrir tanto colisiones directas como rozamientos
        offset_x = random.uniform(-20, 20)
        offset_y = random.uniform(-20, 20)
        
        poly_A = generar_poligono_simple(v_A, x_min=10, x_max=50, y_min=10, y_max=50)
        poly_B = generar_poligono_simple(v_B, x_min=20+offset_x, x_max=60+offset_x, y_min=20+offset_y, y_max=60+offset_y)
        
        # Test Geométrico Real
        real_col = interseccion_real_poligonos(poly_A, poly_B)
        if real_col: contadores_colisiones['Colisión Real'] += 1
            
        # Test OBB
        obb_A = calcular_obb_minimo(poly_A)
        obb_B = calcular_obb_minimo(poly_B)
        obb_col = obb_A.test_interseccion(obb_B)
        if obb_col: contadores_colisiones['OBB'] += 1
            
        # Test AABB
        aabb_A = AABB_min_max(poly_A)
        aabb_B = AABB_min_max(poly_B)
        aabb_col = aabb_A.test_intersección(aabb_B)
        if aabb_col: contadores_colisiones['AABB'] += 1
            
        # Tests de Esferas (Las 3 variantes)
        esf_rit_A = Esfera_Ritter(poly_A)
        esf_rit_B = Esfera_Ritter(poly_B)
        rit_col = esf_rit_A.test_intersección(esf_rit_B)
        if rit_col: contadores_colisiones['Esfera (Ritter)'] += 1
            
        esf_pca_A = RitterEigenSphere(poly_A)
        esf_pca_B = RitterEigenSphere(poly_B)
        pca_col = esf_pca_A.test_intersección(esf_pca_B)
        if pca_col: contadores_colisiones['Esfera (PCA)'] += 1
            
        esf_wzl_A = obtener_esfera(poly_A)
        esf_wzl_B = obtener_esfera(poly_B)
        wzl_col = esf_wzl_A.test_intersección(esf_wzl_B)
        if wzl_col: contadores_colisiones['Esfera (Welzl)'] += 1
            
        tests = {
            'OBB': obb_col,
            'AABB': aabb_col,
            'Esfera (Welzl)': wzl_col,
            'Esfera (PCA)': pca_col,
            'Esfera (Ritter)': rit_col
        }
        
        for modelo, resultado in tests.items():
            if real_col:
                if resultado: metricas[modelo]['VP'] += 1
                else: metricas[modelo]['FN'] += 1
            else:
                if resultado: metricas[modelo]['FP'] += 1
                else: metricas[modelo]['VN'] += 1
                
        datos_brutos.append({
            'Caso': i + 1,
            'Colision_Real': 'Sí' if real_col else 'No',
            'OBB_Detecta': 'Sí' if obb_col else 'No',
            'AABB_Detecta': 'Sí' if aabb_col else 'No',
            'Esfera_Welzl_Detecta': 'Sí' if wzl_col else 'No',
            'Esfera_PCA_Detecta': 'Sí' if pca_col else 'No',
            'Esfera_Ritter_Detecta': 'Sí' if rit_col else 'No'
        })

    # Excel
    df_brutos = pd.DataFrame(datos_brutos)
    
    resumen_listado = []
    for modelo, m in metricas.items():
        total = NUM_CASOS
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
    
    nombre_archivo = 'Comparativa_Bounding_Volumes.xlsx'
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        df_resumen.to_excel(writer, sheet_name='Resumen_Metricas', index=False)
        df_brutos.to_excel(writer, sheet_name='Datos_Brutos_500_Casos', index=False)
        
        for sheet in ['Resumen_Metricas', 'Datos_Brutos_500_Casos']:
            ws = writer.book[sheet]
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    print(f"Tabla de datos exportada a '{nombre_archivo}'")

    # Diagrama de barras
    modelos = list(contadores_colisiones.keys())
    valores = list(contadores_colisiones.values())
    
    plt.figure(figsize=(10, 6))
    
    colores = ['#2b6cb0', '#319795', '#4a5568', '#718096', '#a0aec0', '#cbd5e0']
    
    barras = plt.bar(modelos, valores, color=colores, edgecolor='black', zorder=3)
    
    plt.title(f"Comparativa de colisiones métrica\n(Muestra Total: {NUM_CASOS} Escenarios)", fontsize=13, pad=15)
    plt.ylabel("Número total de colisiones", fontsize=11, labelpad=10)
    plt.xlabel("Técnicas de volúmenes envolventes (Bounding Volumes)", fontsize=11, labelpad=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)
    
    for barra in barras:
        alto = barra.get_height()
        plt.annotate(f'{alto}',
                     xy=(barra.get_x() + barra.get_width() / 2, alto),
                     xytext=(0, 3),  # Desplazamiento vertical de 3 puntos
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=10, weight='bold')
                     
    plt.ylim(0, max(valores) * 1.15)
    
    plt.tight_layout()
    print("Desplegando el diagrama de barras comparativo en pantalla")
    plt.show()