# -*- coding: utf-8 -*-
"""
Created on Sun May 10 20:57:12 2026

@author: María
"""
import random
ERROR = 1e-9

class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return "({0},{1})".format(self.x, self.y)
    def __add__(self, b):
        return Punto(self.x + b.x, self.y + b.y)
    def __sub__(self, b):
        return Punto(self.x - b.x, self.y - b.y)
    def __eq__(self, b):
        if self is None or b is None: return self is None and b is None
        return abs(self.x - b.x) < ERROR and abs(self.y - b.y) < ERROR
    def __hash__(self):
        return hash((round(self.x, 9), round(self.y, 9)))
    
class Vector:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        
    def __repr__(self):
        return "({0},{1})".format(self.x, self.y)   
    def __add__(self,b):
        return Vector(self.x + b.x, self.y + b.y) 
    def __sub__(self, b):
        return Vector(self.x - b.x, self.y - b.y)
    def __eq__(self, b):
        if self is None or b is None: return self is None and b is None
        return abs(self.x - b.x) < ERROR and abs(self.y - b.y) < ERROR
    def __hash__(self):
        return hash((round(self.x, 9), round(self.y, 9)))
    def prod(self,k:float):
        return Vector(self.x * k, self.y * k)
    def prod_escalar(self,b)->float:
        return (self.x*b.x + self.y*b.y)
    
class Matriz:
    def __init__(self, matriz: list[list]): #Las listas de dentro de la lista son las filas
        self.valores=matriz
        self.num_filas = len(matriz)
        self.num_columnas = len(matriz[0])
        
    def __mul__(self,b):
        if self.num_columnas != b.num_filas:
            raise ValueError("Dimensiones no compatibles: columnas de A deben ser igual a filas de B")
        resultado = [[0 for _ in range(b.num_columnas)] for _ in range(self.num_filas)]

        for i in range(self.num_filas):
            for j in range(b.num_columnas):
                for k in range(self.num_columnas):
                    resultado[i][j] += self.valores[i][k] * b.valores[k][j]
            
        return Matriz(resultado)
    
    def transpuesta(self):
        transpuesta = [[self.valores[i][j] for i in range(self.num_filas)] for j in range(self.num_columnas)]
        return Matriz(transpuesta)
    
def puntos_extremos_en_dirección(direc: Vector, poligono: list[Punto]):
    #Obtiene los puntos más extremos en la dirección dada
    imin = 0
    imax = 0
    minproj = float('inf')
    maxproj = float('-inf')
    n = len(poligono)
    for i in range(n):
        v_punto = Vector(poligono[i].x,poligono[i].y)
        proj = direc.prod_escalar(v_punto)
        if (proj<minproj):
            minproj = proj
            imin = i
        if (proj>maxproj):
            maxproj = proj
            imax = i
    return imin, imax

def prod_vect(u, v):
    return u.x * v.y - u.y * v.x
def det(a, b, c):
    return prod_vect(b - a, c - a)

def alineados(a: Punto, b: Punto, c: Punto) -> bool:
    # Devuelve True/False si los puntos a, b, c están alineados/no lo están
    return abs(det(a, b, c)) < ERROR

def orient(a: Punto, b: Punto, c: Punto) -> int:
    # 1/0/-1 si c a la izquierda/alineado/a la derecha de ab    
    d = det(a, b, c)
    if abs(d) < ERROR: return 0
    elif d > ERROR: return 1
    else: return -1
    
def punto_en_segmento(p, s):
    #p punto, s segmento = lista con dos puntos
    #devuelve True si p está dentro del segmento, incluyendo sus extremos
    if not alineados(p, s[0], s[1]):
        return False
    if abs(s[0].x - s[1].x) > ERROR:
        return min(s[0].x, s[1].x) - ERROR <= p.x <= max(s[0].x, s[1].x) + ERROR
    else:
        return min(s[0].y, s[1].y) - ERROR <= p.y <= max(s[0].y, s[1].y) + ERROR
    
def segmentos_se_cortan(s: list[Punto], t: list[Punto]) -> bool:
    # Input: s, t son listas con dos puntos, los extremos de los segmentos s y t.
    # Output: True/False decidiendo si s y t se cortan (incluyendo solaparse o cortarse en un extremo)
    # si los cuatro puntos están alineados
    if alineados(s[0], s[1], t[0]) and alineados(s[0], s[1], t[1]):
        return punto_en_segmento(s[0], t) or punto_en_segmento(s[1], t) or punto_en_segmento(t[0], s) or punto_en_segmento(t[1], s)        
    #si tres puntos están alineados (y no los cuatro) devuelve True solo si uno está dentro del otro segmento
    for p in s:
        if alineados(p, t[0], t[1]): return punto_en_segmento(p, t)        
    for p in t:
        if alineados(p, s[0], s[1]): return punto_en_segmento(p, s)        
    #(sabemos que no hay tres alineados) usamos xor = '^' (True ^ False = True, F^T=T T^T=F, F^F=F)
    return (orient(s[0], s[1], t[0]) * orient(s[0], s[1], t[1]) == -1) and (orient(t[0], t[1], s[0]) * orient(t[0], t[1], s[1]) == -1)

def punto_en_poligono(q: Punto, pol: list[Punto]) -> bool:
    # Input: q es un punto, pol es una lista de puntos que, en ese orden, son los vértices de un polígono (simple)
    # Output: True/False decidiendo si q está dentro de pol (incluyendo la frontera)
    # Contamos el número de cortes del polígono con un segmento que comienza en q y acaba fuera del polígono.
    # Si es par q está fuera y si es impar está dentro del polígono
    maxcoord = max(p.x for p in pol)
    # El segmento acaba en un punto cuya coordenada x es mayor que las de los vértices del polígono y su coordenada y es un real aleatorio
    t = [q, Punto(maxcoord + 1, random.uniform(-1, 1))]
    count = 0
    n = len(pol)
    for i in range(n):
        # Nos avisa si se da la improbable situación en que el segmento pasa por un vértice de pol (en cuyo no bastaría con contar intersecciones)
        # y empezamos de nuevo
        if alineados(t[0], t[1], pol[i]):
            # print(t[0], t[1], pol[i], "El rayo pasa por un vértice")
            return punto_en_poligono(q, pol)
        # Si q está encima de un lado del polígono puede fallar la cuenta de intersecciones pero la función debe devolver True
        if punto_en_segmento(q, [pol[i], pol[(i+1)%n]]): return True
        if segmentos_se_cortan([pol[i], pol[(i+1)%n]], t):
            count = count + 1
    return (count % 2 == 1)  

        