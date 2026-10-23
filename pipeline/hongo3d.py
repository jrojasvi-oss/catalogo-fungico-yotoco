"""Foto recortada de un hongo con píleo y estípite -> modelo 3D (.glb).

Método (reconstrucción paramétrica a partir de una sola foto):
1. Píleo: la cara superior visible en la foto es una elipse (el círculo del sombrero
   visto en perspectiva). Se ajusta esa elipse y se "endereza" a un disco; ese disco
   es la textura de la cara superior del modelo.
2. Estípite y anillo: se mide el ancho del pie fila por fila en la foto y se gira
   alrededor de su eje (superficie de revolución); el color sale de la misma foto.
3. Cara inferior (láminas): cono entre el borde del píleo y el ápice del pie, con
   el color de la franja inferior visible del sombrero.

Supone simetría radial. Sirve para visualizar y para el catálogo; no reemplaza
la fotogrametría (40-80 fotos) cuando se necesitan medidas reales.

Uso: python hongo3d.py recorte.png modelo.glb
"""
import sys
import numpy as np
import trimesh
from PIL import Image
from scipy import ndimage as nd

SEG = 160  # divisiones angulares


def muestrear(img, x, y, cx=None, cy=None):
    h, w = img.shape[:2]
    x = np.asarray(x, float).copy(); y = np.asarray(y, float).copy()
    for _ in range(30):
        xi = np.clip(np.round(x).astype(int), 0, w - 1)
        yi = np.clip(np.round(y).astype(int), 0, h - 1)
        malo = img[yi, xi, 3] < 200
        if cx is None or not malo.any():
            break
        x[malo] = cx + (x[malo] - cx) * 0.93
        y[malo] = cy + (y[malo] - cy) * 0.93
    return img[yi, xi, :3]


def analizar(rgba):
    alpha = rgba[:, :, 3] > 127
    filas = np.where(alpha.any(1))[0]
    ancho = np.array([np.ptp(np.where(alpha[y])[0]) if alpha[y].any() else 0 for y in range(alpha.shape[0])])
    wmax = ancho.max()
    y_wmax = int(np.argmax(ancho))
    # fin del píleo: primera fila bajo el ancho máximo donde el ancho cae al 35 %
    y_cap_fin = next(y for y in range(y_wmax, filas.max()) if ancho[y] < 0.35 * wmax)
    cap = alpha.copy(); cap[y_cap_fin:] = False
    # elipse de la cara superior: momentos de la región del píleo por encima del ancho máximo,
    # reflejada para completar la elipse
    ys, xs = np.where(cap)
    cx = (xs.min() + xs.max()) / 2
    a = (xs.max() - xs.min()) / 2
    y_top = ys.min()
    # semieje vertical: la cara superior va del borde superior hasta la fila de ancho máximo,
    # que es aprox. el centro de la elipse
    b = max(y_wmax - y_top, 0.25 * a)
    cy = y_top + b
    # estípite
    stip = alpha.copy(); stip[:y_cap_fin] = False
    ys2 = np.where(stip.any(1))[0]
    perfil = []
    for y in ys2:
        xx = np.where(stip[y])[0]
        perfil.append((y, (xx.min() + xx.max()) / 2, (xx.max() - xx.min()) / 2))
    perfil = np.array(perfil)
    perfil[:, 2] = nd.gaussian_filter1d(perfil[:, 2], 2)
    eje = np.median(perfil[:, 1])
    return dict(cx=cx, cy=cy, a=a, b=b, y_top=y_top, y_cap_fin=y_cap_fin, perfil=perfil, eje=eje)


