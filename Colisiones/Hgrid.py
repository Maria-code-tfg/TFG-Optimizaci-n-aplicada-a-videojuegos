# -*- coding: utf-8 -*-
"""
Created on Fri May 22 22:11:58 2026

@author: María
"""

import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches


SPHERE_TO_CELL_RATIO = 1.0 / 4.0  # la celda debe medir al menos 4× el diámetro del objeto
CELL_TO_CELL_RATIO   = 2.0         # cada nivel dobla el tamaño de celda
EPSILON              = 1e-6
HGRID_MAX_nivelS     = 32


class Entidad:
    def __init__(self, id_entidad, x, y, r):
        self.id    = id_entidad
        self.x     = x
        self.y     = y
        self.r     = r
        self.nivel = None   # nivel asignado en la inserción
        self.celda = None   # (cx, cy) de la celda única donde se registra


class HSHG_2D:
    def __init__(self, tamanio_celda_min: float):
        self.tamanio_celda_min      = tamanio_celda_min
        self.niveles             = {}   # nivel -> {(cx, cy) -> [entidades]}
        self.objetos_en_nivel    = {}   # nivel -> contador de objetos
        self.niveles_ocupados_mask = 0  # bitmask: bit k activo si el nivel k tiene objetos
        self.tick                = 0   # contador de time-stamping para consultas

    def _calcular_nivel(self, r: float) -> int:
        """Sube de nivel mientras size * SPHERE_TO_CELL_RATIO < diameter."""
        diametro = 2.0 * r
        tamanio     = self.tamanio_celda_min
        nivel    = 0
        while tamanio * SPHERE_TO_CELL_RATIO < diametro and nivel < HGRID_MAX_nivelS-1:
            tamanio  *= CELL_TO_CELL_RATIO
            nivel += 1
        return nivel

    def _obtener_tamanio_celda(self, nivel: int) -> float:
        return self.tamanio_celda_min * (CELL_TO_CELL_RATIO ** nivel)

    def insertar(self, entidad: Entidad):
        """inserta el objeto en la celda que contiene su centro, al nivel correcto."""
        nivel         = self._calcular_nivel(entidad.r)
        tamanio_celda = self._obtener_tamanio_celda(nivel)

        # Celda que contiene el centro del objeto
        cx = int(math.floor(entidad.x / tamanio_celda))
        cy = int(math.floor(entidad.y / tamanio_celda))

        entidad.nivel = nivel
        entidad.celda = (cx, cy)

        if nivel not in self.niveles:
            self.niveles[nivel] = {}
        key = (cx, cy)
        if key not in self.niveles[nivel]:
            self.niveles[nivel][key] = []
        self.niveles[nivel][key].append(entidad)

        self.objetos_en_nivel[nivel] = self.objetos_en_nivel.get(nivel, 0) + 1
        self.niveles_ocupados_mask   |= (1 << nivel)

    def eliminar(self, entidad: Entidad):
        """
        Elimina el objeto y actualiza la máscara de niveles ocupados.
        """
        nivel  = entidad.nivel
        key    = entidad.celda
        bucket = self.niveles[nivel][key]
        bucket.eliminar(entidad)
        if not bucket:
            del self.niveles[nivel][key]

        self.objetos_en_nivel[nivel] -= 1
        if self.objetos_en_nivel[nivel] == 0:
            self.niveles_ocupados_mask &= ~(1 << nivel)

        entidad.nivel = None
        entidad.celda = None

    def obtener_colisiones(self, entidad: Entidad) -> list:
        """Devuelve los objetos cuyas esferas se solapan con la de entidad, recorriendo todos los niveles."""
        self.tick += 1
        colisiones      = []
        visitados_buckets = set()

        tamanio          = self.tamanio_celda_min
        ocupadas_mask = self.niveles_ocupados_mask

        for nivel in range(HGRID_MAX_nivelS):
            if ocupadas_mask == 0:
                break
            if ocupadas_mask & 1:
                delta   = entidad.r + tamanio * SPHERE_TO_CELL_RATIO + EPSILON
                oo_tamanio = 1.0 / tamanio

                x1 = int(math.floor((entidad.x - delta) * oo_tamanio))
                y1 = int(math.floor((entidad.y - delta) * oo_tamanio))
                x2 = int(math.ceil( (entidad.x + delta) * oo_tamanio))
                y2 = int(math.ceil( (entidad.y + delta) * oo_tamanio))

                nivel_buckets = self.niveles.get(nivel, {})

                for cx in range(x1, x2 + 1):
                    for cy in range(y1, y2 + 1):
                        bucket_key = (cx, cy, nivel)
                        if bucket_key in visitados_buckets:
                            continue
                        visitados_buckets.add(bucket_key)

                        for otro in nivel_buckets.get((cx, cy), []):
                            if otro is entidad:
                                continue
                            dist2 = (entidad.x - otro.x)**2 + (entidad.y - otro.y)**2
                            if dist2 <= (entidad.r + otro.r + EPSILON)**2:
                                colisiones.append(otro)

            tamanio          *= CELL_TO_CELL_RATIO
            ocupadas_mask >>= 1

        return colisiones


