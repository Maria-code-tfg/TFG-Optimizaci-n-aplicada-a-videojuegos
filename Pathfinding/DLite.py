# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 22:13:52 2026

@author: María
"""
from mapa import Cuadricula as cuad
from IndexPQ import IndexPQ as queue

#Implementación D* Lite
class DLite():
    def __init__(self, mapa:cuad, inicio,fin):
        self.mapa = mapa
        self.inicio = inicio
        self.fin = fin
        self.open = queue()
        self.open_set = {}
        self.km = 0
        self.g = {}
        self.rhs = {}
        self.inicializar()
        self.compute_shortest_path()
    
    def inicializar(self):
        for x in range(self.mapa.ancho):
            for y in range(self.mapa.largo):
                self.g[(x, y)] = float('inf')
                self.rhs[(x, y)] = float('inf')
        self.rhs[self.fin] = 0
        clave = self.key(self.fin)
        self.open.update(self.fin, clave)
        self.open_set[self.fin]=clave
        
    def key(self,s):
        return (min(self.g[s], self.rhs[s]) + abs(self.inicio[0] - s[0]) + abs(self.inicio[1] - s[1])+self.km,
                    min(self.g[s], self.rhs[s]))
    
    def update_state(self, s):
        if s != self.fin:
            (x1,y1)=s
            self.rhs[s] = min(self.mapa.dist(x,y) + self.g[(x,y)] for (x,y) in self.mapa.vecinos(x1,y1))
        if s in self.open_set:
            self.open_set.pop(s,None)
        if self.g[s] != self.rhs[s]:
            clave = self.key(s)
            self.open.update(s, clave)
            self.open_set[s]=clave
        
    def compute_shortest_path(self):
        while not self.open.is_empty() and self.open.array[1]["prioridad"] < self.key(self.inicio) or self.rhs[self.inicio] != self.g[self.inicio]:
            top_dict = self.open.top()
            s = top_dict["elem"]
            k_old = top_dict["prioridad"]
            self.open.pop()
            if self.open_set.get(s) == k_old:
                self.open_set.pop(s, None)
            else:
                continue
            if self.g[s] > self.rhs[s]:
                self.g[s] = self.rhs[s]
            else:
                self.g[s] = float('inf')
                self.update_state(s)
            (x,y)=s
            for vecino in self.mapa.vecinos(x,y):
                self.update_state(vecino)
                
    def camino_hasta(self):
        camino = []
        s = self.inicio
        
        if self.g[s] == float('inf'):
            return []

        visitados = set()
        while s != self.fin:
            (x,y)=s
            camino.append(s)
            visitados.add(s)
            vecinos = self.mapa.vecinos(x,y)
            vecinos_sin_muros = []
            for v in vecinos:
                (x,y)=v
                if self.mapa.dist(x, y)!=float('inf') and v not in visitados:
                    vecinos_sin_muros.append(v)

            if not vecinos_sin_muros:
                return []

            s_next = min(vecinos_sin_muros, key=lambda s_prime: self.g.get(s_prime, float('inf')))

            if self.g.get(s_next, float('inf')) == float('inf'):
                return []

            s = s_next

        camino.append(self.fin)
        return camino
    
    def update_cell(self, x, y, is_obstacle, coste=1):
        self.mapa.matriz[y][x] = float('inf') if is_obstacle else coste
        for s_next in self.mapa.vecinos(x, y):
            self.update_state(s_next)
        self.compute_shortest_path()
        
    def mover_inicio(self, nuevo_inicio):
        h = abs(self.inicio[0] - nuevo_inicio[0]) + abs(self.inicio[1] - nuevo_inicio[1])
        self.km += h
        self.inicio = nuevo_inicio
        self.compute_shortest_path()