# -*- coding: utf-8 -*-
"""
Created on Fri May 22 22:11:58 2026

@author: María
"""

import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# La celda debe medir al menos 4 veces la dimensión máxima del objeto
OBJECT_TO_CELL_RATIO = 1.0 / 4.0  
CELL_TO_CELL_RATIO   = 2.0         # cada nivel dobla el tamaño de celda
EPSILON              = 1e-6
HGRID_MAX_NIVELES    = 32

class Entidad:
    def __init__(self, id_entidad, x, y, ancho, alto):
        self.id    = id_entidad
        self.x     = x        # Esquina superior izquierda X
        self.y     = y        # Esquina superior izquierda Y
        self.ancho = ancho    # Ancho del AABB (extensión en X)
        self.alto  = alto     # Alto del AABB (extensión en Y)
        self.nivel = None     # nivel asignado en la inserción
        self.clave_celda = None # tupla (cx, cy, level) asignada

class HSHG_2D:
    def __init__(self, tamanio_celda_min: float = 32.0):
        self.tamanio_celda_min = tamanio_celda_min
        self.celdas = {} 
        self.objects_at_level = [0] * HGRID_MAX_NIVELES  
        self.niveles_ocupados_mask = 0  
        
    def _obtener_tamanio_celda(self, nivel: int) -> float:
        return self.tamanio_celda_min * (CELL_TO_CELL_RATIO ** nivel)

    def insertar(self, entidad):
        """ Determina el nivel según la dimensión máxima del AABB e inserta usando la esquina superior izquierda """
        level = 0
        size = self.tamanio_celda_min
        max_dimension = max(entidad.ancho, entidad.alto)
        
        while size * OBJECT_TO_CELL_RATIO < max_dimension and level < HGRID_MAX_NIVELES - 1:
            size *= CELL_TO_CELL_RATIO
            level += 1
        
        cx = int(math.floor(entidad.x / size))
        cy = int(math.floor(entidad.y / size))
        
        clave = (cx, cy, level)
        entidad.clave_celda = clave
        entidad.nivel = level
        
        self.celdas.setdefault(clave, []).append(entidad)
        
        self.objects_at_level[level] += 1
        self.niveles_ocupados_mask |= (1 << level)

    def eliminar(self, entidad):
        """ Retira el objeto y actualiza los mapas de ocupación binaria """
        level = entidad.nivel
        clave = entidad.clave_celda
        
        if clave is not None and level is not None:
            self.objects_at_level[level] -= 1
            if self.objects_at_level[level] == 0:
                self.niveles_ocupados_mask &= ~(1 << level)
                
            if entidad in self.celdas.get(clave, []):
                self.celdas[clave].remove(entidad)
                if not self.celdas[clave]:
                    del self.celdas[clave]
                
            entidad.clave_celda = None
            entidad.nivel = None

    def obtener_colisiones(self, entidad):
        """ Retorna una lista con todas las entidades cuyo AABB solapa con la actual """
        objetos_colisionados = []
        size = self.tamanio_celda_min
        niveles_ocupados_mask = self.niveles_ocupados_mask
        
        level = 0
        while level < HGRID_MAX_NIVELES and niveles_ocupados_mask != 0:
            if (niveles_ocupados_mask & 1) != 0:
                max_dimension_objeto = max(entidad.ancho, entidad.alto)
                delta_atras = size * OBJECT_TO_CELL_RATIO + EPSILON
                delta_adelante = max_dimension_objeto + size * OBJECT_TO_CELL_RATIO + EPSILON
                oo_size = 1.0 / size
                
                x1 = int(math.floor((entidad.x - delta_atras) * oo_size))
                y1 = int(math.floor((entidad.y - delta_atras) * oo_size))
                x2 = int(math.ceil((entidad.x + delta_adelante) * oo_size))
                y2 = int(math.ceil((entidad.y + delta_adelante) * oo_size))
                
                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        # Acceso directo al diccionario O(1)
                        for p in self.celdas.get((x, y, level), []):
                            if p != entidad:
                                no_solapan = (
                                    entidad.x + entidad.ancho < p.x or  
                                    p.x + p.ancho < entidad.x or        
                                    entidad.y + entidad.alto < p.y or   
                                    p.y + p.alto < entidad.y            
                                )
                                
                                if not no_solapan:
                                    objetos_colisionados.append(p)
                
            size *= CELL_TO_CELL_RATIO
            niveles_ocupados_mask >>= 1
            level += 1
            
        return objetos_colisionados
    
    def obtener_candidatos(self, entidad):
        objetos_candidatos = set()
        level = entidad.nivel
        size = self._obtener_tamanio_celda(level)
        niveles_ocupados_mask = self.niveles_ocupados_mask >> level
        
        while level < HGRID_MAX_NIVELES and niveles_ocupados_mask != 0:
            if (niveles_ocupados_mask & 1) != 0:
                max_dimension_objeto = max(entidad.ancho, entidad.alto)
                delta_atras = size * OBJECT_TO_CELL_RATIO + EPSILON
                delta_adelante = max_dimension_objeto + size * OBJECT_TO_CELL_RATIO + EPSILON
                oo_size = 1.0 / size
                
                x1 = int(math.floor((entidad.x - delta_atras) * oo_size))
                y1 = int(math.floor((entidad.y - delta_atras) * oo_size))
                x2 = int(math.ceil((entidad.x + delta_adelante) * oo_size))
                y2 = int(math.ceil((entidad.y + delta_adelante) * oo_size))
                
                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        for p in self.celdas.get((x, y, level), []):
                            if p != entidad:
                                objetos_candidatos.add(p)
                
            size *= CELL_TO_CELL_RATIO
            niveles_ocupados_mask >>= 1
            level += 1
            
        return objetos_candidatos

