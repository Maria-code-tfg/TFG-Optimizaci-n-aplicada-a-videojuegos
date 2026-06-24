# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:05:23 2026

@author: María
"""

from Punto import Punto
import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Objeto:
    def __init__(self, id_obj, x: float, y: float, ancho: float, alto: float):
        """
        Estructura de objeto adaptada a un AABB (Axis-Aligned Bounding Box).
        Definido por su esquina superior izquierda (x, y), su ancho y su alto.
        """
        self.id = id_obj
        self.x = x              # Esquina superior izquierda X
        self.y = y              # Esquina superior izquierda Y
        self.ancho = ancho      # Extensión en el eje X
        self.alto = alto        # Extensión en el eje Y (Largo)
        
    def test_intersección(self, b):
        if (self.x-b.x>b.ancho or -(self.x-b.x)>self.ancho): return False
        if (self.y-b.y>b.alto or -(self.y-b.y)>self.alto): return False
        return True


class Nodo:
    def __init__(self):
        """
        Estructura de un nodo tradicional de Quadtree (2D).
        Mantiene su centro geométrico y su mitad de ancho para subdividir el espacio de forma limpia.
        """
        self.centro = None            # Centro del nodo (Instancia de Punto)
        self.mitadAncho = 0.0          # Mitad del ancho del volumen del nodo
        self.pHijo = [None] * 4      # Referencias a los 4 cuadrantes hijos
        self.pObjList = []          # Lista de objetos
        self.prof = 0


def BuildQuadtree(centro: Punto, mitadAncho: float, stopprof: int, actualprof: int = 0) -> Nodo:
    """ Construye un quadtree de forma recursiva """
    if stopprof < 0:
        return None

    pNodo = Nodo()
    pNodo.centro = centro
    pNodo.prof = actualprof
    pNodo.mitadAncho = mitadAncho
    pNodo.pObjList = []

    step = mitadAncho * 0.5
    for i in range(4):
        offset_x = step if (i & 1) else -step
        offset_y = step if (i & 2) else -step
        
        Hijo_centro = centro + Punto(offset_x, offset_y)
        pNodo.pHijo[i] = BuildQuadtree(Hijo_centro, step, stopprof - 1, actualprof + 1)

    return pNodo


def InsertObjeto(parbol: Nodo, pObjeto: Objeto):
    """
    Inserta un AABB de forma descendente en el árbol.
    Si el rectángulo cruza las líneas divisorias internas del nodo, se queda retenido aquí.
    """
    index = 0
    straddle = False
    # Se comprueba si el objeto queda dividido por la línea divisoria del eje x.
    if pObjeto.x < parbol.centro.x and (pObjeto.x + pObjeto.ancho) > parbol.centro.x:
        straddle = True
    else:
        # Si no la cruza, determinamos en qué lado está completamente contenido
        if pObjeto.x >= parbol.centro.x:
            index |= (1 << 0) # Está en el lado derecho

    if not straddle:
        # Se comprueba si el objeto queda dividido por la línea divisoria del eje y.
        if pObjeto.y < parbol.centro.y and (pObjeto.y + pObjeto.alto) > parbol.centro.y:
            straddle = True
        else:
            if pObjeto.y >= parbol.centro.y:
                index |= (1 << 1) # Está en el lado inferior

    # Si cabe completamente en un cuadrante hijo que existe, descendemos
    if not straddle and parbol.pHijo[index]:
        InsertObjeto(parbol.pHijo[index], pObjeto)
    else:
        # Si cruza o alcanzamos una hoja, se añade a la lista enlazada de este nodo
        parbol.pObjList.append(pObjeto)


def TestAllCollisions(pTree: Nodo, depth: int, ancestorStack: list, colisiones_detectadas: set):
    # 1. Apilar el nodo actual
    ancestorStack[depth] = pTree
    depth += 1

    # 2. Para cada nivel en la pila (desde el más reciente hasta la raíz)
    for n in range(depth):
        ancestor_node = ancestorStack[n]
        if ancestor_node is pTree:
            pares_a_comparar = (
                (pA, pB)
                for indice, pA in enumerate(pTree.pObjList)
                for pB in pTree.pObjList[:indice]
            )
        else:
            pares_a_comparar = (
                (pA, pB)
                for pA in ancestor_node.pObjList
                for pB in pTree.pObjList
            )

        for pA, pB in pares_a_comparar:
            if pA.test_intersección(pB):
                id1, id2 = pA.id, pB.id
                if id1 > id2:
                    id1, id2 = id2, id1
                colisiones_detectadas.add((id1, id2))

    # 3. Recursión sobre los hijos
    for i in range(4):
        if pTree.pHijo[i]:
            TestAllCollisions(pTree.pHijo[i], depth, ancestorStack, colisiones_detectadas)

    # 4. Bajamos la profundidad lógica de la pila
    depth -= 1


def obtener_colisiones(pArbol: Nodo) -> set:
    colisiones = set()
    MAX_DEPTH = 40
    ancestorStack = [None] * MAX_DEPTH
    depth = 0
    TestAllCollisions(pArbol, depth, ancestorStack, colisiones)
    return colisiones


def TestAllCandidatos(pTree: Nodo, depth: int, ancestorStack: list, colisiones_detectadas: set):
    """
    Versión que almacena todos los pares (sin filtrar por intersección)
    """
    ancestorStack[depth] = pTree
    depth += 1

    for n in range(depth):
        ancestor_node = ancestorStack[n]
        if ancestor_node is pTree:
            pares_a_guardar = (
                (pA, pB)
                for indice, pA in enumerate(pTree.pObjList)
                for pB in pTree.pObjList[:indice]
            )
        else:
            pares_a_guardar = (
                (pA, pB)
                for pA in ancestor_node.pObjList
                for pB in pTree.pObjList
            )

        for pA, pB in pares_a_guardar:
            id1, id2 = pA.id, pB.id
            if id1 > id2:
                id1, id2 = id2, id1
            colisiones_detectadas.add((id1, id2))

    for i in range(4):
        if pTree.pHijo[i]:
            TestAllCandidatos(pTree.pHijo[i], depth, ancestorStack, colisiones_detectadas)

    depth -= 1


def obtener_candidatos(pArbol: Nodo) -> set:
    candidatos = set()
    MAX_DEPTH = 40
    ancestorStack = [None] * MAX_DEPTH
    depth = 0
    TestAllCandidatos(pArbol, depth, ancestorStack, candidatos)
    return candidatos


# --- RENDERIZADO MEJORADO ---
def dibujar_quadtree(ax, nodo, colisiones: set):
    if nodo is not None:
        # 1. Estilos de las celdas (Líneas de la cuadrícula)
        colores_linea = {0: "#1a202c", 1: "#2b6cb0", 2: "#2c7a7b", 3: "#9b2c2c"}
        estilos_linea = {0: "-",       1: "--",      2: "-.",      3: ":"}
        grosores_linea = {0: 2.5,       1: 1.8,       2: 1.2,       3: 0.9}

        c_lin = colores_linea.get(nodo.prof, "#cbd5e0")
        e_lin = estilos_linea.get(nodo.prof, ":")
        g_lin = grosores_linea.get(nodo.prof, 0.5)

        x_min = nodo.centro.x - nodo.mitadAncho
        y_min = nodo.centro.y - nodo.mitadAncho
        ancho_celda = nodo.mitadAncho * 2

        rect_celda = patches.Rectangle((x_min, y_min), ancho_celda, ancho_celda,
                                       edgecolor=c_lin, facecolor='none', linestyle=e_lin, lw=g_lin)
        ax.add_patch(rect_celda)

        # 2. Paleta de colores para el FONDO y BORDE de los objetos según su nivel
        colores_fondo_obj = {0: "#e2e8f0", 1: "#ebf8ff", 2: "#e6fffa", 3: "#feebc8"}
        colores_borde_obj = {0: "#4a5568", 1: "#2b6cb0", 2: "#2c7a7b", 3: "#b7791f"}

        for pObj in nodo.pObjList:
            # Comprobar si este objeto está en alguna colisión
            en_colision = any(pObj.id in par for par in colisiones)
            
            color_fondo = colores_fondo_obj.get(nodo.prof, "#ffffff")
            
            if en_colision:
                color_borde = '#e53e3e'  # Rojo brillante de colisión
                grosor_borde = 2.5
                estilo_borde = '-'
            else:
                color_borde = colores_borde_obj.get(nodo.prof, "#718096")
                grosor_borde = 1.2
                estilo_borde = '-'

            rect_objeto = patches.Rectangle((pObj.x, pObj.y), pObj.ancho, pObj.alto,
                                            edgecolor=color_borde, facecolor=color_fondo, 
                                            alpha=0.5, lw=grosor_borde, linestyle=estilo_borde)
            ax.add_patch(rect_objeto)
            
            # Texto Informativo: Muestra ID y el NIVEL
            centro_x = pObj.x + pObj.ancho / 2.0
            centro_y = pObj.y + pObj.alto / 2.0
            ax.text(centro_x, centro_y, f"ID:{pObj.id}\nNiv:{nodo.prof}",
                    fontsize=8, ha='center', va='center', weight='bold', color='#1a202c')

        # Llamada recursiva a los hijos
        for hijo in nodo.pHijo:
            dibujar_quadtree(ax, hijo, colisiones)


# --- BLOQUE PRINCIPAL (MAIN) ---
if __name__ == "__main__":
    random.seed(200) # Semilla consistente

    centro_arbol = Punto(50.0, 50.0)
    mitad_ancho_arbol = 50.0
    profundidad_maxima = 3  
    
    raiz_quadtree = BuildQuadtree(centro_arbol, mitad_ancho_arbol, profundidad_maxima)

    lista_objetos = []
    num_objetos = 14

    for i in range(num_objetos):
        pos_x = random.uniform(5.0, 85.0)
        pos_y = random.uniform(5.0, 85.0)
        
        # Mezcla de objetos grandes y pequeños
        if i % 3 == 0:
            ancho = random.uniform(5.0, 35.0)  
            alto  = random.uniform(5.0, 35.0)
        else:
            ancho = random.uniform(4.0, 10.0)    
            alto  = random.uniform(4.0, 10.0)
        
        nuevo_aabb = Objeto(id_obj=i, x=pos_x, y=pos_y, ancho=ancho, alto=alto)
        lista_objetos.append(nuevo_aabb)
        InsertObjeto(raiz_quadtree, nuevo_aabb)

    # --- Detección de colisiones usando la función obtener_colisiones ---
    colisiones = obtener_colisiones(raiz_quadtree)
    print(f"Colisiones detectadas: {len(colisiones)}")
    print("Pares en colisión:", colisiones)

    # CONFIGURACIÓN DEL GRÁFICO
    fig, ax = plt.subplots(figsize=(11, 11))
    ax.set_title("Quadtree AABB — Código de Colores de Objetos según su Nivel de Inserción", 
                 fontsize=12, fontweight='bold', pad=15)
    
    ax.invert_yaxis() 
    # Pasamos el conjunto de colisiones a la función de dibujo
    dibujar_quadtree(ax, raiz_quadtree, colisiones)

    # Leyenda limpia
    leyenda_texto = (
        "Código de colores por Nivel:\n"
        "[-]  Nivel 0 (Raíz) -> Celda Negra        | Objeto Gris\n"
        "[--] Nivel 1        -> Celda Azul         | Objeto Azul Claro\n"
        "[-.] Nivel 2        -> Celda Verde         | Objeto Verde Claro\n"
        "[:]  Nivel 3        -> Celda Roja          | Objeto Naranja Claro\n\n"
        "Estado de Colisión:\n"
        "[!]  Borde Rojo Grueso = Objeto en colisión (Fase Estrecha)"
    )
    ax.text(2, 98, leyenda_texto, fontsize=9.5, fontfamily='sans-serif',
            bbox=dict(facecolor='white', alpha=0.9, edgecolor='#cbd5e0', boxstyle='round,pad=0.5'))

    ax.set_xlim(0, 100)
    ax.set_ylim(100, 0)
    ax.set_aspect('equal')
    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y (Invertido)")
    
    plt.tight_layout()
    plt.show()
