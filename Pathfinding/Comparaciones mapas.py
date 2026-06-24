# -*- coding: utf-8 -*-
"""
Script de comparación de algoritmos de búsqueda de caminos en entornos dinámicos.
Incluye mapas con diferentes estructuras: espiral (meta en centro), aleatorio y líneas.
Compara A* (estático), D* Lite y Anytime Dynamic A* con distintas tolerancias (epsilon)
y límites de tiempo (t_max). Genera gráficas de tiempos de cómputo y longitudes de camino.
Además, visualiza la evolución de los mapas a lo largo de los cambios y, al final,
dibuja los caminos obtenidos por cada algoritmo sobre el mapa final.
"""

import time
import random
import copy
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
from matplotlib.ticker import MaxNLocator  # <-- NUEVO

# Importaciones de los módulos proporcionados
from mapa import Cuadricula
from AlgoritmosEstaticos import A_estrella
from DLite import DLite
from AnytimeA import AnytimeA


# ---------- Funciones auxiliares ----------

def asegurar_camino(mapa, inicio, fin):
    """
    Modifica el mapa (in-place) para garantizar que exista un camino entre inicio y fin.
    Si ya existe, no hace nada. Si no, abre (pone a 1) las celdas de una ruta teórica.
    """
    ancho = len(mapa[0])
    alto = len(mapa)
    # BFS para ver si hay camino
    visitado = [[False]*ancho for _ in range(alto)]
    cola = deque()
    cola.append(inicio)
    visitado[inicio[1]][inicio[0]] = True
    parent = {inicio: None}
    while cola:
        x, y = cola.popleft()
        if (x, y) == fin:
            return  # Ya hay camino
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < ancho and 0 <= ny < alto and not visitado[ny][nx] and mapa[ny][nx] != float('inf'):
                visitado[ny][nx] = True
                parent[(nx, ny)] = (x, y)
                cola.append((nx, ny))
    # No hay camino, construir uno teórico (ignorando obstáculos)
    visitado2 = [[False]*ancho for _ in range(alto)]
    cola2 = deque()
    cola2.append(inicio)
    visitado2[inicio[1]][inicio[0]] = True
    parent2 = {inicio: None}
    while cola2:
        x, y = cola2.popleft()
        if (x, y) == fin:
            path = []
            cur = fin
            while cur is not None:
                path.append(cur)
                cur = parent2[cur]
            for (px, py) in path:
                mapa[py][px] = 1
            return
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < ancho and 0 <= ny < alto and not visitado2[ny][nx]:
                visitado2[ny][nx] = True
                parent2[(nx, ny)] = (x, y)
                cola2.append((nx, ny))


def generar_cambios(mapa, inicio, fin, num_cambios=20, seed=42):
    """
    Genera una lista de cambios consistentes en añadir o eliminar obstáculos.
    No se mueve el inicio.
    """
    random.seed(seed)
    cambios = []
    ancho = len(mapa[0])
    alto = len(mapa)
    celdas_libres = [(x,y) for x in range(ancho) for y in range(alto) 
                     if mapa[y][x] != float('inf') and (x,y) != inicio and (x,y) != fin]
    celdas_obstaculo = [(x,y) for x in range(ancho) for y in range(alto) 
                        if mapa[y][x] == float('inf')]
    
    for _ in range(num_cambios):
        if celdas_libres and (not celdas_obstaculo or random.random() < 0.5):
            celda = random.choice(celdas_libres)
            cambios.append({'tipo': 'toggle', 'x': celda[0], 'y': celda[1], 'es_obstaculo': True})
            celdas_libres.remove(celda)
            celdas_obstaculo.append(celda)
        elif celdas_obstaculo:
            celda = random.choice(celdas_obstaculo)
            cambios.append({'tipo': 'toggle', 'x': celda[0], 'y': celda[1], 'es_obstaculo': False})
            celdas_obstaculo.remove(celda)
            celdas_libres.append(celda)
        else:
            if celdas_libres:
                celda = random.choice(celdas_libres)
                cambios.append({'tipo': 'toggle', 'x': celda[0], 'y': celda[1], 'es_obstaculo': True})
                celdas_libres.remove(celda)
                celdas_obstaculo.append(celda)
    return cambios


# ---------- Generadores de mapas ----------

