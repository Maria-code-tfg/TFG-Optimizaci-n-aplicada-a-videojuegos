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
        self.open = queue() #Creamos la cola de prioridad de los nodos que tenemos que procesar y son inconsistentes (g(s)!=rhs(s))
        self.modificador = 0 #Acumulador de distancia recorrida por el agente.
                             # Evita el coste computacional O(N) de tener que recalcular las heurísticas 
                             # de todos los nodos en la cola OPEN cada vez que el agente da un paso. 
                             # En su lugar, ajusta matemáticamente la prioridad de los nodos nuevos.
        self.g = {} #Diccionario que almacena la distancia de los nodos al final
        self.rhs = {} #Diccionario que almacena predicción a un paso (lookahead). Calcula el coste
                      #teniendo en cuenta lo que cuesta llegar al final desde cada vecino
        self.inicializar()
        self.compute_shortest_path()
        
    def heuristica(self,s,s_prima):
        return abs(s[0]-s_prima[0])+abs(s[1]-s_prima[1])
    
    def inicializar(self):
        #Inicializamos todos los nodos a infinito, para después calcular las distancias mínimas
        for x in range(self.mapa.ancho):
            for y in range(self.mapa.largo):
                self.g[(x, y)] = float('inf')
                self.rhs[(x, y)] = float('inf')
        #La meta tiene distancia 0
        self.rhs[self.fin] = 0
        clave = self.key(self.fin)
        self.open.update(self.fin, clave)
        
    def key(self,s):
        return (min(self.g[s], self.rhs[s]) + self.heuristica(self.inicio, s)+self.modificador,
                    min(self.g[s], self.rhs[s]))
    
    def update_state(self, s):
        if s != self.fin:
            (x1,y1)=s
            #El coste rhs de cada s es el minimo de sumar la distancia a uno de sus vecinos
            #y la distancia de ese vecino a la meta
            self.rhs[s] = min(self.mapa.dist(x,y) + self.g[(x,y)] for (x,y) in self.mapa.vecinos(x1,y1))
        if self.g[s] != self.rhs[s]:
            #Si el nodo es inconsistente (g(s)!=rhs(s)), se actualiza su clave
            clave = self.key(s)
            self.open.update(s, clave)
        else:
            #Si no lo es, se elimina
            if s in self.open.posiciones:
                self.open.remove(s)
        
    def compute_shortest_path(self):
        while (not self.open.is_empty()) and (self.open.top()["prioridad"] < self.key(self.inicio) or self.rhs[self.inicio] != self.g[self.inicio]):
            top_dict = self.open.top()
            s = top_dict["elem"]
            k_old = top_dict["prioridad"]
            k_new = self.key(s)
            self.open.pop()
            if k_old < k_new:
                # Si la prioridad empeoró antes de procesarlo, lo reinsertamos con la nueva
                self.open.update(s, k_new)
            elif self.g[s] > self.rhs[s]:
                #Si es sobreconsistente, g(s) puede hacerse menor igualándolo a rhs(s)
                self.g[s] = self.rhs[s]
            else:
                #Si es bajoconsistente, actualizamos su coste
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
    
    def update_cell(self, x, y, es_obstáculo, recalcular, coste=1):
        self.mapa.matriz[y][x] = float('inf') if es_obstáculo else coste
        #Actualizamos el coste de los vecinos
        for s_next in self.mapa.vecinos(x, y):
            self.update_state(s_next)
        if recalcular:
            self.compute_shortest_path()
        
    def mover_inicio(self, nuevo_inicio, recalcular):
        h = self.heuristica(self.inicio, nuevo_inicio)
        self.modificador += h
        self.inicio = nuevo_inicio
        if recalcular:
            self.compute_shortest_path()
        
    def mover_inicio(self, nuevo_inicio):
        h = abs(self.inicio[0] - nuevo_inicio[0]) + abs(self.inicio[1] - nuevo_inicio[1])
        self.km += h
        self.inicio = nuevo_inicio
        self.compute_shortest_path()
