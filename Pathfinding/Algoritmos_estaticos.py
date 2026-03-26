# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 17:38:38 2026

@author: María
"""

from mapa import Cuadricula as cu
from IndexPQ import IndexPQ as queue
#Algoritmos no dinámicos

def dijkstra(cuad, inicio, final): #O(n*log n)
    """    
    Parámetros
    ----------
    map : Cuadricula
    inicio : tuple(int,int)
    final : tuple(int,int)

    Devuelve
    -------
    Distancia, camino desde inicio hasta final y nodos visitados
    """
    previos = {}
    distancias = {inicio: 0, final: float('inf')}
    
    cola = queue()
    cola.push(inicio,0)
    visitados = set()
    visitados.add(inicio)
    
    while not cola.is_empty(): #O(n*log n)
        (x,y) = cola.pop() #O(log n)
        dist_actual = distancias[(x,y)]
        visitados.add((x,y))
        if (x,y)==final:
            return dist_actual, camino_hasta(previos, inicio, final), visitados
        for (dx,dy) in cuad.vecinos(x,y): #O(1) (pues solo se calculan 4 tuplas, como mucho)
            dist_nueva = dist_actual + cuad.dist(dx,dy)
            if (dx,dy) not in distancias or dist_nueva < distancias[(dx,dy)]:
                distancias[(dx,dy)] = dist_nueva
                previos[(dx,dy)] = (x,y)
                cola.update((dx,dy), dist_nueva)
    return float('inf'), None, visitados

def camino_hasta(caminos, inicio, final):
    camino = []
    actual = final

    while actual != inicio:
        camino.append(actual)
        actual = caminos[actual]

    camino.append(inicio)
    camino.reverse()
    return camino

def A_estrella(cuad, inicio, final):
    """    
    Parámetros
    ----------
    map : Cuadricula
    inicio : tuple(int,int)
    final : tuple(int,int)

    Devuelve
    -------
    Distancia, camino desde inicio hasta final y nodos visitados
    """
    
    cola = queue()
    cola.push(inicio,0)
    previos = {}
    distancias = {inicio: 0, final: float('inf')}
    visitados = set()
    visitados.add(inicio)
    
    while not cola.is_empty():
        (x,y) = cola.pop()
        dist_actual=distancias[(x,y)]
        visitados.add((x,y))
        if (x,y)==final:
            return dist_actual, camino_hasta(previos, inicio, final), visitados
        for (dx,dy) in cuad.vecinos(x,y): #O(1) (pues solo se calculan 4 tuplas, como mucho)
            dist_nueva = dist_actual + cuad.dist(dx,dy)
            if (dx,dy) not in distancias or dist_nueva < distancias[(dx,dy)]:
                distancias[(dx,dy)] = dist_nueva
                previos[(dx,dy)] = (x,y)
                cola.update((dx,dy),dist_nueva+manhattan((dx,dy),final))
    return float('inf'), None, visitados
    
    
def manhattan(inicio,fin):
    x1,y1=inicio
    x2,y2=fin
    return abs(x1-x2) + abs(y1-y2)
        
        
        
    
