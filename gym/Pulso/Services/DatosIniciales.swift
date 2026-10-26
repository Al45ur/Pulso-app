import Foundation
import SwiftData

/// Crea la rutina de tríceps del reel a partir del catálogo (ejercicios.json), de modo que los textos,
/// las series y las repeticiones tengan una sola fuente. Series, repeticiones y descansos son valores
/// sugeridos, no vienen del reel.
enum DatosIniciales {
    static let categoriaDelReel = "Tríceps"

    static func sembrar(en contexto: ModelContext, catalogo: CatalogoEjercicios = .compartido) {
        let existentes = (try? contexto.fetchCount(FetchDescriptor<Rutina>())) ?? 0
        guard existentes == 0 else { return }

        let fichas = catalogo.fichas.filter { $0.categoria == categoriaDelReel }
        guard !fichas.isEmpty else { return }

        let rutina = Rutina(
            nombre: "Tríceps",
            detalle: "Cuatro ejercicios: jalón, extensión acostado, extensión sobre la cabeza y jalón a una mano.")
        contexto.insert(rutina)

        for (indice, ficha) in fichas.enumerated() {
            let ejercicio = RutinaUsuarioService.ejercicio(para: ficha, en: contexto)
            let plan = EjercicioPlan(orden: indice, series: ficha.series, repsMin: ficha.repsMin,
                                     repsMax: ficha.repsMax, descansoSeg: ficha.descansoSeg, ejercicio: ejercicio)
            contexto.insert(plan)
            plan.rutina = rutina
        }
        try? contexto.save()
    }
}
