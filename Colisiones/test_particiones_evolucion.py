# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 00:10:45 2026

@author: María
"""

import math
import random
import time
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
import sys



from Hgrid import HSHG_2D, Entidad
from MallaHash import MallaHash2D
from MallaImplícita import MallaImplicita2D
from quadtree_punteros2 import Objeto as ObjPunteros, BuildQuadtree, InsertObjeto, Punto, obtener_colisiones, obtener_candidatos
from quadtreelineal import LinearQuadtree, Punto as PuntoLineal, Objeto as ObjLineal, NodoProf


class Objeto:
    def __init__(self, id_obj, x, y, ancho, alto):
        self.id = id_obj
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.nivel = None   # se usará para HSHG

    def interseccion(self, otro):
        return not (self.x + self.ancho < otro.x or
                    otro.x + otro.ancho < self.x or
                    self.y + self.alto < otro.y or
                    otro.y + otro.alto < self.y)


def generar_objetos(n, x_min=0, x_max=100, y_min=0, y_max=100,
                    ancho_min=3, ancho_max=20, alto_min=3, alto_max=20,
                    semilla=42):
    random.seed(semilla)
    objetos = []
    for i in range(n):
        x = random.uniform(x_min, x_max - ancho_max)
        y = random.uniform(y_min, y_max - alto_max)
        ancho = random.uniform(ancho_min, ancho_max)
        alto = random.uniform(alto_min, alto_max)
        objetos.append(Objeto(i, x, y, ancho, alto))
    return objetos


def generar_mixtos(n, semilla):
    random.seed(semilla)
    objetos = []
    for i in range(n):
        if random.random() < 0.5:
            # pequeño
            ancho = random.uniform(2, 8)
            alto = random.uniform(2, 8)
        else:
            # grande
            ancho = random.uniform(15, 30)
            alto = random.uniform(15, 30)
        x = random.uniform(0, 100 - ancho)
        y = random.uniform(0, 100 - alto)
        objetos.append(Objeto(i, x, y, ancho, alto))
    return objetos


def calcular_colisiones_reales(objetos):
    colisiones = set()
    for i in range(len(objetos)):
        for j in range(i+1, len(objetos)):
            if objetos[i].interseccion(objetos[j]):
                colisiones.add(tuple(sorted((objetos[i].id, objetos[j].id))))
    return colisiones


def dimensiones_malla_implicita(objetos, tamanio_celda):
    """
    Calcula las dimensiones necesarias para la MallaImplicita2D,
    """
    if not objetos:
        return 1, 1

    max_x = max(obj.x + obj.ancho for obj in objetos)
    max_y = max(obj.y + obj.alto for obj in objetos)

    grid_width = int(math.floor(max_x / tamanio_celda)) + 1
    grid_height = int(math.floor(max_y / tamanio_celda)) + 1
    return max(1, grid_width), max(1, grid_height)


def ejecutar_para_N_con_celdas(N, ancho_min, ancho_max, alto_min, alto_max, semilla_base=42):
    objetos = generar_objetos(N, ancho_min=ancho_min, ancho_max=ancho_max,
                              alto_min=alto_min, alto_max=alto_max,
                              semilla=semilla_base + N)

    diagonales = [math.sqrt(obj.ancho**2 + obj.alto**2) for obj in objetos]
    diag_max = max(diagonales) if diagonales else 1.0
    tam_celda_diag = max(diag_max, 2.0)

    colisiones_reales = calcular_colisiones_reales(objetos)
    reales = len(colisiones_reales)

    resultados = {}

    # HSHG_2D 
    t0 = time.perf_counter()
    hgrid = HSHG_2D(tamanio_celda_min=10.0)
    for obj in objetos:
        ent = Entidad(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        hgrid.insertar(ent)
        obj.nivel = ent.nivel
    cand_hgrid = set()
    for obj in objetos:
        ent_temp = Entidad(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        ent_temp.nivel = obj.nivel
        for otro in hgrid.obtener_candidatos(ent_temp):
            if otro.id != obj.id:
                cand_hgrid.add(tuple(sorted((obj.id, otro.id))))
    t1 = time.perf_counter()
    resultados['hgrid'] = (len(cand_hgrid), t1 - t0)

    # MallaHash2D con celda 15.0
    t0 = time.perf_counter()
    mh15 = MallaHash2D(tamanio_celda=15.0)
    for obj in objetos:
        mh15.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho,
                             obj.y, obj.y+obj.alto)
    cand_hash15 = set()
    for obj in objetos:
        ids = mh15.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho,
                                               obj.y, obj.y+obj.alto)
        for otro_id in ids:
            if otro_id != obj.id:
                cand_hash15.add(tuple(sorted((obj.id, otro_id))))
    t1 = time.perf_counter()
    resultados['hash_15'] = (len(cand_hash15), t1 - t0)

    # MallaHash2D
    t0 = time.perf_counter()
    mhdiag = MallaHash2D(tamanio_celda=tam_celda_diag)
    for obj in objetos:
        mhdiag.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho,
                               obj.y, obj.y+obj.alto)
    cand_hashdiag = set()
    for obj in objetos:
        ids = mhdiag.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho,
                                                 obj.y, obj.y+obj.alto)
        for otro_id in ids:
            if otro_id != obj.id:
                cand_hashdiag.add(tuple(sorted((obj.id, otro_id))))
    t1 = time.perf_counter()
    resultados['hash_diag'] = (len(cand_hashdiag), t1 - t0)

    # MallaImplicita2D con celda 15.0 (solo tiempo y candidatos)
    t0 = time.perf_counter()
    gw, gh = dimensiones_malla_implicita(objetos, 15.0)
    mi15 = MallaImplicita2D(gw, gh, 15.0, N)
    for obj in objetos:
        mi15.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho,
                             obj.y, obj.y+obj.alto)
    cand_impl15 = set()
    for obj in objetos:
        ids = mi15.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho,
                                               obj.y, obj.y+obj.alto,
                                               id_excluir=obj.id)
        for otro_id in ids:
            if otro_id != obj.id:
                cand_impl15.add(tuple(sorted((obj.id, otro_id))))
    t1 = time.perf_counter()
    resultados['impl_15'] = (len(cand_impl15), t1 - t0)

    # MallaImplicita2D con celda diagonal
    t0 = time.perf_counter()
    gw_d, gh_d = dimensiones_malla_implicita(objetos, tam_celda_diag)
    midiag = MallaImplicita2D(gw_d, gh_d, tam_celda_diag, N)
    for obj in objetos:
        midiag.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho,
                               obj.y, obj.y+obj.alto)
    cand_impldiag = set()
    for obj in objetos:
        ids = midiag.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho,
                                                 obj.y, obj.y+obj.alto,
                                                 id_excluir=obj.id)
        for otro_id in ids:
            if otro_id != obj.id:
                cand_impldiag.add(tuple(sorted((obj.id, otro_id))))
    t1 = time.perf_counter()
    resultados['impl_diag'] = (len(cand_impldiag), t1 - t0)

    # Quadtree con punteros 
    t0 = time.perf_counter()
    centro = Punto(50.0, 50.0)
    mitad = 50.0
    prof_max = 4
    raiz = BuildQuadtree(centro, mitad, prof_max)
    for obj in objetos:
        obj_p = ObjPunteros(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        InsertObjeto(raiz, obj_p)
    cand_punteros = obtener_candidatos(raiz)
    t1 = time.perf_counter()
    resultados['punteros'] = (len(cand_punteros), t1 - t0)

    # Quadtree Lineal (solo tiempo, los candidatos son iguales a punteros)
    t0 = time.perf_counter()
    ql = LinearQuadtree(PuntoLineal(50.0, 50.0), 50.0, prof_max)
    for obj in objetos:
        obj_l = ObjLineal(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        ql.InsertObjetoLinear(obj_l)
    cand_lineal = ql.obtener_candidatos()
    t1 = time.perf_counter()
    resultados['lineal'] = (len(cand_lineal), t1 - t0)

    return reales, resultados


# Función para ejecutar barrido para una configuración de tamaños
def ejecutar_barrido(N_min=10, N_max=200, paso=20,
                     ancho_min=3, ancho_max=20, alto_min=3, alto_max=20,
                     semilla_base=42):
    Ns = list(range(N_min, N_max+1, paso))
    reales = []
    todas = ['hgrid', 'hash_15', 'hash_diag', 'impl_15', 'impl_diag', 'punteros', 'lineal']
    candidatos = {k: [] for k in todas}
    tiempos = {k: [] for k in todas}

    print(f"  Barrido con tamaños [{ancho_min}-{ancho_max}]")
    for N in Ns:
        print(f"    N={N}...", end=' ', flush=True)
        reales_n, res = ejecutar_para_N_con_celdas(N, ancho_min, ancho_max,
                                                   alto_min, alto_max, semilla_base)
        reales.append(reales_n)
        for k in todas:
            candidatos[k].append(res[k][0])
            tiempos[k].append(res[k][1])
        print(f"reales={reales_n}")
    return Ns, reales, candidatos, tiempos


# Función para ejecutar barrido con objetos mixtos
def ejecutar_barrido_mixto(N_min=10, N_max=200, paso=20, semilla_base=42):
    Ns = list(range(N_min, N_max+1, paso))
    reales = []
    todas = ['hgrid', 'hash_15', 'hash_diag', 'impl_15', 'impl_diag', 'punteros', 'lineal']
    candidatos = {k: [] for k in todas}
    tiempos = {k: [] for k in todas}

    print("  Barrido con objetos mixtos (pequeños+grandes)")
    for N in Ns:
        print(f"    N={N}...", end=' ', flush=True)
        objetos = generar_mixtos(N, semilla_base + N)
        diagonales = [math.sqrt(obj.ancho**2 + obj.alto**2) for obj in objetos]
        diag_max = max(diagonales) if diagonales else 1.0
        tam_celda_diag = max(diag_max, 2.0)

        colisiones_reales = calcular_colisiones_reales(objetos)
        reales.append(len(colisiones_reales))

        # HSHG
        t0 = time.perf_counter()
        hgrid = HSHG_2D(tamanio_celda_min=10.0)
        for obj in objetos:
            ent = Entidad(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
            hgrid.insertar(ent)
            obj.nivel = ent.nivel
        cand = set()
        for obj in objetos:
            ent_temp = Entidad(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
            ent_temp.nivel = obj.nivel
            for otro in hgrid.obtener_candidatos(ent_temp):
                if otro.id != obj.id:
                    cand.add(tuple(sorted((obj.id, otro.id))))
        t1 = time.perf_counter()
        candidatos['hgrid'].append(len(cand))
        tiempos['hgrid'].append(t1 - t0)

        # MallaHash 15
        t0 = time.perf_counter()
        mh15 = MallaHash2D(15.0)
        for obj in objetos:
            mh15.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho, obj.y, obj.y+obj.alto)
        cand = set()
        for obj in objetos:
            ids = mh15.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho, obj.y, obj.y+obj.alto)
            for oid in ids:
                if oid != obj.id:
                    cand.add(tuple(sorted((obj.id, oid))))
        t1 = time.perf_counter()
        candidatos['hash_15'].append(len(cand))
        tiempos['hash_15'].append(t1 - t0)

        # MallaHash diag
        t0 = time.perf_counter()
        mhdiag = MallaHash2D(tam_celda_diag)
        for obj in objetos:
            mhdiag.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho, obj.y, obj.y+obj.alto)
        cand = set()
        for obj in objetos:
            ids = mhdiag.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho, obj.y, obj.y+obj.alto)
            for oid in ids:
                if oid != obj.id:
                    cand.add(tuple(sorted((obj.id, oid))))
        t1 = time.perf_counter()
        candidatos['hash_diag'].append(len(cand))
        tiempos['hash_diag'].append(t1 - t0)

        # MallaImpl 15
        t0 = time.perf_counter()
        gw, gh = dimensiones_malla_implicita(objetos, 15.0)
        mi15 = MallaImplicita2D(gw, gh, 15.0, N)
        for obj in objetos:
            mi15.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho, obj.y, obj.y+obj.alto)
        cand = set()
        for obj in objetos:
            ids = mi15.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho, obj.y, obj.y+obj.alto, id_excluir=obj.id)
            for oid in ids:
                if oid != obj.id:
                    cand.add(tuple(sorted((obj.id, oid))))
        t1 = time.perf_counter()
        candidatos['impl_15'].append(len(cand))
        tiempos['impl_15'].append(t1 - t0)

        # MallaImpl diag
        t0 = time.perf_counter()
        gw_d, gh_d = dimensiones_malla_implicita(objetos, tam_celda_diag)
        midiag = MallaImplicita2D(gw_d, gh_d, tam_celda_diag, N)
        for obj in objetos:
            midiag.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho, obj.y, obj.y+obj.alto)
        cand = set()
        for obj in objetos:
            ids = midiag.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho, obj.y, obj.y+obj.alto, id_excluir=obj.id)
            for oid in ids:
                if oid != obj.id:
                    cand.add(tuple(sorted((obj.id, oid))))
        t1 = time.perf_counter()
        candidatos['impl_diag'].append(len(cand))
        tiempos['impl_diag'].append(t1 - t0)

        # Quadtree punteros
        t0 = time.perf_counter()
        centro = Punto(50.0, 50.0)
        mitad = 50.0
        prof_max = 4
        raiz = BuildQuadtree(centro, mitad, prof_max)
        for obj in objetos:
            obj_p = ObjPunteros(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
            InsertObjeto(raiz, obj_p)
        cand = obtener_candidatos(raiz)
        t1 = time.perf_counter()
        candidatos['punteros'].append(len(cand))
        tiempos['punteros'].append(t1 - t0)

        # Quadtree Lineal
        t0 = time.perf_counter()
        ql = LinearQuadtree(PuntoLineal(50.0, 50.0), 50.0, prof_max)
        for obj in objetos:
            obj_l = ObjLineal(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
            ql.InsertObjetoLinear(obj_l)
        cand = ql.obtener_candidatos()
        t1 = time.perf_counter()
        candidatos['lineal'].append(len(cand))
        tiempos['lineal'].append(t1 - t0)

        print(f"reales={len(colisiones_reales)}")
    return Ns, reales, candidatos, tiempos


# Función para generar las tres figuras independientes
def generar_figuras(resultados_por_config):
    # Estructuras que se muestran en candidatos y factor
    mostrar = ['hgrid', 'hash_15', 'hash_diag', 'punteros']
    nombres_mostrar = ['HSHG_2D', 'Hash(15)', 'Hash(diag)', 'Punteros']
    colores_mostrar = ['#1f77b4', '#ff7f0e', '#ffbb78', '#d62728']
    marcadores_mostrar = ['o', 's', 's', 'd']
    estilos_mostrar = ['-', '-', '--', '-']

    # Todas las estructuras para tiempos
    todas_tiempo = ['hgrid', 'hash_15', 'hash_diag', 'impl_15', 'impl_diag', 'punteros', 'lineal']
    nombres_tiempo = ['HSHG_2D', 'Hash(15)', 'Hash(diag)', 'Impl(15)', 'Impl(diag)', 'Punteros', 'Lineal']
    colores_tiempo = ['#1f77b4', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#9467bd']
    marcadores_tiempo = ['o', 's', 's', '^', '^', 'd', '*']
    estilos_tiempo = ['-', '-', '--', '-', '--', '-', '-']

    configs = list(resultados_por_config.keys())
    Ns_dict = {cfg: resultados_por_config[cfg][0] for cfg in configs}
    reales_dict = {cfg: resultados_por_config[cfg][1] for cfg in configs}
    cand_dict = {cfg: resultados_por_config[cfg][2] for cfg in configs}
    time_dict = {cfg: resultados_por_config[cfg][3] for cfg in configs}

    # Figura 1: Candidatos
    fig1, axes1 = plt.subplots(1, 3, figsize=(18, 5))
    for col, cfg in enumerate(configs):
        ax = axes1[col]
        Ns = Ns_dict[cfg]
        reales = reales_dict[cfg]
        ax.plot(Ns, reales, 'k-', linewidth=2, label='Colisiones reales')
        for idx, est in enumerate(mostrar):
            ax.plot(Ns, cand_dict[cfg][est],
                    marker=marcadores_mostrar[idx], linestyle=estilos_mostrar[idx],
                    color=colores_mostrar[idx], label=nombres_mostrar[idx],
                    linewidth=1.5, markersize=4)
        ax.set_xlabel('Número de objetos')
        ax.set_ylabel('Número de pares')
        ax.set_title(f'Configuración: {cfg}')
        ax.legend(loc='upper left', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
    fig1.suptitle('Evolución de pares candidatos', fontsize=14, weight='bold')
    plt.tight_layout()
    plt.show()

    # Figura 2: Factor de sobrecarga 
    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
    for col, cfg in enumerate(configs):
        ax = axes2[col]
        Ns = Ns_dict[cfg]
        reales = reales_dict[cfg]
        for idx, est in enumerate(mostrar):
            factor = [c/r if r>0 else np.nan for c,r in zip(cand_dict[cfg][est], reales)]
            ax.plot(Ns, factor,
                    marker=marcadores_mostrar[idx], linestyle=estilos_mostrar[idx],
                    color=colores_mostrar[idx], label=nombres_mostrar[idx],
                    linewidth=1.5, markersize=4)
        ax.axhline(y=1.0, color='k', linestyle='--', linewidth=1.5, label='Ideal')
        ax.set_xlabel('Número de objetos')
        ax.set_ylabel('Relación candidatos y colisiones (candidatos / reales)')
        ax.set_title(f'Configuración: {cfg}')
        ax.legend(loc='upper left', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
    fig2.suptitle('Relación candidatos y colisiones', fontsize=14, weight='bold')
    plt.tight_layout()
    plt.show()

    # Figura 3: Tiempos
    fig3, axes3 = plt.subplots(1, 3, figsize=(18, 5))
    for col, cfg in enumerate(configs):
        ax = axes3[col]
        Ns = Ns_dict[cfg]
        for idx, est in enumerate(todas_tiempo):
            ax.plot(Ns, time_dict[cfg][est],
                    marker=marcadores_tiempo[idx], linestyle=estilos_tiempo[idx],
                    color=colores_tiempo[idx], label=nombres_tiempo[idx],
                    linewidth=1.5, markersize=4)
        ax.set_xlabel('Número de objetos')
        ax.set_ylabel('Tiempo (segundos)')
        ax.set_title(f'Configuración: {cfg}')
        ax.legend(loc='upper left', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
    fig3.suptitle('Tiempo de ejecución (obtención de candidatos)', fontsize=14, weight='bold')
    plt.tight_layout()
    plt.show()


# Función principal
def comparar_evolucion_distribuciones(N_min=10, N_max=200, paso=20):
    resultados = {}

    # 1. Objetos pequeños (2-8)
    print("\n=== CONFIGURACIÓN: PEQUEÑOS (2-8) ===")
    Ns_peq, reales_peq, cand_peq, time_peq = ejecutar_barrido(
        N_min, N_max, paso, 2, 8, 2, 8, semilla_base=42)
    resultados['Pequeños'] = (Ns_peq, reales_peq, cand_peq, time_peq)

    # 2. Objetos grandes (15-30)
    print("\n=== CONFIGURACIÓN: GRANDES (15-30) ===")
    Ns_gran, reales_gran, cand_gran, time_gran = ejecutar_barrido(
        N_min, N_max, paso, 15, 30, 15, 30, semilla_base=100)
    resultados['Grandes'] = (Ns_gran, reales_gran, cand_gran, time_gran)

    # 3. Mezcla (pequeños y grandes al 50%)
    print("\n=== CONFIGURACIÓN: MEZCLA (50% pequeños, 50% grandes) ===")
    Ns_mix, reales_mix, cand_mix, time_mix = ejecutar_barrido_mixto(
        N_min, N_max, paso, semilla_base=200)
    resultados['Mixtos'] = (Ns_mix, reales_mix, cand_mix, time_mix)

    generar_figuras(resultados)


if __name__ == "__main__":
    comparar_evolucion_distribuciones(N_min=10, N_max=200, paso=20)
