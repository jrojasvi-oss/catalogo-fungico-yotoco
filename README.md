# Catálogo fúngico de la Reserva Forestal Bosque de Yotoco

Catálogo digital y libre de los hongos de la Reserva Forestal Bosque de Yotoco (Valle del Cauca, Colombia), con fichas, fotos de campo y modelos 3D que se giran en el navegador.

**Ver el catálogo:** https://jrojasvi-oss.github.io/catalogo-fungico-yotoco/

Nace de la salida de campo del 20 de octubre de 2026 de la asignatura Hongos y Oomicetos (Universidad Nacional de Colombia, Sede Palmira), con los docentes Carlos Alberto Huertas Davey y Eyder Daniel Gómez López.

## Contenido

| Carpeta | Qué tiene |
| --- | --- |
| `index.html` | La página del catálogo |
| `datos/fichas.json` | Las fichas en formato de datos |
| `modelos/` | Modelos 3D (`.glb`) |
| `img/` | Fotos de campo y recortes |
| `pipeline/hongo3d.py` | Programa que convierte un recorte en modelo 3D |
| `vendor/` | Visor 3D *model-viewer* (Google, Apache 2.0) |

## Cómo se hace un modelo

1. Recortar el hongo de la foto (se usó SAM, *Segment Anything*, vía `rembg`), guardando un PNG con fondo transparente.
2. `pip install trimesh pillow scipy numpy`
3. `python pipeline/hongo3d.py recorte.png modelo.glb`

El método supone simetría radial: la cara superior del píleo se toma de la foto y se endereza a un disco; el estípite se gira sobre su eje a partir de su ancho en la foto. Sirve para visualizar, no para medir. Para modelos fieles se recomienda fotogrametría (40 a 80 fotos alrededor del hongo).

## Fichas

| Código | Género | Sustrato | Estado |
| --- | --- | --- | --- |
| CF-001 | *Leucoagaricus* (prob.) | Hojarasca | Pendiente revisión docente |

Las identificaciones son tentativas, hechas a partir de fotografía.

## Licencia

Fotos, fichas y modelos: CC BY 4.0. Código: MIT. Autor: Juan David Rojas Villafañe, Ingeniería Agronómica, UNAL Palmira.
