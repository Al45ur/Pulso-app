# Pulso — app de gym para iPhone

App nativa (SwiftUI + SwiftData + App Intents, iOS 17 o superior) basada en un reel de tríceps de @modopro_app.

## Abrirla en Xcode (en un Mac)

```bash
brew install xcodegen
cd gym
xcodegen            # genera Pulso.xcodeproj desde project.yml
open Pulso.xcodeproj
```

En Xcode: elige el target **Pulso** → *Signing & Capabilities* → selecciona tu *Team*, y ejecuta en tu iPhone o simulador.
Para correr las pruebas: `Cmd+U`.

## Qué incluye

- **Rutina de tríceps** con 4 ejercicios (pasos y errores comunes contrastados con fuentes públicas).
- **Entrenamiento en curso**: registra peso y repeticiones por serie, con temporizador de descanso.
- **Historial** de entrenamientos con volumen total.
- **Siri / Atajos**:
  - «Inicia Tríceps en Pulso»
  - «Registra una serie en Pulso» (Siri pregunta las repeticiones y los kilos)
  - «Siguiente ejercicio en Pulso»
  - «Termina el entrenamiento en Pulso»

## Notas

- Series, repeticiones y descansos son valores **sugeridos**; el reel no los indica.
- Las frases de Siri están en español: el idioma del iPhone y de Siri debe ser español.
- No se incluyen imágenes del reel (son de otro autor).
