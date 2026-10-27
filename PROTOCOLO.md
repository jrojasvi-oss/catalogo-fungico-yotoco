# Protocolo de digitalización de hongos

Cómo fotografiar, procesar y publicar un hongo en el catálogo fúngico de Yotoco. Está pensado para hacerse con un celular y herramientas gratuitas.

## 1. En campo: las fotos

1. **Sin tocarlo primero.** Una foto del hongo tal como está, con su entorno.
2. **Tres vistas.** Arriba (píleo), abajo (láminas o poros) y de perfil (pie, anillo, volva). La de perfil es la que se usa para el 3D.
3. **Escala.** Una regla o tarjeta de color junto al hongo en al menos una foto.
4. **Sustrato.** Una foto de dónde crece: suelo, madera, hojarasca u otro hongo.
5. **Fondo limpio para el perfil.** Si se puede, apartar ramas u hojas que tapen el pie, sin dañar el hongo.
6. **Para 3D fiel (fotogrametría).** 40 a 80 fotos dando la vuelta completa, a dos alturas, con luz pareja y sin flash directo. Apps: RealityScan, Polycam; en PC: Meshroom.

## 2. Datos de la ficha

| Campo | Ejemplo (CF-001) |
| --- | --- |
| Código | CF-001 |
| Determinación | *Leucoagaricus* sp. (probable), por fotografía |
| Taxonomía | Fungi › Basidiomycota › Agaricomycetes › Agaricales › Agaricaceae |
| Píleo, láminas, estípite | Forma, color, superficie, anillo, volva |
| Sustrato | Hojarasca |
| Localidad y coordenadas | Reserva Forestal Bosque de Yotoco; GPS y altitud |
| Fecha y colector | 20 oct 2026 · Juan David Rojas Villafañe |
| Caracteres no visuales | Olor, textura, látex, esporada |

Las fichas se guardan en `datos/fichas.json`.

## 3. En el computador: recorte y 3D

1. Instalar: `pip install "rembg[cpu]" trimesh pillow scipy numpy`
2. **Recorte con SAM.** Marcar puntos sobre el hongo (positivos) y sobre el fondo (negativos) y obtener la máscara con `rembg` usando el modelo `sam`. Si algo tapa el pie, unir los tramos y limpiar la máscara (quitar manchas sueltas y rellenar huecos).
3. Guardar el recorte como PNG con fondo transparente.
4. **Modelo 3D:** `python pipeline/hongo3d.py recorte.png modelos/CF-00X_genero.glb`
5. Revisar el modelo en el navegador y agregar la ficha y la foto al catálogo.

## 4. Límites del modelo de una sola foto

- Supone simetría radial; no reproduce lóbulos ni roturas.
- Las partes que no se ven (normalmente las láminas) se completan con su color.
- Sirve para ver forma y caracteres, no para medir. Para medidas, fotogrametría con escala.
- Funciona con hongos de píleo y estípite. Para poliporos, gelatinosos o cuerpos irregulares hace falta fotogrametría.

## 5. Publicar y compartir

- Fotos, fichas y modelos con licencia CC BY 4.0; código MIT.
- Toda identificación se marca como tentativa hasta que la revise un docente o especialista.
- Las correcciones se reciben como *issues* en GitHub.
