import Foundation
import SwiftData

/// Rutina de tríceps tomada del reel. Los pasos y errores se contrastaron con fuentes
/// públicas (Fitbod, StrengthLog, Muscle & Strength, Built With Science).
/// Series, repeticiones y descansos son valores sugeridos (3–4 × 8–12, 60–90 s), no vienen del reel.
enum DatosIniciales {
    static func sembrar(en contexto: ModelContext) {
        let existentes = (try? contexto.fetchCount(FetchDescriptor<Rutina>())) ?? 0
        guard existentes == 0 else { return }

        let barraRecta = Ejercicio(
            nombre: "Jalón de tríceps con barra recta",
            equipo: "Polea alta, barra recta",
            enfasis: "Las tres cabezas del tríceps, con énfasis en la lateral",
            pasos: [
                "Agarre por encima (palmas hacia abajo), pies al ancho de hombros y rodillas ligeramente flexionadas.",
                "Codos pegados a los costados y antebrazos paralelos al suelo al empezar.",
                "Extiende solo los codos hasta estirar los brazos, sin bloquearlos.",
                "Sube la barra despacio manteniendo la tensión en el tríceps."
            ],
            errores: [
                "Demasiado peso: el cuerpo se balancea y trabajan los hombros.",
                "Inclinarte hacia delante o arquear la espalda (si te inclinas, hazlo desde la cadera)."
            ])

        let acostado = Ejercicio(
            nombre: "Extensión de tríceps acostado con barra",
            equipo: "Banco plano, barra (la barra Z cuida muñecas y codos)",
            enfasis: "Tríceps completo, con buen estiramiento al bajar",
            pasos: [
                "Acostado en el banco, sostén la barra con los brazos extendidos sobre el pecho.",
                "Mantén los codos apuntando al frente, sin abrirlos.",
                "Baja la barra despacio hasta unos 2–3 cm de la frente.",
                "Extiende los codos para subir sin bloquearlos arriba."
            ],
            errores: [
                "Abrir los codos hacia los lados.",
                "Bloquear los codos arriba: se pierde tensión en el tríceps.",
                "Llevar los codos demasiado atrás: entran los dorsales."
            ])

        let sobreCabeza = Ejercicio(
            nombre: "Extensión de tríceps sobre la cabeza con cuerda",
            equipo: "Polea, cuerda",
            enfasis: "Cabeza larga (la que cruza el hombro), por el estiramiento",
            pasos: [
                "De espaldas a la polea, sostén la cuerda con ambas manos detrás de la cabeza.",
                "Codos hacia delante y cerca de la cabeza; el tronco estable.",
                "Extiende los codos hasta estirar los brazos por encima de la cabeza.",
                "Vuelve controlando el estiramiento."
            ],
            errores: [
                "Mover los codos hacia afuera o hacia atrás.",
                "Impulsarte con el tronco en lugar de usar el tríceps."
            ])

        let unaMano = Ejercicio(
            nombre: "Jalón de tríceps a una mano",
            equipo: "Polea alta, agarre individual",
            enfasis: "Tríceps, con control de cada brazo por separado",
            pasos: [
                "Agarra la polea con una mano, el codo pegado al costado.",
                "Extiende el codo hacia abajo sin mover el hombro.",
                "Mantén la posición final y sube controlando unos 2 segundos."
            ],
            errores: [
                "Separar el codo del cuerpo.",
                "Soltar la polea sin control al subir."
            ])

        let rutina = Rutina(
            nombre: "Tríceps",
            detalle: "Cuatro ejercicios: jalón, extensión acostado, extensión sobre la cabeza y jalón a una mano.")
        contexto.insert(rutina)

        let planes: [(Ejercicio, Int, Int, Int, Int)] = [
            (barraRecta, 3, 8, 12, 90),
            (acostado, 3, 8, 12, 90),
            (sobreCabeza, 3, 10, 12, 60),
            (unaMano, 3, 10, 12, 60)
        ]
        for (indice, datos) in planes.enumerated() {
            contexto.insert(datos.0)
            let plan = EjercicioPlan(orden: indice, series: datos.1, repsMin: datos.2,
                                     repsMax: datos.3, descansoSeg: datos.4, ejercicio: datos.0)
            contexto.insert(plan)
            plan.rutina = rutina
        }
        try? contexto.save()
    }
}