def construir(ruta, salida):
    rgba = np.array(Image.open(ruta).convert('RGBA'))
    g = analizar(rgba)
    a, b, cx, cy = g['a'], g['b'], g['cx'], g['cy']
    perfil = g['perfil']
    esc = 1.0 / a  # radio del píleo = 1
    th = np.linspace(0, 2 * np.pi, SEG, endpoint=False)

    V, C, F = [], [], []

    def anillo(radio, altura, cols):
        base = len(V)
        for t, col in zip(th, cols):
            V.append([radio * np.cos(t), altura, radio * np.sin(t)])
            C.append(col)
        return base

    def unir(i0, i1, invertir=False):
        for j in range(SEG):
            p, q = i0 + j, i0 + (j + 1) % SEG
            r, s = i1 + j, i1 + (j + 1) % SEG
            if invertir:
                F.extend([[p, q, r], [q, s, r]])
            else:
                F.extend([[p, r, q], [q, r, s]])

    # alturas del modelo (unidades: radio del píleo = 1)
    y_ap = (g['y_cap_fin'] - g['y_top']) * esc * 0.35   # grosor visual del píleo
    largo_pie = (perfil[-1, 0] - perfil[0, 0]) * esc
    h_pie_top = largo_pie                                # el pie va de 0 a h_pie_top
    h_borde = h_pie_top + 0.12
    depresion = 0.12                                     # centro del píleo hundido

    # --- cara superior del píleo: anillos de r=1 (borde) a r=0 (centro) ---
    n_r = 40
    idx_sup = []
    for k in range(n_r + 1):
        f = 1 - k / n_r
        altura = h_borde + 0.32 * (1 - f ** 2) - depresion * (1 - f) ** 3 - 0.06 * f ** 6
        cols = muestrear(rgba, cx + a * f * np.cos(th), cy - b * f * np.sin(th), cx, cy)
        idx_sup.append(anillo(f, altura, cols))
    for k in range(n_r):
        unir(idx_sup[k], idx_sup[k + 1])

    # --- cara inferior: del borde al ápice del pie ---
    r_pie_top = perfil[0, 2] * esc
    # color de las láminas: la franja inferior visible del píleo (los tonos más claros)
    banda = rgba[int(cy + 0.55 * b):g['y_cap_fin'], int(cx - 0.6 * a):int(cx + 0.6 * a)]
    banda = banda[banda[:, :, 3] > 200][:, :3].astype(float)
    lum = banda.mean(1)
    base_inf = np.median(banda[lum >= np.percentile(lum, 60)], axis=0)
    rayas = 0.86 + 0.14 * (0.5 + 0.5 * np.cos(th * 90))   # sugerencia de láminas radiales
    col_inf = np.clip(base_inf[None, :] * rayas[:, None], 0, 255).astype(np.uint8)
    n_inf = 14
    idx_inf = [idx_sup[0]]
    for k in range(1, n_inf + 1):
        f = 1 - k / n_inf
        radio = r_pie_top + (1 - r_pie_top) * f
        altura = h_borde - 0.02 - (1 - f) * 0.10
        idx_inf.append(anillo(radio, altura, col_inf))
    for k in range(n_inf):
        unir(idx_inf[k], idx_inf[k + 1], invertir=True)

    # --- estípite (superficie de revolución desde la foto) ---
    idx_pie = []
    for (y, cxx, r) in perfil[::2]:
        altura = h_pie_top - (y - perfil[0, 0]) * esc
        cols = muestrear(rgba, cxx + r * np.cos(th) * 0.9, np.full(SEG, y))
        idx_pie.append(anillo(r * esc, altura, cols))
    unir(idx_inf[-1], idx_pie[0], invertir=True)
    for k in range(len(idx_pie) - 1):
        unir(idx_pie[k], idx_pie[k + 1], invertir=True)
    # tapa de la base
    c0 = len(V); V.append([0, h_pie_top - (perfil[-1, 0] - perfil[0, 0]) * esc, 0]); C.append(C[idx_pie[-1]])
    last = idx_pie[-1]
    for j in range(SEG):
        F.append([last + j, last + (j + 1) % SEG, c0])

    V = np.array(V, float)
    V[:, 1] -= V[:, 1].min()
    cols = np.c_[np.array(C, dtype=np.uint8), np.full(len(C), 255, dtype=np.uint8)]
    m = trimesh.Trimesh(V, np.array(F), process=False)
    m.visual = trimesh.visual.ColorVisuals(m, vertex_colors=cols)
    m.export(salida)
    return m


if __name__ == '__main__':
    m = construir(sys.argv[1], sys.argv[2])
    print(sys.argv[2], len(m.vertices), 'vértices', len(m.faces), 'caras', 'estanco' if m.is_watertight else '')
