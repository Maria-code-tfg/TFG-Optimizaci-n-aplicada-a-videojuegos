# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 18:14:17 2026

@author: María
"""

import pygame
import numpy as np
import time
from mapa import Cuadricula
from AnytimeA import AnytimeA
import matplotlib.pyplot as plt

# Pygame Preconfig
grid_size = int(input("Introduce el tamaño de la matriz (solo n) : "))
display_size = 600 # max window dimension (width and height)
cell_size = max(4, display_size // grid_size)
window_size = display_size

start = (0, 0) # Green 
goal = (grid_size - 1, grid_size - 1) # Red

matriz = [[1 for _ in range(grid_size)] for _ in range(grid_size)]

grid = Cuadricula(matriz)

# Pygame init
pygame.init()
win = pygame.display.set_mode((display_size, display_size))
pygame.display.set_caption("D* Lite Pathfinding")

def draw(grid_obj, camino, inicio, fin):
    colors = np.full((grid_size, grid_size, 3), 255, dtype=np.uint8) #Cuadrícula base

    for y in range(grid_size):
        for x in range(grid_size):
            if grid_obj.dist(x, y) == float('inf'): #Si es inf el valor es un muro
                colors[x, y] = [0, 0, 0]
    # Dibujar el camino
    for (px, py) in camino:
        if (px, py) != inicio and (px, py) != fin:
            colors[px, py] = [0, 0, 255] # Azul

    colors[inicio] = [0, 255, 0] # Verde
    colors[fin] = [255, 0, 0]  # Rojo

    # Renderizado en Pygame
    surf = pygame.surfarray.make_surface(np.transpose(colors, (1, 0, 2)))
    scaled = pygame.transform.scale(surf, (display_size, display_size))
    win.blit(scaled, (0, 0))
    pygame.display.update()

tiempos_anytime = []

# Initial path
anytime = AnytimeA(grid, start, goal, 3, 0.005)
path = anytime.camino_hasta()
clock = pygame.time.Clock()


running = True
while running:
    cambios = False
    clock.tick(30)
    draw(grid, path, start, goal)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key in [pygame.K_w, pygame.K_UP]: dx = -1
            if event.key in [pygame.K_s, pygame.K_DOWN]: dx = 1
            if event.key in [pygame.K_a, pygame.K_LEFT]: dy = -1
            if event.key in [pygame.K_d, pygame.K_RIGHT]: dy = 1
            
            if dx != 0 or dy != 0:
                nuevo_x, nuevo_y = start[0] + dx, start[1] + dy
                if 0 <= nuevo_x < grid_size and 0 <= nuevo_y < grid_size:
                    if grid.dist(nuevo_x, nuevo_y) != float('inf'):
                        start = (nuevo_x, nuevo_y)
                        if start in path:
                            # Seguimos en el camino: Anytime solo actualiza su km internamente
                            anytime.mover_inicio(start,False)
                            # Acortamos la ruta visual
                            indice = path.index(start)
                            path = path[indice:]
                        else:
                            t0 = time.time()
                            anytime.mover_inicio(start,True)
                            path = anytime.camino_hasta()
                            elapsed_ms = (time.time() - t0) * 1000
                            print(f"Tiempo Anytime Dynamic A*: {elapsed_ms:.2f} ms")
                            tiempos_anytime.append(elapsed_ms)
                            cambios = True

    mouse_buttons = pygame.mouse.get_pressed()
    if any(mouse_buttons):
        x, y = pygame.mouse.get_pos()
        if x >= window_size or y >= window_size:
            continue

        grid_x, grid_y = y // cell_size, x // cell_size
        if (grid_x, grid_y) in [start, goal]:
            continue

        if mouse_buttons[0]:  # left-click: add
            if grid.dist(grid_x, grid_y) != float('inf'):
                if (grid_x, grid_y) in path:
                    t0 = time.time()
                    anytime.update_cell(grid_x, grid_y, True, True)
                    path = anytime.camino_hasta()
                    elapsed_ms = (time.time() - t0) * 1000
                    
                    print(f"Ruta Bloqueada -> Anytime: {elapsed_ms:.2f} ms")
                    tiempos_anytime.append(elapsed_ms)
                    cambios = True
                else:
                    # El muro no molesta. Anytime se actualiza en silencio para no 
                    # desincronizar su grafo
                    anytime.update_cell(grid_x, grid_y, True, False)

        elif mouse_buttons[2]:  # right-click: remove
            if grid.dist(grid_x, grid_y) == float('inf'):
                grid.actualizar_casilla(grid_x, grid_y, False)
                t0 = time.time()
                anytime.update_cell(grid_x, grid_y, False, True)
                path = anytime.camino_hasta()
                elapsed_ms = (time.time() - t0) * 1000
                print(f"Tiempo Anytime: {elapsed_ms:.2f} ms")
                tiempos_anytime.append(elapsed_ms)
                cambios = True
                
    if (not cambios) and anytime.epsilon>1:
        anytime.improve_path(0.2)
        print("Mejorando camino")
        path = anytime.camino_hasta()

pygame.quit()

if tiempos_anytime:
    interacciones = range(1, len(tiempos_anytime) + 1)
    plt.figure(figsize=(10, 6))
    
    plt.plot(interacciones, tiempos_anytime, label='Anytime', color='red', marker='o', alpha=0.7)
    
    plt.xlabel('Número de Interacción (Movimiento o cambio de Muro)', fontsize=12)
    plt.ylabel('Tiempo de Cálculo (milisegundos)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)
    
    # Usar escala logarítmica si la diferencia es gigantesca (opcional, muy útil en mapas grandes)
    # plt.yscale('log') 
    
    plt.tight_layout()
    plt.show()