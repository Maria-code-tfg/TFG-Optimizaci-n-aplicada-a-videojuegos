# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 22:07:41 2026

@author: María
"""

class IndexPQ:
    def __init__(self):
        self.array = [None] 
        self.posiciones = {}

    def push(self, e, prioridad):
        if e in self.posiciones:
            raise ValueError("No se pueden insertar elementos repetidos.")
        
        self.array.append({"elem": e, "prioridad": prioridad})
        self.posiciones[e] = self.size()
        self._flotar(self.size())

    def update(self, e, prioridad):
        # Si el elemento no está, get() devuelve 0
        i = self.posiciones.get(e, 0) 
        
        if i == 0:
            # El elemento se inserta por primera vez
            self.push(e, prioridad)
        else:
            self.array[i]["prioridad"] = prioridad
            # Si no es la raíz y tiene más prioridad (menor valor) que su padre, flota
            if i != 1 and prioridad < self.array[i // 2]["prioridad"]:
                self._flotar(i)
            else:
                # Si no, puede que haga falta hundirlo
                self._hundir(i)

    def size(self):
        return len(self.array) - 1

    def is_empty(self):
        return self.size() == 0

    def top(self):
        if self.is_empty():
            raise ValueError("No se puede consultar el primero de una cola vacía.")
        return self.array[1]

    def pop(self):
        if self.is_empty():
            raise ValueError("No se puede eliminar el primero de una cola vacía.")
        
        top_elem = self.array[1]["elem"]
        del self.posiciones[top_elem] # Lo quitamos del registro
        
        if self.size() > 1:
            # Movemos el último elemento a la raíz
            self.array[1] = self.array.pop()
            self.posiciones[self.array[1]["elem"]] = 1
            self._hundir(1)
        else:
            self.array.pop()
            
        return top_elem

    def priority(self, e):
        i = self.posiciones.get(e, 0)
        if i == 0:
            raise ValueError("No se puede consultar la prioridad de un elemento no insertado.")
        return self.array[i]["prioridad"]

    def _flotar(self, i):
        parmov = self.array[i]
        hueco = i
        # Mientras no sea la raíz y tenga más prioridad que su padre
        while hueco != 1 and parmov["prioridad"] < self.array[hueco // 2]["prioridad"]:
            self.array[hueco] = self.array[hueco // 2]
            self.posiciones[self.array[hueco]["elem"]] = hueco
            hueco //= 2
            
        self.array[hueco] = parmov
        self.posiciones[self.array[hueco]["elem"]] = hueco

    def _hundir(self, i):
        parmov = self.array[i]
        hueco = i
        hijo = 2 * hueco # hijo izquierdo
        
        while hijo <= self.size():
            # Cambiar al hijo derecho si existe y tiene más prioridad que el izquierdo
            if hijo < self.size() and self.array[hijo + 1]["prioridad"] < self.array[hijo]["prioridad"]:
                hijo += 1
                
            # Flotar el hijo si va antes que el elemento que se está hundiendo
            if self.array[hijo]["prioridad"] < parmov["prioridad"]:
                self.array[hueco] = self.array[hijo]
                self.posiciones[self.array[hueco]["elem"]] = hueco
                hueco = hijo
                hijo = 2 * hueco
            else:
                break
                
        self.array[hueco] = parmov
        self.posiciones[self.array[hueco]["elem"]] = hueco