def generar_mapa_aleatorio(ancho, alto, prob_obstaculo=0.2):
    mapa = []
    for y in range(alto):
        fila = []
        for x in range(ancho):
            if random.random() < prob_obstaculo:
                fila.append(float('inf'))
            else:
                fila.append(1)
        mapa.append(fila)
    return mapa

def generar_mapa_lineas(ancho, alto, num_verticales=5, num_horizontales=3, max_longitud_factor=0.8):
    """
    Genera un mapa con líneas de diferentes tamaños.
    - Líneas verticales: comienzan en la parte superior (y=0) y bajan una longitud aleatoria.
    - Líneas horizontales: comienzan en la izquierda (x=0) y avanzan una longitud aleatoria.
    """
    mapa = [[1 for _ in range(ancho)] for _ in range(alto)]
    
    # Líneas verticales desde la parte superior
    for _ in range(num_verticales):
        x = random.randint(0, ancho-1)
        longitud = random.randint(3, int(alto * max_longitud_factor))
        for y in range(longitud):
            if y < alto:
                mapa[y][x] = float('inf')
    
    # Líneas horizontales desde la izquierda
    for _ in range(num_horizontales):
        y = random.randint(0, alto-1)
        longitud = random.randint(1, int(ancho * max_longitud_factor))
        for x in range(longitud):
            if x < ancho:
                mapa[y][x] = float('inf')
    
    # Aseguramos inicio y meta
    mapa[0][0] = 1
    mapa[alto-1][ancho-1] = 1
    return mapa

def generar_mapa_espiral_centro(ancho, alto):
    """
    Crea un mapa con un corredor en espiral continuo desde (0,0) hasta el centro.
    El resto de celdas quedan como obstáculos (inf).
    """
    mapa = [[float('inf') for _ in range(ancho)] for _ in range(alto)]
    top, bottom = 0, alto - 1
    left, right = 0, ancho - 1
    
    while top <= bottom and left <= right:
        for i in range(left, right + 1):
            mapa[top][i] = 1
        top += 2
        if top > bottom or left > right: break
        for i in range(top - 1, bottom + 1):
            mapa[i][right] = 1
        right -= 2
        if top > bottom or left > right: break
        for i in range(right + 1, left - 1, -1):
            mapa[bottom][i] = 1
        bottom -= 2
        if top > bottom or left > right: break
        for i in range(bottom + 1, top - 1, -1):
            mapa[i][left] = 1
        left += 2
        if top <= bottom and left <= right:
            mapa[top][left - 1] = 1
            
    center_x, center_y = ancho // 2, alto // 2
    mapa[center_y][center_x] = 1
    return mapa


# ---------- Visualización de la evolución del mapa ----------

