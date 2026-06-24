# -*- coding: utf-8 -*-
"""
Created on Mon May 18 00:38:43 2026

@author: María
"""

from Punto import * 
from math import sqrt,hypot
import math

class OBB:
    def __init__(self, origen:Punto, ejes: list[Vector], radios: list[float]):
        self.c = origen
        self.u = ejes
        self.e = radios
    
    def test_interseccion(self, b: 'OBB') -> bool:
        R = Matriz([[0.0, 0.0], [0.0, 0.0]])
        AbsR = Matriz([[0.0, 0.0], [0.0, 0.0]])

        # Calcular la matriz de rotación que expresa b en el sistema de coordenadas de self
        for i in range(2):
            for j in range(2):
                R.valores[i][j] = self.u[i].prod_escalar(b.u[j])
                AbsR.valores[i][j] = abs(R.valores[i][j]) + ERROR

        # Calcular el vector de traslación t (distancia entre centros)
        t_global = Vector(b.c.x - self.c.x, b.c.y - self.c.y)

        # Llevar la traslación al sistema de coordenadas de self
        t = [t_global.prod_escalar(self.u[0]),t_global.prod_escalar(self.u[1])]

        # Testear los ejes de 'self' (L = A0, L = A1)
        for i in range(2):
            ra = self.e[i]
            rb = b.e[0] * AbsR.valores[i][0] + b.e[1] * AbsR.valores[i][1]
            if abs(t[i]) > ra + rb:
                return False  # Hay separación, no intersectan

        # Testear los ejes de 'b' (L = B0, L = B1)
        for i in range(2):
            ra = self.e[0] * AbsR.valores[0][i] + self.e[1] * AbsR.valores[1][i]
            rb = b.e[i]
            if abs(t[0] * R.valores[0][i] + t[1] * R.valores[1][i]) > ra + rb:
                return False  # Hay separación, no intersectan

        return True
        
        
    def generar_vertices(self)->list[Punto]:
        v1 = self.c + self.u[0].prod(self.e[0]) + self.u[1].prod(self.e[1])
        v2 = self.c - self.u[0].prod(self.e[0]) + self.u[1].prod(self.e[1])
        v3 = self.c - self.u[0].prod(self.e[0]) - self.u[1].prod(self.e[1])
        v4 = self.c + self.u[0].prod(self.e[0]) - self.u[1].prod(self.e[1])
        return [v1, v2, v3, v4]
    
def calcular_obb_minimo(pt: list[Punto]) -> OBB:
    num_pts = len(pt)
    min_area = float('inf')
    
    mejor_c = None
    mejores_u = [None, None]
    mejores_e = [0.0, 0.0]  # Aquí se almacenan los radios
    
    j = num_pts - 1
    for i in range(num_pts):
        # Obtener la arista actual e0, normalizada
        dx = pt[i].x - pt[j].x
        dy = pt[i].y - pt[j].y
        
        longitud = math.hypot(dx, dy)
        if longitud == 0: 
            j = i
            continue
            
        e0 = Vector(dx / longitud, dy / longitud)
        
        # Obtener un eje e1 ortogonal a la arista e0
        e1 = Vector(-e0.y, e0.x)
        
        # Recorrer todos los puntos para obtener las extensiones máximas
        min0, min1, max0, max1 = 0.0, 0.0, 0.0, 0.0
        
        for k in range(num_pts):
            d = Vector(pt[k].x - pt[j].x, pt[k].y - pt[j].y)
            
            dot0 = d.prod_escalar(e0)
            if dot0 < min0: min0 = dot0
            if dot0 > max0: max0 = dot0
            
            dot1 = d.prod_escalar(e1)
            if dot1 < min1: min1 = dot1
            if dot1 > max1: max1 = dot1
            
        area = (max0 - min0) * (max1 - min1)
        
        # Si encontramos un área mejor, guardamos todos los datos del OBB
        if area < min_area:
            min_area = area
            
            # Centro
            v0_escalado = e0.prod(min0 + max0)
            v1_escalado = e1.prod(min1 + max1)
            v_suma = v0_escalado + v1_escalado
            
            mejor_c = pt[j] + v_suma.prod(0.5)
            
            # Ejes directores
            mejores_u = [e0, e1]
            
            # Radios
            mejores_e = [(max0 - min0) / 2.0, (max1 - min1) / 2.0]
            
        # Actualizar j para la siguiente iteración
        j = i
    return OBB(origen=mejor_c, ejes=mejores_u, radios=mejores_e)
        