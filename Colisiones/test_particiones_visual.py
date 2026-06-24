# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 20:43:24 2026

@author: María
"""

import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from pathlib import Path

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


def dibujar_referencia(objetos, colisiones_reales):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title("Referencia (sin partición) - Fuerza Bruta", fontsize=12, weight='bold')
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_xlim(0, 100)
    ax.set_ylim(100, 0)

    for obj in objetos:
        en_colision = any(obj.id in par for par in colisiones_reales)
        color = '#e53e3e' if en_colision else '#718096'
        grosor = 2.5 if en_colision else 1.0
        rect = patches.Rectangle((obj.x, obj.y), obj.ancho, obj.alto,
                                 edgecolor=color, facecolor='#f7fafc',
                                 linewidth=grosor, alpha=0.5)  # Transparencia
        ax.add_patch(rect)
        ax.text(obj.x + obj.ancho/2, obj.y + obj.alto/2,
                f"{obj.id}", fontsize=9, ha='center', va='center',
                color='#2d3748', weight='bold')
    ax.text(2, 2, f"Colisiones reales: {len(colisiones_reales)}", fontsize=10,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    plt.tight_layout()
    plt.show()


def dibujar_hgrid(hgrid, objetos, colisiones_reales, colisiones_detectadas, candidatos):
    niveles_activos = [n for n in range(4) if (hgrid.niveles_ocupados_mask >> n) & 1]
    if not niveles_activos:
        niveles_activos = [0]

    n = len(niveles_activos)
    ncols = 2 if n > 1 else 1
    nrows = (n + 1) // 2
    fig, axs = plt.subplots(nrows, ncols, figsize=(10, 5*nrows))
    if nrows == 1 and ncols == 1:
        axs = [axs]
    else:
        axs = axs.ravel()

    limites = (-5, 105)
    colores_nivel = {0: "#3182ce", 1: "#e53e3e", 2: "#319795", 3: "#d69e2e"}

    for idx, nivel in enumerate(niveles_activos):
        ax = axs[idx]
        tc = hgrid._obtener_tamanio_celda(nivel)
        ax.set_title(f"Nivel {nivel}  —  celda {tc:.1f}×{tc:.1f}", fontsize=10, weight='bold')
        ax.invert_yaxis()
        ax.set_aspect('equal')
        ax.set_xlim(limites)
        ax.set_ylim(limites[1], limites[0])

        col = colores_nivel.get(nivel, "#cbd5e0")
        cx_min = int(math.floor(limites[0] / tc))
        cx_max = int(math.ceil(limites[1] / tc))
        for c in range(cx_min, cx_max + 1):
            coord = c * tc
            ax.axvline(coord, color=col, linestyle=":", linewidth=0.7, alpha=0.8)
            ax.axhline(coord, color=col, linestyle=":", linewidth=0.7, alpha=0.8)

        for obj in objetos:
            en_colision = any(obj.id in par for par in colisiones_detectadas)
            if obj.nivel == nivel:
                color_borde = '#e53e3e' if en_colision else col
                grosor = 2.5 if en_colision else 1.8
                facecolor = '#ebf8ff' if not en_colision else '#fff5f5'
            else:
                color_borde = '#cbd5e0'
                grosor = 0.8
                facecolor = 'none'
            rect = patches.Rectangle((obj.x, obj.y), obj.ancho, obj.alto,
                                     edgecolor=color_borde, facecolor=facecolor,
                                     linewidth=grosor, alpha=0.7)
            ax.add_patch(rect)
            if obj.nivel == nivel:
                ax.text(obj.x + obj.ancho/2, obj.y + obj.alto/2,
                        f"{obj.id}", fontsize=8, ha='center', va='center',
                        color='#2d3748', weight='bold')

    # Ocultar ejes vacíos
    for j in range(len(niveles_activos), len(axs)):
        axs[j].axis('off')

    # Información resumida: aparece UNA SOLA VEZ en la figura
    aciertos = len(colisiones_detectadas.intersection(colisiones_reales))
    info = (f"Candidatos: {len(candidatos)}\n"
            f"Detectadas: {len(colisiones_detectadas)}\n"
            f"Aciertos: {aciertos}/{len(colisiones_reales)}")
    fig.text(0.98, 0.02, info, fontsize=10,
             bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'),
             ha='right', va='bottom')

    plt.suptitle("HSHG_2D — Niveles de la jerarquía", fontsize=14, weight='bold')
    plt.tight_layout()
    plt.show()


def dibujar_malla_hash(malla, objetos, colisiones_reales, colisiones_detectadas, pares_candidatos):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title("MallaHash2D (Hash uniforme)", fontsize=12, weight='bold')
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_xlim(-10, 110)
    ax.set_ylim(110, -10)

    tc = malla.tamanio_celda
    for x in np.arange(-10, 110, tc):
        ax.axvline(x, color="#cbd5e0", linestyle="--", linewidth=0.8, alpha=0.8)
    for y in np.arange(-10, 110, tc):
        ax.axhline(y, color="#cbd5e0", linestyle="--", linewidth=0.8, alpha=0.8)

    for obj in objetos:
        en_colision = any(obj.id in par for par in colisiones_detectadas)
        color = '#e53e3e' if en_colision else '#2b6cb0'
        grosor = 2.5 if en_colision else 1.0
        rect = patches.Rectangle((obj.x, obj.y), obj.ancho, obj.alto,
                                 edgecolor=color, facecolor='#ebf8ff', alpha=0.6,
                                 linewidth=grosor)
        ax.add_patch(rect)
        ax.text(obj.x + obj.ancho/2, obj.y + obj.alto/2,
                f"{obj.id}", fontsize=9, ha='center', va='center',
                color='#2c5282', weight='bold')

    aciertos = len(colisiones_detectadas.intersection(colisiones_reales))
    falsos_pos = len(colisiones_detectadas) - aciertos
    info = (f"Candidatos: {len(pares_candidatos)}\n"
            f"Colisiones reales: {len(colisiones_reales)}\n"
            f"Detectadas: {len(colisiones_detectadas)}\n"
            f"Aciertos: {aciertos}  |  Falsos +: {falsos_pos}")
    ax.text(2, 2, info, fontsize=9,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    plt.tight_layout()
    plt.show()


def dibujar_malla_implicita(malla, objetos, colisiones_reales, colisiones_detectadas, pares_candidatos):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title("MallaImplicita2D (Bits)", fontsize=12, weight='bold')
    ax.invert_yaxis()
    ax.set_aspect('equal')

    tc = malla.tamanio_celda
    max_x = max(obj.x + obj.ancho for obj in objetos)
    max_y = max(obj.y + obj.alto for obj in objetos)
    limite_x = math.ceil(max_x / tc) * tc
    limite_y = math.ceil(max_y / tc) * tc

    ax.set_xlim(-5, limite_x + 5)
    ax.set_ylim(limite_y + 5, -5)

    for x in np.arange(0, limite_x + tc, tc):
        ax.axvline(x, color="#cbd5e0", linestyle="--", linewidth=0.8, alpha=0.8)
    for y in np.arange(0, limite_y + tc, tc):
        ax.axhline(y, color="#cbd5e0", linestyle="--", linewidth=0.8, alpha=0.8)

    for obj in objetos:
        en_colision = any(obj.id in par for par in colisiones_detectadas)
        color = '#e53e3e' if en_colision else '#38a169'
        grosor = 2.5 if en_colision else 1.0
        rect = patches.Rectangle((obj.x, obj.y), obj.ancho, obj.alto,
                                 edgecolor=color, facecolor='#e6fffa', alpha=0.6,
                                 linewidth=grosor)
        ax.add_patch(rect)
        ax.text(obj.x + obj.ancho/2, obj.y + obj.alto/2,
                f"{obj.id}", fontsize=9, ha='center', va='center',
                color='#2c7a7b', weight='bold')

    aciertos = len(colisiones_detectadas.intersection(colisiones_reales))
    falsos_pos = len(colisiones_detectadas) - aciertos
    info = (f"Candidatos: {len(pares_candidatos)}\n"
            f"Colisiones reales: {len(colisiones_reales)}\n"
            f"Detectadas: {len(colisiones_detectadas)}\n"
            f"Aciertos: {aciertos}  |  Falsos +: {falsos_pos}")
    ax.text(2, 2, info, fontsize=9,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    plt.tight_layout()
    plt.show()


def dibujar_quadtree_punteros(raiz, objetos, colisiones_reales, colisiones_detectadas, pares_candidatos):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title("Quadtree con punteros", fontsize=12, weight='bold')
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_xlim(0, 100)
    ax.set_ylim(100, 0)

    def dibujar_nodo(nodo):
        if nodo is None:
            return
        colores_linea = {0: "#1a202c", 1: "#2b6cb0", 2: "#2c7a7b", 3: "#9b2c2c"}
        estilos_linea = {0: "-", 1: "--", 2: "-.", 3: ":"}
        grosores_linea = {0: 2.5, 1: 1.8, 2: 1.2, 3: 0.9}
        c_lin = colores_linea.get(nodo.prof, "#cbd5e0")
        e_lin = estilos_linea.get(nodo.prof, ":")
        g_lin = grosores_linea.get(nodo.prof, 0.5)

        x_min = nodo.centro.x - nodo.mitadAncho
        y_min = nodo.centro.y - nodo.mitadAncho
        ancho_celda = nodo.mitadAncho * 2
        rect_celda = patches.Rectangle((x_min, y_min), ancho_celda, ancho_celda,
                                       edgecolor=c_lin, facecolor='none',
                                       linestyle=e_lin, lw=g_lin)
        ax.add_patch(rect_celda)

        colores_fondo = {0: "#e2e8f0", 1: "#ebf8ff", 2: "#e6fffa", 3: "#feebc8"}
        for pObj in nodo.pObjList:
            en_colision = any(pObj.id in par for par in colisiones_detectadas)
            color_borde = '#e53e3e' if en_colision else "#4a5568"
            grosor = 2.5 if en_colision else 1.2
            rect_obj = patches.Rectangle((pObj.x, pObj.y), pObj.ancho, pObj.alto,
                                         edgecolor=color_borde,
                                         facecolor=colores_fondo.get(nodo.prof, "#ffffff"),
                                         alpha=0.6, lw=grosor)
            ax.add_patch(rect_obj)
            cx = pObj.x + pObj.ancho/2
            cy = pObj.y + pObj.alto/2
            ax.text(cx, cy, f"{pObj.id}", fontsize=8, ha='center', va='center', weight='bold')

        for hijo in nodo.pHijo:
            if hijo:
                dibujar_nodo(hijo)

    dibujar_nodo(raiz)
    aciertos = len(colisiones_detectadas.intersection(colisiones_reales))
    falsos_pos = len(colisiones_detectadas) - aciertos
    info = (f"Candidatos: {len(pares_candidatos)}\n"
            f"Detectadas: {len(colisiones_detectadas)}\n"
            f"Aciertos: {aciertos}/{len(colisiones_reales)}\n"
            f"Falsos +: {falsos_pos}")
    ax.text(2, 2, info, fontsize=9,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    plt.tight_layout()
    plt.show()


def dibujar_quadtree_lineal(quadtree, objetos, colisiones_reales, colisiones_detectadas, pares_candidatos):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title("Quadtree Lineal (Hash)", fontsize=12, weight='bold')
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_xlim(0, 100)
    ax.set_ylim(100, 0)

    estilos_celda = {
        0: {"color": "#1a202c", "estilo": "-",  "grosor": 2.5},
        1: {"color": "#2b6cb0", "estilo": "--", "grosor": 1.8},
        2: {"color": "#2c7a7b", "estilo": "-.", "grosor": 1.2},
        3: {"color": "#9b2c2c", "estilo": ":",  "grosor": 1.0}
    }
    colores_objetos = {0: "#cbd5e0", 1: "#bee3f8", 2: "#b2f5ea", 3: "#feebc8"}

    for key, nodo in quadtree.Nodos_hash.items():
        d = NodoProf(key)
        cfg = estilos_celda.get(d, {"color": "#718096", "estilo": ":", "grosor": 0.5})
        x_min = nodo.centro.x - nodo.mitadAncho
        y_min = nodo.centro.y - nodo.mitadAncho
        ancho_celda = nodo.mitadAncho * 2
        rect_celda = patches.Rectangle((x_min, y_min), ancho_celda, ancho_celda,
                                       edgecolor=cfg["color"], facecolor='none',
                                       linestyle=cfg["estilo"], lw=cfg["grosor"])
        ax.add_patch(rect_celda)

        for obj in nodo.pObjList:
            en_colision = any(obj.id in par for par in colisiones_detectadas)
            color_borde = '#e53e3e' if en_colision else cfg["color"]
            grosor = 2.5 if en_colision else 1.2
            rect_obj = patches.Rectangle((obj.x, obj.y), obj.ancho, obj.alto,
                                         edgecolor=color_borde,
                                         facecolor=colores_objetos.get(d, "#ffffff"),
                                         alpha=0.6, lw=grosor)
            ax.add_patch(rect_obj)
            cx = obj.x + obj.ancho/2
            cy = obj.y + obj.alto/2
            ax.text(cx, cy, f"{obj.id}", fontsize=8, ha='center', va='center', weight='bold')

    aciertos = len(colisiones_detectadas.intersection(colisiones_reales))
    falsos_pos = len(colisiones_detectadas) - aciertos
    info = (f"Candidatos: {len(pares_candidatos)}\n"
            f"Detectadas: {len(colisiones_detectadas)}\n"
            f"Aciertos: {aciertos}/{len(colisiones_reales)}\n"
            f"Falsos +: {falsos_pos}")
    ax.text(2, 2, info, fontsize=9,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    plt.tight_layout()
    plt.show()


def comparar_estructuras(num_objetos=25):
    objetos = generar_objetos(num_objetos, semilla=5)
    colisiones_reales = calcular_colisiones_reales(objetos)

    # 0. Referencia
    dibujar_referencia(objetos, colisiones_reales)

    # 1. HSHG_2D 
    hgrid = HSHG_2D(tamanio_celda_min=10.0)
    for obj in objetos:
        ent = Entidad(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        hgrid.insertar(ent)
        obj.nivel = ent.nivel

    candidatos_hgrid = set()
    for obj in objetos:
        ent_temp = Entidad(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        ent_temp.nivel = obj.nivel
        for otro in hgrid.obtener_candidatos(ent_temp):
            if otro.id != obj.id:
                candidatos_hgrid.add(tuple(sorted((obj.id, otro.id))))

    colisiones_hgrid = set()
    for obj in objetos:
        ent_temp = Entidad(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        for otro in hgrid.obtener_colisiones(ent_temp):
            if otro.id != obj.id:
                colisiones_hgrid.add(tuple(sorted((obj.id, otro.id))))
    dibujar_hgrid(hgrid, objetos, colisiones_reales, colisiones_hgrid, candidatos_hgrid)

    # 2. MallaHash2D 
    # Calcular el lado mayor máximo entre todos los objetos
    tam_celda_hash = max(math.sqrt((obj.ancho**2)+(obj.alto**2)) for obj in objetos)
    tam_celda_hash = max(tam_celda_hash, 2.0)
    print(f"Tamaño de celda para mallas uniformes: {tam_celda_hash:.2f}")

    malla_hash = MallaHash2D(tamanio_celda=tam_celda_hash)
    for obj in objetos:
        malla_hash.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho,
                                   obj.y, obj.y+obj.alto)

    pares_candidatos_hash = set()
    for obj in objetos:
        candidatos = malla_hash.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho,
                                                            obj.y, obj.y+obj.alto)
        for otro_id in candidatos:
            if otro_id != obj.id:
                pares_candidatos_hash.add(tuple(sorted((obj.id, otro_id))))

    colisiones_hash = set()
    for (a, b) in pares_candidatos_hash:
        if objetos[a].interseccion(objetos[b]):
            colisiones_hash.add((a, b))
    dibujar_malla_hash(malla_hash, objetos, colisiones_reales, colisiones_hash, pares_candidatos_hash)

    # 3. MallaImplicita2D
    celda_impl = tam_celda_hash
    grid_width, grid_height = dimensiones_malla_implicita(objetos, celda_impl)
    malla_impl = MallaImplicita2D(grid_width, grid_height, celda_impl, num_objetos)
    for obj in objetos:
        malla_impl.insertar_objeto(obj.id, obj.x, obj.x+obj.ancho,
                                   obj.y, obj.y+obj.alto)

    pares_candidatos_impl = set()
    for obj in objetos:
        candidatos = malla_impl.obtener_posibles_colisiones(obj.x, obj.x+obj.ancho,
                                                            obj.y, obj.y+obj.alto,
                                                            id_excluir=obj.id)
        for otro_id in candidatos:
            if otro_id != obj.id:
                pares_candidatos_impl.add(tuple(sorted((obj.id, otro_id))))

    colisiones_impl = set()
    for (a, b) in pares_candidatos_impl:
        if objetos[a].interseccion(objetos[b]):
            colisiones_impl.add((a, b))
    dibujar_malla_implicita(malla_impl, objetos, colisiones_reales, colisiones_impl, pares_candidatos_impl)

    # 4. Quadtree con punteros
    centro = Punto(50.0, 50.0)
    mitad = 50.0
    prof_max = 4
    raiz = BuildQuadtree(centro, mitad, prof_max)
    for obj in objetos:
        obj_p = ObjPunteros(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        InsertObjeto(raiz, obj_p)

    colisiones_punteros = obtener_colisiones(raiz)
    candidatos_punteros = obtener_candidatos(raiz)
    dibujar_quadtree_punteros(raiz, objetos, colisiones_reales, colisiones_punteros, candidatos_punteros)

    # 5. Quadtree Lineal (usando métodos de la clase)
    quadtree_lineal = LinearQuadtree(PuntoLineal(50.0, 50.0), 50.0, prof_max)
    for obj in objetos:
        obj_lineal = ObjLineal(obj.id, obj.x, obj.y, obj.ancho, obj.alto)
        quadtree_lineal.InsertObjetoLinear(obj_lineal)

    colisiones_lineal = quadtree_lineal.obtener_colisiones()
    candidatos_lineal = quadtree_lineal.obtener_candidatos()
    dibujar_quadtree_lineal(quadtree_lineal, objetos, colisiones_reales, colisiones_lineal, candidatos_lineal)

    print("\n" + "="*70)
    print("RESUMEN DE LA COMPARATIVA")
    print("="*70)
    print(f"Total de objetos: {num_objetos}")
    print(f"Colisiones reales (fuerza bruta): {len(colisiones_reales)}")
    print("-"*70)
    print(f"HSHG_2D                : candidatos {len(candidatos_hgrid)}, detectadas {len(colisiones_hgrid)}")
    print(f"MallaHash2D            : candidatos {len(pares_candidatos_hash)}, detectadas {len(colisiones_hash)}")
    print(f"MallaImplicita2D       : candidatos {len(pares_candidatos_impl)}, detectadas {len(colisiones_impl)}")
    print(f"Quadtree con punteros  : candidatos {len(candidatos_punteros)}, detectadas {len(colisiones_punteros)}")
    print(f"Quadtree Lineal        : candidatos {len(candidatos_lineal)}, detectadas {len(colisiones_lineal)}")
    print("="*70)


if __name__ == "__main__":
    comparar_estructuras(25)
