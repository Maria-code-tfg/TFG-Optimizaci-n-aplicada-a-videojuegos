# -*- coding: utf-8 -*-
"""
Created on Sun May 10 20:48:52 2026

@author: María
"""
from Punto import Punto

class AABB_min_max:
    """
    Representación de los AABB mediante coordenadas mínimas y máximas en x e y de sus puntos.
    """
    def __init__(self, poligono:list[Punto])->None:
        self.minimos = [min(poligono, key= lambda p: p.x).x,min(poligono, key= lambda p: p.y).y] 
        self.maximos = [max(poligono, key= lambda p: p.x).x,max(poligono, key= lambda p: p.y).y]
        
    def generar_vertices(self)->list[Punto]:
        v1 = Punto(self.minimos[0],self.minimos[1])
        v2 = Punto(self.minimos[0],self.maximos[1])
        v3 = Punto(self.maximos[0],self.maximos[1])
        v4 = Punto(self.maximos[0],self.minimos[1])
        return [v1,v2,v3,v4]
    
    def test_intersección(self, b):
        if (self.maximos[0]<b.minimos[0] or self.minimos[0]>b.maximos[0]): return False
        if (self.maximos[1]<b.minimos[1] or self.minimos[1]>b.maximos[1]): return False
        return True
    
class AABB_min_diam:
    """
    Representación de los AABB mediante coordenadas mínimas en x e y y la distancia a los
    extremos en x e y.
    """
    def __init__(self, poligono:list[Punto])->None:
        self.minimo = Punto(min(poligono, key= lambda p: p.x).x,min(poligono, key= lambda p: p.y).y)
        self.diametros = [max(poligono, key= lambda p: p.x).x - min(poligono, key= lambda p: p.x).x, 
                          max(poligono, key= lambda p: p.y).y - min(poligono, key= lambda p: p.y).y]
        
    def generar_vertices(self)->list[Punto]:
        v1 = self.minimo
        v2 = Punto(self.minimo.x +self.diametros[0],self.minimo.y)
        v3 = Punto(self.minimo.x +self.diametros[0],self.minimo.y+self.diametros[1])
        v4 = Punto(self.minimo.x,self.minimo.y+self.diametros[1])
        return [v1,v2,v3,v4]
    
    def test_intersección(self, b):
        if (self.minimo.x-b.minimo.x>b.diametros[0] or -(self.minimo.x>b.minimo.x)>self.diametros[0]): return False
        if (self.minimo.y-b.minimo.y>b.diametros[1] or -(self.minimo.y>b.minimo.y)>self.diametros[1]): return False
        return True
    
class AABB_centro:
    """
    Representación de los AABB mediante el centro del polígono y la distancia a los
    extremos en x e y.
    """
    def __init__(self, poligono:list[Punto])->None:
        self.centro=Punto((max(poligono, key= lambda p: p.x).x+min(poligono, key= lambda p: p.x).x)/2,
                          (max(poligono, key= lambda p: p.y).y+min(poligono, key= lambda p: p.y).y)/2)
        self.radios = [abs(max(poligono, key= lambda p: abs(p.x-self.centro.x)).x-self.centro.x),
                       abs(max(poligono, key= lambda p: abs(p.y-self.centro.y)).y-self.centro.y)]
        
    def generar_vertices(self)->list[Punto]:
        v1 = Punto(self.centro.x - self.radios[0], self.centro.y - self.radios[1])
        v2 = Punto(self.centro.x + self.radios[0], self.centro.y - self.radios[1])
        v3 = Punto(self.centro.x + self.radios[0], self.centro.y + self.radios[1])
        v4 = Punto(self.centro.x - self.radios[0], self.centro.y + self.radios[1])
        return [v1, v2, v3, v4]
                
    def test_intersección(self, b):
        if (abs(self.centro.x - b.centro.x) > (self.radios[0] + b.radios[0])): return False
        if (abs(self.centro.y - b.centro.y) > (self.radios[1] + b.radios[1])): return False
        return True