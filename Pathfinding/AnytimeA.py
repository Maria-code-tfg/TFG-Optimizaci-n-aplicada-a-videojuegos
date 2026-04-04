# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 19:12:43 2026

@author: María
"""

from mapa import Cuadricula as cuad
from IndexPQ import IndexPQ as queue
import time

#Implementación Anytime Dynamic A*
class AnytimeA():
    def __init__(self, mapa:cuad, inicio,fin,epsilon=1,t_max=float('inf')):
        self.mapa = mapa
        self.inicio = inicio
        self.fin = fin
        self.open = queue() # Creamos la cola de prioridad de los nodos que tenemos que procesar y son inconsistentes (g(s)!=rhs(s))
        self.closed = set() # Conjunto que guarda los nodos que han sido procesados en la iteración en la que estamos
        self.incons = set() # Conjunto que guarda los nodos que estaban en closed y que son inconsistentes
        self.modificador = 0 # Acumulador de distancia recorrida por el agente.
                             # Evita el coste computacional O(N) de tener que recalcular las heurísticas 
                             # de todos los nodos en la cola OPEN cada vez que el agente da un paso. 
                             # En su lugar, ajusta matemáticamente la prioridad de los nodos nuevos.
        self.epsilon = epsilon # Tolerancia inicial
        self.g = {} # Diccionario que almacena la distancia de los nodos al final
        self.rhs = {} # Diccionario que almacena predicción a un paso (lookahead). Calcula el coste
                      # teniendo en cuenta lo que cuesta llegar al final desde cada vecino
        self.t_max = t_max
        self.tiempo_excedido = False
        self.inicializar()
        self.compute_shortest_path()
        
    def heuristica(self,s,s_prima):
        #Heurística usada, se puede cambiar
        return abs(s[0]-s_prima[0])+abs(s[1]-s_prima[1])
    
    def inicializar(self):
        # Inicializamos todos los nodos a infinito, para después calcular las distancias mínimas
        for x in range(self.mapa.ancho):
            for y in range(self.mapa.largo):
                self.g[(x, y)] = float('inf')
                self.rhs[(x, y)] = float('inf')
        # La meta tiene distancia 0
        self.rhs[self.fin] = 0
        clave = self.key(self.fin)
        self.open.update(self.fin, clave)
        
    def key(self,s):
        if (self.g[s]>self.rhs[s]):
            return (self.rhs[s]+self.epsilon*self.heuristica(self.inicio, s)+self.modificador, self.rhs[s])
        else:
            return (self.g[s]+self.heuristica(self.inicio,s)+self.modificador, self.g[s])
    
    def update_state(self, s):
        if s != self.fin:
            (x1,y1)=s
            # El coste rhs de cada s es el minimo de sumar la distancia a uno de sus vecinos
            # y la distancia de ese vecino a la meta
            self.rhs[s] = min(self.mapa.dist(x,y) + self.g[(x,y)] for (x,y) in self.mapa.vecinos(x1,y1))
        i = self.open.posiciones.get(s,0)
        if i!=0:
            # Si el elemento está en open, lo eliminamos porque lo vamos a procesar
            self.open.remove(s)
        if self.g[s]!=self.rhs[s]:
            if s not in self.closed:
                clave = self.key(s)
                self.open.update(s, clave)
            else:
                self.incons.add(s)
        else:
            # Lo sacamos de inconsistentes si ya está arreglado
            self.incons.discard(s)
        
    def compute_shortest_path(self, epsilon_cambiado=False):
        self.closed = set()
        for s in self.incons:
            self.open.update(s, self.key(s))
        if epsilon_cambiado:
            #Solo se recalculan los costes de los nodos si la tolerancia se ha modificado
            elementos_open = [self.open.array[i]["elem"] for i in range(1, len(self.open.array))]
            for s in elementos_open:
                self.open.update(s, self.key(s))
        self.incons = set()
        tiempo_inicio = time.time()
        tiempo = 0
        while ((not self.open.is_empty()) and (self.open.top()["prioridad"] < self.key(self.inicio) or 
                                               self.rhs[self.inicio] != self.g[self.inicio]) and (tiempo<self.t_max)):
            s = self.open.pop()
            if self.g[s] > self.rhs[s]:
                # Si es sobreconsistente, g(s) puede hacerse menor igualándolo a rhs(s)
                self.g[s] = self.rhs[s]
                self.closed.add(s)
            else:
                # Si es bajoconsistente, actualizamos su coste
                self.g[s] = float('inf')
                self.update_state(s)
            (x,y)=s
            for vecino in self.mapa.vecinos(x,y):
                self.update_state(vecino)
            tiempo = time.time()-tiempo_inicio
        self.tiempo_excedido = tiempo >= self.t_max
        
    def improve_path(self, disminuir_tolerancia=0.5):
        #Cuando no se detectan cambios en el mapa se ejecuta esta función en el main
        #para obtener un camino más óptimo si la tolerancia es >1 (se puede elegir la
        #disminución de la tolerancia, pero por defecto es 0.5)
        if self.epsilon>1:
            if self.epsilon-disminuir_tolerancia<1:
                self.epsilon = 1
            else:
                self.epsilon -= disminuir_tolerancia
            self.compute_shortest_path(True)
                
    def camino_hasta(self):
        camino = []
        s = self.inicio
        
        while self.tiempo_excedido and self.g[s] == float('inf'):
            print("Tiempo en Anytime A excedido, recalculando")
            self.epsilon += 1
            self.compute_shortest_path(True)
        
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
        h = abs(self.inicio[0] - nuevo_inicio[0]) + abs(self.inicio[1] - nuevo_inicio[1])
        self.modificador += h
        self.inicio = nuevo_inicio
        if recalcular:
            self.compute_shortest_path()
