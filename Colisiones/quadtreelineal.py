# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 20:43:24 2026

@author: María
"""

from Punto import Punto
import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches



class Objeto:
    def __init__(self, id_obj, x: float, y: float, ancho: float, alto: float):
        self.id = id_obj
        self.x = x              
        self.y = y              
        self.ancho = ancho      
        self.alto = alto  
        
    def test_intersección(self, b):
        if (self.x-b.x>b.ancho or -(self.x-b.x)>self.ancho): return False
        if (self.y-b.y>b.alto or -(self.y-b.y)>self.alto): return False
        return True



class Nodo:
    def __init__(self, clave: tuple, centro: Punto, mitadAncho: float):
        self.clave = clave             # Clave del nodo: (profundidad, indice_x, indice_y)
        self.centro = centro           # Centro geométrico del nodo
        self.mitadAncho = mitadAncho   # Mitad del ancho de la celda
        self.hasChildK = 0             # Máscara de bits indicando qué hijos existen (0-3)
        self.pObjList = []             # Lista de objetos contenidos en este nodo



def NodoProf(clave: tuple) -> int:
    """ Devuelve la profundidad almacenada en la clave (profundidad, indice_x, indice_y) """
    return clave[0]

def ClaveHijo(clave_padre: tuple, index: int) -> tuple:
    """ Calcula la clave del hijo usando coordenadas discretas dentro del nivel """
    profundidad, indice_x, indice_y = clave_padre
    bit_x = index & 1
    bit_y = (index & 2) >> 1
    return profundidad + 1, indice_x * 2 + bit_x, indice_y * 2 + bit_y



class LinearQuadtree:
    def __init__(self, mundo_centro: Punto, mundo_mitadAncho: float, max_Prof: int):
        self.mundo_centro = mundo_centro
        self.mundo_mitadAncho = mundo_mitadAncho
        self.max_Prof = max_Prof
        
        # Tabla Hash de nodos
        self.Nodos_hash = {}
        self.colisiones_detectadas = set()
        
        # Inicializamos el nodo raíz con la clave (profundidad, indice_x, indice_y)
        self.Nodos_hash[(0, 0, 0)] = Nodo((0, 0, 0), mundo_centro, mundo_mitadAncho)

    def InsertObjetoLinear(self, obj: Objeto):
        """ Inserta un objeto de forma desde arriba hacia abajo en la tabla Hash del árbol """
        actual_clave = (0, 0, 0)
        curr_Nodo = self.Nodos_hash[actual_clave]
        Prof = 0
        
        straddle = False
        while Prof < self.max_Prof and not straddle:
            index = 0
            straddle = False
            
            # Comprobación Eje X
            if obj.x < curr_Nodo.centro.x and (obj.x + obj.ancho) > curr_Nodo.centro.x:
                straddle = True
            else:
                if obj.x >= curr_Nodo.centro.x:
                    index |= (1 << 0)
                    
            # Comprobación Eje Y
            if not straddle:
                if obj.y < curr_Nodo.centro.y and (obj.y + obj.alto) > curr_Nodo.centro.y:
                    straddle = True
                else:
                    if obj.y >= curr_Nodo.centro.y:
                        index |= (1 << 1)
                        
            if not straddle:
                # Calculamos la clave del hijo
                child_clave = ClaveHijo(curr_Nodo.clave, index)
                curr_Nodo.hasChildK |= (1 << index)
                
                # Si el hijo no existe en el Hash, se genera
                if child_clave not in self.Nodos_hash:
                    child_mitadAncho = curr_Nodo.mitadAncho * 0.5
                    offset_x = child_mitadAncho if (index & 1) else -child_mitadAncho
                    offset_y = child_mitadAncho if (index & 2) else -child_mitadAncho
                    child_centro = Punto(curr_Nodo.centro.x + offset_x, curr_Nodo.centro.y + offset_y)
                    
                    self.Nodos_hash[child_clave] = Nodo(child_clave, child_centro, child_mitadAncho)
                    
                curr_Nodo = self.Nodos_hash[child_clave]
                Prof += 1
            
        curr_Nodo.pObjList.append(obj)

    def TestCollision(self, pA: Objeto, pB: Objeto):
        """ Comprobación AABB estándar """
        no_solapan = (
            pA.x + pA.ancho < pB.x or  
            pB.x + pB.ancho < pA.x or  
            pA.y + pA.alto < pB.y or   
            pB.y + pB.alto < pA.y      
        )
        return not no_solapan

    def TestAllCollisionsLinear(self, curr_Nodo: Nodo, ancestor_stack: list, colisiones_detectadas: set, Prof: int = 0):
        """ Recorrido jerárquico lineal guiado por máscara de bits """
        ancestor_stack[Prof] = curr_Nodo
        Prof += 1
        
        for n in range(Prof):
            ancestor_Nodo = ancestor_stack[n]
            if ancestor_Nodo is curr_Nodo:
                pares_a_comparar = (
                    (pA, pB)
                    for indice, pA in enumerate(curr_Nodo.pObjList)
                    for pB in curr_Nodo.pObjList[:indice]
                )
            else:
                pares_a_comparar = (
                    (pA, pB)
                    for pA in ancestor_Nodo.pObjList
                    for pB in curr_Nodo.pObjList
                )

            for pA, pB in pares_a_comparar:
                if self.TestCollision(pA, pB):
                    colisiones_detectadas.add(tuple(sorted((pA.id, pB.id))))
                    
        for i in range(4):
            if curr_Nodo.hasChildK & (1 << i):
                child_clave = ClaveHijo(curr_Nodo.clave, i)
                child_Nodo = self.Nodos_hash.get(child_clave)
                if child_Nodo:
                    self.TestAllCollisionsLinear(child_Nodo, ancestor_stack, colisiones_detectadas, Prof)


    def obtener_colisiones(self):
        """Método público que inicia la detección de colisiones y devuelve el conjunto de pares"""
        colisiones = set()
        stack_ancestros = [None] * 50
        nodo_raiz = self.Nodos_hash[(0, 0, 0)]
        self.TestAllCollisionsLinear(nodo_raiz, stack_ancestros, colisiones)
        return colisiones
    
    def TestAllCandidatosLinear(self, curr_Nodo: Nodo, ancestor_stack: list, colisiones_detectadas: set, Prof: int = 0):
        """ Recorrido jerárquico lineal guiado por máscara de bits """
        ancestor_stack[Prof] = curr_Nodo
        Prof += 1
        
        for n in range(Prof):
            ancestor_Nodo = ancestor_stack[n]
            if ancestor_Nodo is curr_Nodo:
                pares_a_guardar = (
                    (pA, pB)
                    for indice, pA in enumerate(curr_Nodo.pObjList)
                    for pB in curr_Nodo.pObjList[:indice]
                )
            else:
                pares_a_guardar = (
                    (pA, pB)
                    for pA in ancestor_Nodo.pObjList
                    for pB in curr_Nodo.pObjList
                )

            for pA, pB in pares_a_guardar:
                colisiones_detectadas.add(tuple(sorted((pA.id, pB.id))))
                    
        for i in range(4):
            if curr_Nodo.hasChildK & (1 << i):
                child_clave = ClaveHijo(curr_Nodo.clave, i)
                child_Nodo = self.Nodos_hash.get(child_clave)
                if child_Nodo:
                    self.TestAllCandidatosLinear(child_Nodo, ancestor_stack, colisiones_detectadas, Prof)


    def obtener_candidatos(self):
        """Método público que inicia la detección de colisiones y devuelve el conjunto de pares"""
        colisiones = set()
        stack_ancestros = [None] * 50
        nodo_raiz = self.Nodos_hash[(0, 0, 0)]
        self.TestAllCandidatosLinear(nodo_raiz, stack_ancestros, colisiones)
        return colisiones


# --- BLOQUE PRINCIPAL (MAIN) ---
if __name__ == "__main__":
    random.seed(42)  # Semilla fija para consistencia

    centro_mundo = Punto(50.0, 50.0)
    mitad_ancho_mundo = 50.0
    profundidad_maxima = 3

    # Instanciamos la clase que encapsula la tabla hash y las operaciones
    quadtree = LinearQuadtree(centro_mundo, mitad_ancho_mundo, profundidad_maxima)

    # Generamos la lista de objetos de prueba
    num_objetos = 15
    lista_objetos = []
    for i in range(num_objetos):
        pos_x = random.uniform(5.0, 85.0)
        pos_y = random.uniform(5.0, 85.0)
        if i % 3 == 0:
            ancho, alto = random.uniform(15.0, 22.0), random.uniform(15.0, 22.0)
        else:
            ancho, alto = random.uniform(4.0, 8.0), random.uniform(4.0, 8.0)

        obj = Objeto(id_obj=i, x=pos_x, y=pos_y, ancho=ancho, alto=alto)
        lista_objetos.append(obj)
        quadtree.InsertObjetoLinear(obj)

    quadtree.colisiones_detectadas = quadtree.obtener_colisiones()

    # Resumen en la terminal
    print("=" * 70)
    print(f" NÚMERO DE NODOS ACTIVOS EN LA TABLA HASH: {len(quadtree.Nodos_hash)}")
    print("=" * 70)
    for k, v in sorted(quadtree.Nodos_hash.items()):
        items_ids = [o.id for o in v.pObjList]
        print(f"-> Hash Key: {str(k):<12} | Profundidad: {NodoProf(k)} | Máscara Hijos: {bin(v.hasChildK)} | Objetos: {items_ids}")
    print("=" * 70)

    # --- RENDERIZADO GRÁFICO ---
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("Quadtree Lineal Basado en Hash (Estructura No-Punteros de Ericson)", fontsize=12, fontweight='bold')

    ax.set_xlim(0, 100)
    ax.set_ylim(100, 0)
    ax.set_aspect('equal')
    ax.plot([0, 100], [0, 100], alpha=0)  # Trazado invisible de control

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
            en_colision = any(obj.id in par for par in quadtree.colisiones_detectadas)
            color_borde = '#e53e3e' if en_colision else cfg["color"]
            grosor_borde = 2.5 if en_colision else 1.2

            rect_obj = patches.Rectangle((obj.x, obj.y), obj.ancho, obj.alto,
                                         edgecolor=color_borde, facecolor=colores_objetos.get(d, "#ffffff"),
                                         alpha=0.6, lw=grosor_borde)
            ax.add_patch(rect_obj)

            cx = obj.x + obj.ancho / 2
            cy = obj.y + obj.alto / 2
            ax.text(cx, cy, f"ID:{obj.id}\nKey:{key}", fontsize=8, ha='center', va='center', weight='bold')

    leyenda = (
        "Estructura del Quadtree Lineal (Clase Encapsulada):\n"
        "[-]  Profundidad 0 -> Celda Negra\n"
        "[--] Profundidad 1 -> Celda Azul\n"
        "[-.] Profundidad 2 -> Celda Verde\n"
        "[:]  Profundidad 3 -> Celda Roja\n\n"
        "Clave = (profundidad, indice_x, indice_y)\n"
        "Borde Rojo Grueso = Objeto en Colisión"
    )
    ax.text(2, 98, leyenda, fontsize=9.5, fontfamily='sans-serif',
            bbox=dict(facecolor='white', alpha=0.9, edgecolor='#cbd5e0', boxstyle='round,pad=0.5'))

    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y (Invertido)")
    plt.show()