if __name__ == "__main__":
    random.seed(101)

    # min_tamanio = 10 → niveles: 0(r≤1.25), 1(r≤2.5), 2(r≤5.0), 3(r≤10.0)
    TAMANIO_MIN_CELDA = 10.0
    malla = HSHG_2D(tamanio_celda_min=TAMANIO_MIN_CELDA)

    # Radios elegidos para poblar los niveles 0-3
    radios_prueba = [1.0, 1.2, 2.0, 2.4, 4.0, 4.8, 8.0, 9.5]

    lista_entidades = []
    for i, r in enumerate(radios_prueba):
        x = random.uniform(15, 85)
        y = random.uniform(15, 85)
        ent = Entidad(id_entidad=i, x=x, y=y, r=r)
        lista_entidades.append(ent)
        malla.insertar(ent)

    print("=" * 55)
    print("  NIVEL ASIGNADO A CADA ENTIDAD")
    print("=" * 55)
    for ent in lista_entidades:
        tc = malla._obtener_tamanio_celda(ent.nivel)
        print(f"  ID:{ent.id}  r={ent.r:4.1f}  diám={2*ent.r:4.1f}"
              f"  → Nivel {ent.nivel}  (celda {tc:.0f}×{tc:.0f})  en {ent.celda}")

    print()
    print("=" * 55)
    print("  PARES CON COLISIÓN DETECTADA")
    print("=" * 55)
    pares = set()
    for ent in lista_entidades:
        for otro in malla.obtener_colisiones(ent):
            pares.add(tuple(sorted((ent.id, otro.id))))
    if pares:
        for a, b in sorted(pares):
            print(f"  ID:{a} ↔ ID:{b}")
    else:
        print("  (ninguna con estos datos de prueba)")
    print("=" * 55)

    # Gráfico
    NUM_NIVELES = 4
    colores = {0: "#3182ce", 1: "#e53e3e", 2: "#319795", 3: "#d69e2e"}
    fig, axs = plt.subplots(2, 2, figsize=(14, 14))
    axs = axs.ravel()
    limites = (-5, 105)

    for niv in range(NUM_NIVELES):
        ax  = axs[niv]
        tc  = malla._obtener_tamanio_celda(niv)
        col = colores[niv]
        ax.set_title(f"Nivel {niv}  —  celda {tc:.0f}×{tc:.0f} u.",
                     fontsize=11, fontweight="bold")

        # Cuadrícula de este nivel
        cx_min = int(math.floor(limites[0] / tc))
        cx_max = int(math.ceil(limites[1] / tc))

        for c in range(cx_min, cx_max + 1):
            coordenada = c * tc
            ax.axvline(coordenada, color="#cbd5e0", linestyle=":", linewidth=0.9)
            ax.axhline(coordenada, color="#cbd5e0", linestyle=":", linewidth=0.9)

        for ent in lista_entidades:
            if ent.nivel != niv:
                continue

            # Círculo del objeto
            ax.add_patch(plt.Circle((ent.x, ent.y), ent.r,
                                    edgecolor=col, facecolor=col,
                                    alpha=0.25, linewidth=2))

            # Celda única donde está registrado (inserción monocelda)
            cx, cy = ent.celda
            ax.add_patch(patches.Rectangle(
                (cx * tc, cy * tc), tc, tc,
                edgecolor=col, facecolor=col, alpha=0.15,
                linestyle="--", linewidth=1.5))

            ax.text(ent.x, ent.y,
                    f"ID:{ent.id}\nr={ent.r}",
                    fontsize=8, ha="center", va="center",
                    fontweight="bold", color="#2d3748")

        ax.set_xlim(limites)
        ax.set_ylim(limites)
        ax.set_aspect("equal")

    plt.suptitle("HSHG 2D — Inserción monocelda por nivel jerárquico",
                 fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.show()
