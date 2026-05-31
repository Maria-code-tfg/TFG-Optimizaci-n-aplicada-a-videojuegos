# -*- coding: utf-8 -*-
"""
Created on Tue May 12 23:00:42 2026

@author: María
"""

from Punto import * 
from AABB import *
from math import sqrt

class Esfera:
    def __init__(self,centro:Punto,radio:float):
        self.centro = centro
        self.radio = radio
        
    def test_intersección(self,b):
        d=Vector(self.centro.x-b.centro.x,self.centro.y-b.centro.y)
        distancia2 = d.prod_escalar(d)
        suma_radios = self.radio + b.radio
        return distancia2 <= (suma_radios*suma_radios)
    
    def punto_dentro(self, p:Punto):
        if self.radio < 0:
            return False
        dx = p.x - self.centro.x
        dy = p.y - self.centro.y
        return dx*dx + dy*dy <= self.radio*self.radio+ERROR
    

# ALGORITMOS PARA OBTENER ESFERAS

# ALGORITMO RITTER
def Puntos_mas_separados_AABB(poligono: list[Punto])->tuple[int,int]:
    """
    Obtiene los puntos que serían los extremos del AABB que encierra al polígono.
    """
    minx, maxx, miny, maxy = 0,0,0,0
    num_puntos = len(poligono)
    for i in range(1,num_puntos):
        if (poligono[i].x < poligono[minx].x): minx = i
        if (poligono[i].x > poligono[maxx].x): maxx = i
        if (poligono[i].y < poligono[miny].y): miny = i
        if (poligono[i].y > poligono[maxy].y): maxy = i
    vector_x = Vector(poligono[maxx].x-poligono[minx].x,poligono[maxx].y-poligono[minx].y)
    vector_y = Vector(poligono[maxy].x-poligono[miny].x,poligono[maxy].y-poligono[miny].y)
    
    dist2x = vector_x.prod_escalar(vector_x)
    dist2y = vector_y.prod_escalar(vector_y)
    
    minimo = minx
    maximo = maxx
    if dist2y > dist2x:
        minimo = miny
        maximo = maxy
    return minimo,maximo

def Esfera_de_puntos_mas_separados(poligono: list[Punto])->Esfera:
    """
    Obtiene la esfera que tiene como centro el punto medio del AABB que encierra
    al polígono.
    """
    minimo,maximo = Puntos_mas_separados_AABB(poligono)
    centro = Punto((poligono[minimo].x+poligono[maximo].x)/2,(poligono[minimo].y+poligono[maximo].y)/2)
    vector_radio = Vector(poligono[maximo].x-centro.x,poligono[maximo].y-centro.y)
    radio2 = vector_radio.prod_escalar(vector_radio)
    return Esfera(centro, sqrt(radio2))

def Esfera_de_esfera_y_punto(s: Esfera, p: Punto)->Esfera:
    """
    Dada una esfera y un punto, si el punto no está en el interior de la esfera, genera
    una nueva esfera a partir de la que ya se tenía para que encierre también al punto p.
    """
    d = Vector(p.x-s.centro.x, p.y-s.centro.y)
    dist2 = d.prod_escalar(d)
    if (dist2>(s.radio*s.radio)):
        dist = sqrt(dist2)
        nuevo_radio = (s.radio+dist)/2
        k = (nuevo_radio-s.radio)/dist
        s.radio=nuevo_radio
        s.centro=Punto(s.centro.x+d.prod(k).x,s.centro.y+d.prod(k).y)
    return s
        
def Esfera_Ritter(poligono: list[Punto])->Esfera:
    num_puntos = len(poligono)
    s = Esfera_de_puntos_mas_separados(poligono)
    for i in range(num_puntos):
        s = Esfera_de_esfera_y_punto(s, poligono[i])
    return s
        
# ALGORITMO RITTER CON PCA
def Matriz_Covarianza(poligono: list[Punto])->Matriz:
    num_puntos = len(poligono)
    oon = 1.0/float(num_puntos)
    c = Punto(0.0,0.0)
    e00,e11,e01 = 0.0,0.0,0.0
    for i in range(num_puntos):
        c = c+poligono[i]
    c = Punto(c.x*oon,c.y*oon)
    for i in range(num_puntos):
        p=poligono[i]-c
        e00 += p.x*p.x
        e11 += p.y*p.y
        e01 += p.x*p.y
    cov = Matriz([[0,0],[0,0]])
    cov.valores[0][0]=e00*oon
    cov.valores[1][1]=e11*oon
    cov.valores[0][1]=e01*oon
    cov.valores[1][0]=cov.valores[0][1]
    return cov

def SymSchur2(a:Matriz, p:int, q:int):
    if abs(a.valores[p][q])>0.0001:
        r=(a.valores[q][q]-a.valores[p][p])/(2.0*a.valores[p][q])
        if (r>=0.0):
            t=1.0/(r+sqrt(1.0 + r*r))
        else:
            t = -1.0/(-r+sqrt(1.0 + r*r))
        c = 1.0/sqrt(1.0+t*t)
        s = t*c
    else:
        c=1.0
        s=0.0
    return c,s

