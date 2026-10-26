import Foundation
import SwiftData

/// «Mi rutina»: la rutina que arma la persona añadiendo ejercicios del catálogo.
enum RutinaUsuarioService {
    static let nombre = "Mi rutina"

    static func buscarRutina(en contexto: ModelContext) -> Rutina? {
        let buscado = nombre
        var descriptor = FetchDescriptor<Rutina>(predicate: #Predicate<Rutina> { $0.nombre == buscado })
        descriptor.fetchLimit = 1
        return try? contexto.fetch(descriptor).first
    }

    /// Devuelve el `Ejercicio` guardado para una ficha, o lo crea la primera vez.
    static func ejercicio(para ficha: FichaEjercicio, en contexto: ModelContext) -> Ejercicio {
        let id = ficha.id
        var descriptor = FetchDescriptor<Ejercicio>(predicate: #Predicate<Ejercicio> { $0.fichaID == id })
        descriptor.fetchLimit = 1
        if let existente = try? contexto.fetch(descriptor).first { return existente }
        let nuevo = Ejercicio(fichaID: ficha.id, nombre: ficha.nombre, equipo: ficha.equipo,
                              enfasis: ficha.etiquetaMusculos, pasos: ficha.pasos, errores: ficha.errores)
        contexto.insert(nuevo)
        return nuevo
    }

    private static func plan(de ficha: FichaEjercicio, en miRutina: Rutina) -> EjercicioPlan? {
        miRutina.plan.first { $0.ejercicio?.fichaID == ficha.id }
    }

    static func contiene(_ ficha: FichaEjercicio, en contexto: ModelContext) -> Bool {
        guard let miRutina = buscarRutina(en: contexto) else { return false }
        return plan(de: ficha, en: miRutina) != nil
    }

    /// Añade el ejercicio con la configuración elegida; si ya estaba, solo actualiza series, repeticiones y descanso.
    @discardableResult
    static func agregar(_ ficha: FichaEjercicio, config: ConfigEjercicio, en contexto: ModelContext) -> EjercicioPlan {
        let miRutina: Rutina
        if let existente = buscarRutina(en: contexto) {
            miRutina = existente
        } else {
            miRutina = Rutina(nombre: nombre, detalle: "Los ejercicios que añadiste desde el catálogo.")
            contexto.insert(miRutina)
        }

        if let existente = plan(de: ficha, en: miRutina) {
            existente.series = config.series
            existente.repsMin = config.repsMin
            existente.repsMax = config.repsMax
            existente.descansoSeg = config.descansoSeg
            try? contexto.save()
            return existente
        }

        let ejercicio = ejercicio(para: ficha, en: contexto)
        let orden = (miRutina.plan.map(\.orden).max() ?? -1) + 1
        let nuevo = EjercicioPlan(orden: orden, series: config.series, repsMin: config.repsMin,
                                  repsMax: config.repsMax, descansoSeg: config.descansoSeg, ejercicio: ejercicio)
        contexto.insert(nuevo)
        nuevo.rutina = miRutina
        try? contexto.save()
        return nuevo
    }

    /// Quita el ejercicio de la rutina y vuelve a numerar los que quedan.
    static func quitar(_ ficha: FichaEjercicio, en contexto: ModelContext) {
        guard let miRutina = buscarRutina(en: contexto), let existente = plan(de: ficha, en: miRutina) else { return }
        let restantes = miRutina.planOrdenado.filter { $0 !== existente }
        contexto.delete(existente)
        for (indice, restante) in restantes.enumerated() { restante.orden = indice }
        try? contexto.save()
    }
}
