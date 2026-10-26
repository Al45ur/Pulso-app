# Pulso — app de gym para iPhone

App nativa (SwiftUI + SwiftData + SceneKit + App Intents, iOS 17 o superior). Empezó con la rutina de tríceps de un reel
y ahora incluye un catálogo de ejercicios con modelo humano 3D articulado.

## Abrirla en Xcode (en un Mac)

```bash
brew install xcodegen
cd gym
xcodegen            # genera Pulso.xcodeproj desde project.yml
open Pulso.xcodeproj
```

En Xcode: target **Pulso** → *Signing & Capabilities* → elige tu *Team* y ejecuta. Pruebas: `Cmd+U`.

## Usarla sin Mac: versión web

`gym/web/` genera una página (`python3 gym/web/construir.py`) con el mismo personaje y los mismos ejercicios: catálogo,
ficha 3D, **mapa del cuerpo** (toca un músculo y ves sus ejercicios), rutinas, entrenamiento con registro de series y
descanso, historial y **evolución fotográfica**. Publicada como Artifact de claude.ai,
guarda los datos en la cuenta de quien la usa (`db`, subárbol privado) o, sin sesión, en el navegador. No incluye Siri.

## Pestañas y pantallas

| Pestaña | Contenido |
|---|---|
| **Ejercicios** | 1 Catálogo (búsqueda y filtros) → 2 Ficha → 3 Animación 3D · 4 Anatomía 3D · 5 Técnica · 6 Mapa de músculos · 7 Guía paso a paso · 8 Resumen |
| **Mapa** *(solo web)* | Muñeco 3D (frente/perfil/espalda): al tocar un músculo se listan los ejercicios donde es principal o secundario; marca los músculos sin ejercicio en el catálogo |
| **Rutinas** | «Tríceps» (la del reel) y «Mi rutina» (los ejercicios que añades desde el resumen) |
| **Historial** | Entrenamientos terminados con su volumen |
| **Progreso** *(solo web)* | Fotos de frente, perfil y espalda por fecha, comparación de dos fechas, guía para repetir la pose, borrado y exportación. Privadas; sin reconocimiento corporal por IA |

El ejercicio elegido se mantiene entre pantallas (se navega por identificador de ficha).

## Dónde está cada cosa

- `Pulso/Resources/ejercicios.json`: **única fuente** de cada ejercicio: músculos principales y secundarios, pasos, errores,
  seguridad, series/repeticiones/descanso sugeridos, accesorios (banco, barra, cable), cámara y las poses de cada fase.
  Cada ficha lleva `pendienteValidacion` con lo que aún no está confirmado; la app lo muestra.
- `Pulso/Scene3D/Maniqui.swift`: esqueleto articulado (cada articulación es un nodo que se gira). Cuelga de él el
  personaje cargado de `Resources/maniqui.json` + `maniqui.bin` (piel, short, tenis, ojos y una capa por músculo). Tiene dos
  aspectos: «piel» (vestido; solo se ven los músculos marcados y el short se aclara si el músculo queda debajo) y «anatomía».
  Si esos archivos faltan, usa un maniquí procedural de respaldo.
- `tools/generar_maniqui.py`: genera el personaje (secciones elípticas con splines para la piel; cada músculo se recorta
  de la piel y se eleva con un perfil suave). `tools/vista_previa_maniqui.py` lo dibuja en cada pose sin Xcode.
- `Pulso/Scene3D/EscenaEntrenamiento.swift`: luces, cámara y accesorios que siguen a las manos.
- `Pulso/Models/Pose.swift`: poses, interpolación y la línea de tiempo (cada fase pasa a la siguiente y la última vuelve a la primera).
- `Pulso/Views/Ejercicios/`: las ocho pantallas.

El deltoides tiene tres cabezas con malla propia (`deltoides_anterior`, `deltoides_lateral`, `deltoides_posterior`).
La animación y el resaltado muscular salen de la **misma ficha**; no son dos elementos independientes.
El resaltado marca los músculos asociados al ejercicio; **no mide activación real**.

## Cómo añadir un ejercicio

1. Añade una ficha en `ejercicios.json` (copia una existente). Los músculos deben ser ids de `Musculo`.
2. Define 2 o más fases con sus poses. Ángulos en grados: `[flexión, abducción, rotación]` (la rotación, opcional, solo la usa el hombro:
   giro del brazo sobre su eje, positivo = externa); `raiz.pos` = posición de la pelvis.
3. Comprueba las poses sin Xcode: `python3 gym/tools/verificar_poses.py /ruta/salida` (requiere Pillow).
   Dibuja cada fase de perfil y de frente e informa si los pies tocan el suelo.
4. La app valida el JSON al cargar (`CatalogoEjercicios.validar`) y muestra el error en pantalla si algo no cuadra.

`tools/verificar_poses.py` y `Maniqui.swift` usan las mismas medidas y la misma cinemática. La prueba
`testLaCinematicaDeSceneKitCoincideConElVerificador` falla si dejan de coincidir.

## Siri / Atajos

- «Inicia Tríceps en Pulso» · «Inicia Mi rutina en Pulso»
- «Registra una serie en Pulso» (pregunta repeticiones y kilos)
- «Siguiente ejercicio en Pulso» · «Termina el entrenamiento en Pulso»

Las frases están en español: el iPhone y Siri deben estar en español.

## Pendiente (para completar la visión del diseño)

1. **Modelo humano de estudio.** El personaje es un maniquí atlético generado por código: segmentos rígidos con
   articulaciones redondeadas, cara simplificada, manos sin dedos ni deformación de la piel al doblar; no es fotorrealista. Para un nivel de estudio
   hace falta un personaje con esqueleto (USDZ) y malla muscular separada, con licencia comercial. `Maniqui` está aislado:
   basta con otra clase con los mismos métodos (`aplicar(_:)`, `resaltar(...)`, `manoI`, `manoD`).
2. **Más ejercicios.** Hay 7 (4 de tríceps, 1 de piernas, 2 de hombros). Los filtros muestran solo categorías con ejercicios.
3. **Validación de contenido** por un entrenador: ver `pendienteValidacion` de cada ficha.
4. **Mapa del cuerpo y Progreso en la app nativa.** Solo existen en la web (ahí se pueden probar sin Mac). En Swift ya están
   el aspecto «piel/anatomía» y `CatalogoEjercicios.ejercicios(para:)`; falta la interfaz SwiftUI.
5. **Pestañas Inicio y Perfil** del diseño de referencia: no se crearon porque no tienen función todavía.
6. **SceneKit** está marcado como obsoleto desde iOS 26 (sigue funcionando). Si se migra a RealityKit, solo cambian
   `Scene3D/` y `VistaEscena`.
7. No se incluyen imágenes del reel ni del diseño de referencia (son de terceros).