if __name__ == "__main__":
    random.seed(105)

    TAMANIO_MIN_CELDA = 10.0
    malla = HSHG_2D(tamanio_celda_min=TAMANIO_MIN_CELDA)

    lista_entidades = []
    dimensiones_prueba = [
        (2.0, 5.0), (6.0, 2.0), (4.0, 4.0), (12.0, 3.0),
        (3.0, 15.0), (8.0, 9.0), (16.0, 16.0), (19.0, 5.0)
    ]

    for i, (ancho, alto) in enumerate(dimensiones_prueba):
        x = random.uniform(15, 75)
        y = random.uniform(15, 75)
        ent = Entidad(id_entidad=i, x=x, y=y, ancho=ancho, alto=alto)
        lista_entidades.append(ent)
        malla.insertar(ent)

    print("=" * 75)
    print("  NIVEL ASIGNADO A CADA ENTIDAD")
    print("=" * 75)
    for ent in lista_entidades:
        tc = malla._obtener_tamanio_celda(ent.nivel)
        cx = int(ent.x / tc)
        cy = int(ent.y / tc)
        print(f"  ID:{ent.id}  dim=({ent.ancho:4.1f}×{ent.alto:4.1f})  "
              f"→ Nivel {ent.nivel}  (celda {tc:.0f}×{tc:.0f})  en ({cx}, {cy})")

    print("\n" + "=" * 75)
    print("  PARES CON COLISIÓN DETECTADA")
    print("=" * 75)
    pares = set()
    for ent in lista_entidades:
        for otro in malla.obtener_colisiones(ent):
            pares.add(tuple(sorted((ent.id, otro.id))))
    if pares:
        for a, b in sorted(pares):
            print(f"  ID:{a} ↔ ID:{b}")
    else:
        print("  (ninguna con estos datos de prueba)")
    print("=" * 75)

    NUM_NIVELES = 4
    colores = {0: "#3182ce", 1: "#e53e3e", 2: "#319795", 3: "#d69e2e"}
    fig, axs = plt.subplots(2, 2, figsize=(14, 14))
    axs = axs.ravel()
    limites = (-5, 105)

    for niv in range(NUM_NIVELES):
        ax  = axs[niv]
        tc  = malla._obtener_tamanio_celda(niv)
        col = colores[niv]
        ax.set_title(f"Nivel {niv}  —  celda {tc:.0f}×{tc:.0f} u.", fontsize=11, fontweight="bold")
        ax.invert_yaxis()

        cx_min = int(math.floor(limites[0] / tc))
        cx_max = int(math.ceil(limites[1] / tc))

        for c in range(cx_min, cx_max + 1):
            coordenada = c * tc
            ax.axvline(coordenada, color="#cbd5e0", linestyle=":", linewidth=0.9)
            ax.axhline(coordenada, color="#cbd5e0", linestyle=":", linewidth=0.9)

        for ent in lista_entidades:
            if ent.nivel == niv:
                ax.add_patch(patches.Rectangle((ent.x, ent.y), ent.ancho, ent.alto,
                                               edgecolor=col, facecolor=col, alpha=0.35, linewidth=2))

                cx = int(ent.x / tc)
                cy = int(ent.y / tc)
                ax.add_patch(patches.Rectangle(
                    (cx * tc, cy * tc), tc, tc,
                    edgecolor=col, facecolor=col, alpha=0.10, linestyle="--", linewidth=1.5))

                cx_txt = ent.x + ent.ancho / 2.0
                cy_txt = ent.y + ent.alto / 2.0
                ax.text(cx_txt, cy_txt, f"ID:{ent.id}\n{ent.ancho}×{ent.alto}",
                        fontsize=8, ha="center", va="center", fontweight="bold", color="#2d3748")

        ax.set_xlim(limites)
        ax.set_ylim(limites[1], limites[0])
        ax.set_aspect("equal")

    plt.suptitle("HSHG 2D — AABB con Diccionarios de Python", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.show()