def dibujar_mapa(mapa, inicio, fin, titulo, ax=None, camino=None):
    """
    Dibuja un mapa en un eje de matplotlib. 
    Si se proporciona camino, lo superpone en azul.
    Convención: negro = obstáculo, blanco = libre.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    ancho = len(mapa[0])
    alto = len(mapa)
    img = np.zeros((alto, ancho))
    for y in range(alto):
        for x in range(ancho):
            if mapa[y][x] == float('inf'):
                img[y, x] = 0  # negro = obstáculo
            else:
                img[y, x] = 1  # blanco = libre
    ax.imshow(img, cmap='gray', origin='upper', vmin=0, vmax=1)
    ax.scatter(inicio[0], inicio[1], c='green', s=100, marker='s', label='Inicio', edgecolors='black')
    ax.scatter(fin[0], fin[1], c='red', s=100, marker='*', label='Meta', edgecolors='black')
    if camino:
        px, py = zip(*camino)
        ax.plot(px, py, c='blue', linewidth=2, alpha=0.7, label='Camino')
    ax.set_title(titulo)
    ax.axis('off')
    if ax is None:
        plt.tight_layout()
        plt.show()
    return ax

def visualizar_evolucion(mapa_inicial, cambios, inicio, fin, titulo_mapa, num_frames=6):
    """
    Muestra la evolución del mapa a lo largo de los cambios.
    (Opcionalmente se puede dibujar el camino de A* en cada frame descomentando las líneas)
    """
    mapa_actual = copy.deepcopy(mapa_inicial)
    total_cambios = len(cambios)
    indices = [0]
    if total_cambios > 0:
        step = max(1, total_cambios // (num_frames - 1))
        for i in range(1, num_frames - 1):
            idx = min(i * step, total_cambios)
            if idx not in indices:
                indices.append(idx)
        indices.append(total_cambios)
    indices = sorted(set(indices))
    
    num_subplots = len(indices)
    fig, axes = plt.subplots(1, num_subplots, figsize=(4*num_subplots, 4))
    if num_subplots == 1:
        axes = [axes]
    
    for idx, ax in zip(indices, axes):
        mapa_temp = copy.deepcopy(mapa_inicial)
        for i in range(idx):
            c = cambios[i]
            mapa_temp[c['y']][c['x']] = float('inf') if c['es_obstaculo'] else 1
        # Opcional: calcular y dibujar camino de A* en cada frame
        # cuad = Cuadricula(mapa_temp)
        # _, camino, _ = A_estrella(cuad, inicio, fin)
        # dibujar_mapa(mapa_temp, inicio, fin, f'{titulo_mapa}\nCambio {idx}/{total_cambios}', ax, camino)
        dibujar_mapa(mapa_temp, inicio, fin, f'{titulo_mapa}\nCambio {idx}/{total_cambios}', ax, camino=None)
    
    plt.suptitle(f'Evolución del mapa: {titulo_mapa}', fontsize=14)
    plt.tight_layout()
    plt.show()


# ---------- Visualización comparativa de caminos finales ----------

def visualizar_caminos_finales(mapa_final, inicio, fin, configs, titulo_mapa):
    """
    Dibuja el mapa final con los caminos obtenidos por cada configuración de algoritmo.
    Muestra hasta 8 configuraciones en una cuadrícula de 2 filas x 4 columnas.
    """
    n_configs = len(configs)
    # Si son menos de 8, rellenamos con None para mantener la estructura, pero aquí asumimos 8
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))  # 2 filas, 4 columnas
    axes = axes.flatten()  # Convertir en lista de 8 ejes
    
    for idx, cfg in enumerate(configs):
        if idx >= len(axes):
            break  # Por seguridad
        ax = axes[idx]
        # Ejecutar algoritmo
        if cfg['tipo'] == 'A*':
            _, camino, _ = A_estrella(Cuadricula(mapa_final), inicio, fin)
        elif cfg['tipo'] == 'D* Lite':
            dstar = DLite(Cuadricula(mapa_final), inicio, fin)
            camino = dstar.camino_hasta()
        elif cfg['tipo'] == 'AnytimeA':
            any_a = AnytimeA(Cuadricula(mapa_final), inicio, fin,
                             epsilon=cfg.get('epsilon', 1.0),
                             t_max=cfg.get('t_max', float('inf')))
            camino = any_a.camino_hasta()
        else:
            camino = None
        
        dibujar_mapa(mapa_final, inicio, fin, cfg['nombre'], ax, camino=camino)
    
    # Ocultar los subplots sobrantes si configs < 8 (no debería ocurrir)
    for j in range(len(configs), len(axes)):
        axes[j].axis('off')
    
    plt.suptitle(f'Caminos en mapa {titulo_mapa} (estado final)', fontsize=16)
    plt.tight_layout()
    plt.show()


# ---------- Ejecución de un algoritmo en un mapa dinámico ----------

def ejecutar_algoritmo(nombre, mapa_inicial, inicio, fin, cambios, **kwargs):
    """
    Ejecuta un algoritmo a lo largo de una secuencia de cambios (toggle).
    Retorna dos listas: tiempos (por cambio) y longitudes (después de cada cambio).
    El tiempo de cada cambio es el tiempo que tarda en recomputar el camino tras aplicar ese cambio.
    """
    tiempos = []
    longitudes = []
    mapa_actual = copy.deepcopy(mapa_inicial)
    
    if nombre == 'A*':
        t0 = time.perf_counter()
        dist, camino, _ = A_estrella(Cuadricula(mapa_actual), inicio, fin)
        t1 = time.perf_counter()
        tiempos.append(t1 - t0)
        longitudes.append(len(camino) if camino else float('inf'))
        
        for cambio in cambios:
            x, y = cambio['x'], cambio['y']
            es_obstaculo = cambio['es_obstaculo']
            mapa_actual[y][x] = float('inf') if es_obstaculo else 1
            t0 = time.perf_counter()
            dist, camino, _ = A_estrella(Cuadricula(mapa_actual), inicio, fin)
            t1 = time.perf_counter()
            tiempos.append(t1 - t0)
            longitudes.append(len(camino) if camino else float('inf'))
    
    elif nombre == 'D* Lite':
        t0 = time.perf_counter()
        dstar = DLite(Cuadricula(mapa_actual), inicio, fin)
        t1 = time.perf_counter()
        tiempos.append(t1 - t0)
        camino = dstar.camino_hasta()
        longitudes.append(len(camino) if camino else float('inf'))
        
        for cambio in cambios:
            x, y = cambio['x'], cambio['y']
            es_obstaculo = cambio['es_obstaculo']
            t0 = time.perf_counter()
            dstar.update_cell(x, y, es_obstaculo, recalcular=True)
            t1 = time.perf_counter()
            tiempos.append(t1 - t0)
            camino = dstar.camino_hasta()
            longitudes.append(len(camino) if camino else float('inf'))
    
    elif nombre.startswith('AnytimeA'):
        epsilon = kwargs.get('epsilon', 1.0)
        t_max = kwargs.get('t_max', float('inf'))
        mejorar = kwargs.get('mejorar', False)
        
        t0 = time.perf_counter()
        any_a = AnytimeA(Cuadricula(mapa_actual), inicio, fin, epsilon=epsilon, t_max=t_max)
        t1 = time.perf_counter()
        tiempos.append(t1 - t0)
        camino = any_a.camino_hasta()
        longitudes.append(len(camino) if camino else float('inf'))
        
        for cambio in cambios:
            x, y = cambio['x'], cambio['y']
            es_obstaculo = cambio['es_obstaculo']
            t0 = time.perf_counter()
            any_a.update_cell(x, y, es_obstaculo, recalcular=True)
            t1 = time.perf_counter()
            tiempos.append(t1 - t0)
            if mejorar and any_a.epsilon > 1:
                any_a.improve_path(disminuir_tolerancia=0.5)
            camino = any_a.camino_hasta()
            longitudes.append(len(camino) if camino else float('inf'))
    
    return tiempos, longitudes


# ---------- Experimento principal ----------

def experimento():
    # Parámetros generales
    ANCHO, ALTO = 30, 30
    NUM_CAMBIOS = 20
    SEED = 130
    random.seed(SEED)
    
    # Tipos de mapa
    mapas = {}
    
    # 1. Aleatorio
    mapa_rand = generar_mapa_aleatorio(ANCHO, ALTO, prob_obstaculo=0.2)
    inicio = (0, 0)
    fin = (ANCHO-1, ALTO-1)
    asegurar_camino(mapa_rand, inicio, fin)
    mapas['Aleatorio'] = (mapa_rand, inicio, fin)
    
    # 2. Líneas (nueva versión con líneas desde arriba/izquierda)
    mapa_lineas = generar_mapa_lineas(ANCHO, ALTO, num_verticales=8, num_horizontales=4, max_longitud_factor=0.7)
    asegurar_camino(mapa_lineas, inicio, fin)
    mapas['Líneas'] = (mapa_lineas, inicio, fin)
    
    # 3. Espiral con meta en el centro
    mapa_espiral = generar_mapa_espiral_centro(ANCHO, ALTO)
    inicio_esp = (0, 0)
    fin_esp = (ANCHO//2, ALTO//2)
    mapas['Espiral (centro)'] = (mapa_espiral, inicio_esp, fin_esp)
    
    # Generar cambios y visualizar evolución para cada mapa
    cambios_por_mapa = {}
    for nombre, (mapa, ini, fin_m) in mapas.items():
        cambios = generar_cambios(mapa, ini, fin_m, num_cambios=NUM_CAMBIOS, seed=SEED)
        cambios_por_mapa[nombre] = cambios
        visualizar_evolucion(mapa, cambios, ini, fin_m, nombre, num_frames=5)
    
    # Configuraciones de algoritmos para pruebas de rendimiento (sin t_max=0.001)
    configs = [
        {'nombre': 'A*', 'tipo': 'A*'},
        {'nombre': 'D* Lite', 'tipo': 'D* Lite'},
        {'nombre': 'AnytimeA eps=1.0', 'tipo': 'AnytimeA', 'epsilon': 1.0, 't_max': float('inf'), 'mejorar': False},
        # Eliminada la configuración con t_max=0.001
        {'nombre': 'AnytimeA eps=2.0 t=0.01', 'tipo': 'AnytimeA', 'epsilon': 2.0, 't_max': 0.01, 'mejorar': False},
        {'nombre': 'AnytimeA eps=2.0 t=0.1', 'tipo': 'AnytimeA', 'epsilon': 2.0, 't_max': 0.1, 'mejorar': False},
        {'nombre': 'AnytimeA eps=3.0 t=0.01', 'tipo': 'AnytimeA', 'epsilon': 3.0, 't_max': 0.01, 'mejorar': False},
        {'nombre': 'AnytimeA eps=5.0 t=0.01', 'tipo': 'AnytimeA', 'epsilon': 5.0, 't_max': 0.01, 'mejorar': False},
        {'nombre': 'AnytimeA eps=2.0 t=0.01 mejora', 'tipo': 'AnytimeA', 'epsilon': 2.0, 't_max': 0.01, 'mejorar': True},
    ]
    
    # Almacenar resultados: {nombre_mapa: {nombre_config: (tiempos, longitudes)}}
    resultados = {}
    
    for nombre_mapa, (mapa_inicial, ini, fin_m) in mapas.items():
        print(f"\n--- Procesando mapa: {nombre_mapa} ---")
        cambios = cambios_por_mapa[nombre_mapa]
        resultados[nombre_mapa] = {}
        for cfg in configs:
            print(f"  Ejecutando {cfg['nombre']}...")
            if cfg['tipo'] == 'A*':
                tiempos, longitudes = ejecutar_algoritmo('A*', mapa_inicial, ini, fin_m, cambios)
            elif cfg['tipo'] == 'D* Lite':
                tiempos, longitudes = ejecutar_algoritmo('D* Lite', mapa_inicial, ini, fin_m, cambios)
            elif cfg['tipo'] == 'AnytimeA':
                tiempos, longitudes = ejecutar_algoritmo(
                    'AnytimeA', mapa_inicial, ini, fin_m, cambios,
                    epsilon=cfg['epsilon'], t_max=cfg['t_max'], mejorar=cfg.get('mejorar', False)
                )
            resultados[nombre_mapa][cfg['nombre']] = (tiempos, longitudes)
    
    # Graficar resultados de rendimiento
    for nombre_mapa, data in resultados.items():
        configs_longitudes = [
            'A*',
            'D* Lite',
            'AnytimeA eps=1.0',
            'AnytimeA eps=2.0 t=0.01',
            'AnytimeA eps=2.0 t=0.1',
            'AnytimeA eps=3.0 t=0.01',
            'AnytimeA eps=5.0 t=0.01',
            'AnytimeA eps=2.0 t=0.01 mejora'
        ]
        
        # Crear un ciclo de estilos para distinguir mejor las líneas
        estilos = [
            {'color': 'blue', 'linestyle': '-', 'marker': 'o', 'markersize': 4},
            {'color': 'red', 'linestyle': '-', 'marker': 's', 'markersize': 4},
            {'color': 'green', 'linestyle': '--', 'marker': '^', 'markersize': 4},
            {'color': 'purple', 'linestyle': '-.', 'marker': 'd', 'markersize': 4},
            {'color': 'orange', 'linestyle': ':', 'marker': 'p', 'markersize': 4},
            {'color': 'brown', 'linestyle': '-', 'marker': '*', 'markersize': 5},
            {'color': 'cyan', 'linestyle': '--', 'marker': 'X', 'markersize': 5},
            {'color': 'magenta', 'linestyle': '-.', 'marker': 'P', 'markersize': 5},
            {'color': 'olive', 'linestyle': ':', 'marker': 'h', 'markersize': 5},
        ]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle(f'Comparación en mapa {nombre_mapa}', fontsize=14)
        
        # ---- Gráfica de tiempos (mostramos todas las configuraciones) ----
        for idx, (alg_nombre, (tiempos, longitudes)) in enumerate(data.items()):
            estilo = estilos[idx % len(estilos)]
            ax1.plot(range(len(tiempos)), tiempos, 
                     color=estilo['color'], linestyle=estilo['linestyle'],
                     marker=estilo['marker'], markersize=estilo['markersize'],
                     label=alg_nombre, alpha=0.8)
        ax1.set_xlabel('Número de cambio (0 = inicial)')
        ax1.set_ylabel('Tiempo de cómputo (s)')
        ax1.legend(loc='upper left', fontsize=7, ncol=2)  # ncol=2 para ahorrar espacio vertical
        ax1.grid(True, linestyle='--', alpha=0.6)
        
        # ---- Gráfica de longitudes (solo las configuraciones seleccionadas) ----
        for idx, alg_nombre in enumerate(configs_longitudes):
            if alg_nombre in data:
                tiempos, longitudes = data[alg_nombre]
                estilo = estilos[idx % len(estilos)]
                ax2.plot(range(len(longitudes)), longitudes,
                         color=estilo['color'], linestyle=estilo['linestyle'],
                         marker=estilo['marker'], markersize=estilo['markersize'],
                         label=alg_nombre, alpha=0.8)
        ax2.set_xlabel('Número de cambio (0 = inicial)')
        ax2.set_ylabel('Longitud del camino')
        ax2.legend(loc='upper left', fontsize=7, ncol=2)
        ax2.grid(True, linestyle='--', alpha=0.6)
        
        # ---- Ajuste de ticks a valores enteros ----
        num_points = len(next(iter(data.values()))[0])  # longitud de tiempos de cualquier algoritmo
        ax1.set_xticks(range(num_points))
        ax2.set_xticks(range(num_points))
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        plt.tight_layout()
        plt.savefig(f'comparacion_{nombre_mapa}.png', dpi=150)
        plt.show()
    
    # Resumen estadístico
    print("\n--- Resumen de tiempos medios por cambio (excluyendo el inicial) ---")
    for nombre_mapa, data in resultados.items():
        print(f"\nMapa: {nombre_mapa}")
        for alg_nombre, (tiempos, longitudes) in data.items():
            if len(tiempos) > 1:
                tiempo_promedio = sum(tiempos[1:]) / len(tiempos[1:])
                long_promedio = sum(longitudes[1:]) / len(longitudes[1:]) if longitudes[1:] else float('inf')
            else:
                tiempo_promedio = tiempos[0]
                long_promedio = longitudes[0]
            print(f"  {alg_nombre}: tiempo medio = {tiempo_promedio:.6f}s, longitud media = {long_promedio:.2f}")
    
    # ---------- VISUALIZACIÓN DE CAMINOS FINALES ----------
    # Seleccionamos algunas configuraciones representativas (sin t_max=0.001)
    configs_visualizacion = [
        {'nombre': 'A*', 'tipo': 'A*'},
        {'nombre': 'D* Lite', 'tipo': 'D* Lite'},
        {'nombre': 'AnytimeA ε=1', 'tipo': 'AnytimeA', 'epsilon': 1.0, 't_max': float('inf')},
        {'nombre': 'AnytimeA ε=2 t=0.01', 'tipo': 'AnytimeA', 'epsilon': 2.0, 't_max': 0.01},
        {'nombre': 'AnytimeA ε=2 t=0.01 mejora', 'tipo': 'AnytimeA', 'epsilon': 2.0, 't_max': 0.01, 'mejorar': True},
        {'nombre': 'AnytimeA ε=2 t=0.1', 'tipo': 'AnytimeA', 'epsilon': 2.0, 't_max': 0.1},
        {'nombre': 'AnytimeA ε=3 t=0.01', 'tipo': 'AnytimeA', 'epsilon': 3.0, 't_max': 0.01},
        {'nombre': 'AnytimeA ε=5 t=0.01', 'tipo': 'AnytimeA', 'epsilon': 5.0, 't_max': 0.01},
    ]
    
    for nombre_mapa, (mapa_inicial, ini, fin_m) in mapas.items():
        # Reconstruir el mapa final aplicando todos los cambios
        mapa_final = copy.deepcopy(mapa_inicial)
        for c in cambios_por_mapa[nombre_mapa]:
            mapa_final[c['y']][c['x']] = float('inf') if c['es_obstaculo'] else 1
        visualizar_caminos_finales(mapa_final, ini, fin_m, configs_visualizacion, nombre_mapa)


if __name__ == "__main__":
    experimento()