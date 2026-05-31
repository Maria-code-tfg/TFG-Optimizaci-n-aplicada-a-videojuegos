# -*- coding: utf-8 -*-
"""
Created on Sat May 16 23:19:59 2026

@author: María
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May 16 23:19:59 2026

@author: María
"""

import random
import matplotlib.pyplot as plt
from math import sqrt
from Punto import Punto, Vector
from AABB import AABB_min_max, AABB_min_diam, AABB_centro
from Esferas import Esfera, Esfera_Ritter, RitterEigenSphere, obtener_esfera

from OBB import calcular_obb_minimo

random.seed(30)
puntos_prueba = [Punto(random.uniform(10, 80), random.uniform(15, 75)) for _ in range(25)]

# Tipos de AABB
aabb_mm = AABB_min_max(puntos_prueba)
aabb_md = AABB_min_diam(puntos_prueba)
aabb_c = AABB_centro(puntos_prueba)

# Esferas
esfera_ritter = Esfera_Ritter(puntos_prueba)
esfera_pca = RitterEigenSphere(puntos_prueba)
esfera_min = obtener_esfera(puntos_prueba)

# OBB
obb_min = calcular_obb_minimo(puntos_prueba)

fig, axs = plt.subplots(2, 4, figsize=(20, 10))
axs = axs.ravel()

def plot_base(ax, titulo):
    ax.scatter([p.x for p in puntos_prueba], [p.y for p in puntos_prueba], color='#4a5568', zorder=3, label='Puntos')
    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_aspect('equal')

# GRÁFICOS
plot_base(axs[0], "AABB: Min-Max")
v_mm = aabb_mm.generar_vertices()
x_mm = [p.x for p in v_mm] + [v_mm[0].x] # Cerramos el polígono
y_mm = [p.y for p in v_mm] + [v_mm[0].y]
axs[0].plot(x_mm, y_mm, color='#3182ce', linewidth=2)
axs[0].fill(x_mm, y_mm, color='#3182ce', alpha=0.1)

plot_base(axs[1], "AABB: Min-Diam")
v_md = aabb_md.generar_vertices()
x_md = [p.x for p in v_md] + [v_md[0].x]
y_md = [p.y for p in v_md] + [v_md[0].y]
axs[1].plot(x_md, y_md, color='#dd6b20', linewidth=2)
axs[1].fill(x_md, y_md, color='#dd6b20', alpha=0.1)

plot_base(axs[2], "AABB: Centro-Radio")
v_c = aabb_c.generar_vertices()
x_c = [p.x for p in v_c] + [v_c[0].x]
y_c = [p.y for p in v_c] + [v_c[0].y]
axs[2].plot(x_c, y_c, color='#319795', linewidth=2)
axs[2].fill(x_c, y_c, color='#319795', alpha=0.1)

plot_base(axs[3], "Esfera: Ritter Estándar")
axs[3].scatter([esfera_ritter.centro.x], [esfera_ritter.centro.y], color='red', marker='+', s=100, zorder=5)
c_ritter = plt.Circle((esfera_ritter.centro.x, esfera_ritter.centro.y), esfera_ritter.radio, color='#805ad5', fill=False, linewidth=2)
axs[3].add_patch(c_ritter)

plot_base(axs[4], "Esfera: Ritter + PCA (Eigen)")
axs[4].scatter([esfera_pca.centro.x], [esfera_pca.centro.y], color='red', marker='+', s=100, zorder=5)
c_pca = plt.Circle((esfera_pca.centro.x, esfera_pca.centro.y), esfera_pca.radio, color='#d69e2e', fill=False, linewidth=2)
axs[4].add_patch(c_pca)

plot_base(axs[5], "Esfera: Welzl")
axs[5].scatter([esfera_min.centro.x], [esfera_min.centro.y], color='red', marker='+', s=100, zorder=5)
c_welzl = plt.Circle((esfera_min.centro.x, esfera_min.centro.y), esfera_min.radio, color='#d69e2e', fill=False, linewidth=2)
axs[5].add_patch(c_welzl)

plot_base(axs[6], "OBB: Área Mínima")
axs[6].scatter([obb_min.c.x], [obb_min.c.y], color='red', marker='+', s=100, zorder=5)
v_obb = obb_min.generar_vertices()
x_obb = [p.x for p in v_obb] + [v_obb[0].x]
y_obb = [p.y for p in v_obb] + [v_obb[0].y]
axs[6].plot(x_obb, y_obb, color='#e53e3e', linewidth=2)
axs[6].fill(x_obb, y_obb, color='#e53e3e', alpha=0.1)

axs[7].axis('off')

plt.tight_layout()
plt.show()

print(f"Esfera Ritter -> Centro: {esfera_ritter.centro}, Radio: {esfera_ritter.radio:.3f}")
print(f"Esfera PCA    -> Centro: {esfera_pca.centro}, Radio: {esfera_pca.radio:.3f}")
print(f"Esfera Welzl  -> Centro: {esfera_min.centro}, Radio: {esfera_min.radio:.3f}")
print(f"OBB           -> Centro: {obb_min.c}, Ejes: {obb_min.u}, Radios: {obb_min.e}")