def Jacobi(a:Matriz):
    J = Matriz([[0.0,0.0],[0.0,0.0]])
    b = Matriz([[0.0,0.0],[0.0,0.0]])
    t = Matriz([[0.0,0.0],[0.0,0.0]])
    v = Matriz([[0.0,0.0],[0.0,0.0]])
    prevoff = 0.0
    for i in range(2):
        v.valores[i][i] = 1.0
    max_iteraciones = 50
    for n in range(max_iteraciones):
        p=0
        q=1
        for i in range(2):
            for j in range(2):
                if (i==j): continue
                if (abs(a.valores[i][j])>abs(a.valores[p][q])):
                    p=i
                    q=j
        c,s = SymSchur2(a, p, q)
        for i in range(2):
            J.valores[i][0]=0.0
            J.valores[i][1]=J.valores[i][0]
            J.valores[i][i]=1.0
        J.valores[p][p]=c
        J.valores[p][q]=s
        J.valores[q][p]=-s
        J.valores[q][q]=c
        v=v*J
        Jt=J.transpuesta()
        a1 = Jt*a
        a = a1*J
        off = 0
        for i in range(2):
            for j in range(2):
                if (i==j): continue
                off += a.valores[i][j] * a.valores[i][j]
        if (n>2 and off >= prevoff):
            return a,v
        prevoff = off
        
def EigenEsfera(poligono: list[Punto]):
    m = Matriz_Covarianza(poligono)
    m,v = Jacobi(m)
    maxc = 0
    maxe = abs(m.valores[0][0])
    if (abs(m.valores[1][1])>maxe):
        maxc=1
        maxe=m.valores[1][1]
    e = Vector(v.valores[0][maxc],v.valores[1][maxc])
    imin, imax = puntos_extremos_en_dirección(e, poligono)
    punto_min = poligono[imin]
    punto_max = poligono[imax]
    vector = Vector(punto_max.x-punto_min.x,punto_max.y-punto_min.y)
    dist = sqrt(vector.prod_escalar(vector))
    radio = dist/2
    centro = Punto((punto_max.x+punto_min.x)/2,(punto_max.y+punto_min.y)/2)
    esfera = Esfera(centro, radio)
    return esfera

def RitterEigenSphere(poligono: list[Punto]):
    s = EigenEsfera(poligono)
    n = len(poligono)
    for i in range(n):
        s = Esfera_de_esfera_y_punto(s, poligono[i])
    return s

# ALGORITMO DE WELZL

# Funciones auxiliares para definir círculos a partir de puntos (de 0 a 3)

def circulo_cero_puntos():
    return Esfera(Punto(0,0),-1)

def circulo_un_punto(p:Punto):
    return Esfera(p,0)

def circulo_dos_puntos(p:Punto, q:Punto):
    centro = Punto((p.x+q.x)/2,(p.y+q.y)/2)
    radio = sqrt(((p.x-q.x)**2+(p.y-q.y)**2))/2
    return Esfera(centro,radio)

def circulo_tres_puntos(p:Punto,q:Punto,r:Punto):
    x1, y1 = p.x, p.y
    x2, y2 = q.x, q.y
    x3, y3 = r.x, r.y
    D = 2 * (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))    
    if abs(D) < ERROR:

        candidatos = [
            circulo_dos_puntos(p, q),
            circulo_dos_puntos(p, r),
            circulo_dos_puntos(q, r)
        ]
    
        mejor = None
    
        for circ in candidatos:
    
            if (circ.punto_dentro(p) and
                circ.punto_dentro(q) and
                circ.punto_dentro(r)):
    
                if mejor is None or circ.radio < mejor.radio:
                    mejor = circ
    
        return mejor  
    # Se calcula el circuncentro del triángulo que definen los tres puntos, que es el centro del círculo
    Ux = ((x1**2 + y1**2)*(y2 - y3) + (x2**2 + y2**2)*(y3 - y1) + (x3**2 + y3**2)*(y1 - y2)) / D    
    Uy = ((x1**2 + y1**2)*(x3 - x2) + (x2**2 + y2**2)*(x1 - x3) + (x3**2 + y3**2)*(x2 - x1)) / D
    centro = Punto(Ux,Uy)
    radio = sqrt((Ux-x1)**2 + (Uy-y1)**2)
    return Esfera(centro,radio)

# Función para obtener el círculo más pequeño que contiene al polígono

def EsferaWelzl(poligono:list[Punto], num_puntos: int, sos: list[Punto], num_sos: int):
    if num_puntos == 0 or num_sos == 3:
        if num_sos==0:
            return circulo_cero_puntos()
        elif num_sos==1:
            return circulo_un_punto(sos[0])
        elif num_sos==2:
            return circulo_dos_puntos(sos[0], sos[1])
        elif num_sos==3:
            return circulo_tres_puntos(sos[0], sos[1], sos[2])
    else:
        i = num_puntos-1
        esfera_pequeña = EsferaWelzl(poligono, num_puntos-1, sos, num_sos)
        if (esfera_pequeña.punto_dentro(poligono[i])):
            return esfera_pequeña
        else:
            sos[num_sos] = poligono[i]
            return EsferaWelzl(poligono, num_puntos-1, sos, num_sos+1)
        
def obtener_esfera(poligono: list[Punto]):
    sos = [None]*3
    num_puntos = len(poligono)
    circulo = EsferaWelzl(poligono,num_puntos,sos,0)
    return circulo