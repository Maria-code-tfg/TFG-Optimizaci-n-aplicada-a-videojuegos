# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 22:26:15 2026

@author: María
"""

class Grafos:
    def __init__(self):
        #Uso un diccionario de diccionarios
        self.nodos = {}
        
    def añadir_nodo(self, nodo):
        #Añade un nodo al grafo si no estaba antes
        if nodo not in self.nodos:
            self.nodos[nodo]={}
            
    def añadir_aristas(self, origen, destino, peso, dirigida=False):
        #Añadimos arista al grafo, si el origen o el destino no están se añaden
        self.añadir_nodo(origen)
        self.añadir_nodo(destino)
        self.nodos[origen][destino] = peso
        if not dirigida:
            self.nodos[destino][origen] = peso
            
    def vecinos(self, nodo):
        if nodo in self.nodos:
            for vecino, peso in self.nodos[nodo].items():
                yield vecino, peso
                
    def __str__(self):
        """Muestra el grafo de forma legible (para depurar)."""
        resultado = ""
        for nodo, vecinos in self.nodos.items():
            resultado += f"{nodo} -> {vecinos}\n"
        return resultado