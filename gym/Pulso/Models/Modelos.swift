import Foundation
import SwiftData

@Model
final class Ejercicio {
    @Attribute(.unique) var id: UUID
    var nombre: String
    var equipo: String
    var enfasis: String
    var pasos: [String]
    var errores: [String]

    init(nombre: String, equipo: String, enfasis: String, pasos: [String], errores: [String]) {
        self.id = UUID()
        self.nombre = nombre
        self.equipo = equipo
        self.enfasis = enfasis
        self.pasos = pasos
        self.errores = errores
    }
}

/// Un ejercicio dentro de una rutina, con su objetivo de series y repeticiones.
@Model
final class EjercicioPlan {
    var orden: Int
    var series: Int
    var repsMin: Int
    var repsMax: Int
    var descansoSeg: Int
    var ejercicio: Ejercicio?
    var rutina: Rutina?

    init(orden: Int, series: Int, repsMin: Int, repsMax: Int, descansoSeg: Int, ejercicio: Ejercicio) {
        self.orden = orden
        self.series = series
        self.repsMin = repsMin
        self.repsMax = repsMax
        self.descansoSeg = descansoSeg
        self.ejercicio = ejercicio
    }

    var nombre: String { ejercicio?.nombre ?? "Ejercicio" }

    var objetivo: String {
        repsMin == repsMax ? "\(series) × \(repsMin)" : "\(series) × \(repsMin)–\(repsMax)"
    }
}

@Model
final class Rutina {
    @Attribute(.unique) var id: UUID
    var nombre: String
    var detalle: String
    @Relationship(deleteRule: .cascade, inverse: \EjercicioPlan.rutina)
    var plan: [EjercicioPlan] = []

    init(nombre: String, detalle: String) {
        self.id = UUID()
        self.nombre = nombre
        self.detalle = detalle
    }

    var planOrdenado: [EjercicioPlan] { plan.sorted { $0.orden < $1.orden } }
}

/// Un entrenamiento en curso (`fin == nil`) o terminado.
@Model
final class Sesion {
    var inicio: Date
    var fin: Date?
    var indiceEjercicio: Int
    var rutina: Rutina?
    @Relationship(deleteRule: .cascade, inverse: \SerieRegistrada.sesion)
    var series: [SerieRegistrada] = []

    init(inicio: Date = .now) {
        self.inicio = inicio
        self.indiceEjercicio = 0
    }

    var planOrdenado: [EjercicioPlan] { rutina?.planOrdenado ?? [] }

    var ejercicioActual: EjercicioPlan? {
        let plan = planOrdenado
        return plan.indices.contains(indiceEjercicio) ? plan[indiceEjercicio] : nil
    }

    func seriesRegistradas(enEjercicio indice: Int) -> [SerieRegistrada] {
        series.filter { $0.indiceEjercicio == indice }.sorted { $0.numero < $1.numero }
    }

    var volumenKg: Double { series.reduce(0) { $0 + Double($1.repeticiones) * $1.pesoKg } }
}

@Model
final class SerieRegistrada {
    var indiceEjercicio: Int
    var ejercicioNombre: String
    var numero: Int
    var repeticiones: Int
    var pesoKg: Double
    var fecha: Date
    var sesion: Sesion?

    init(indiceEjercicio: Int, ejercicioNombre: String, numero: Int,
         repeticiones: Int, pesoKg: Double, fecha: Date = .now) {
        self.indiceEjercicio = indiceEjercicio
        self.ejercicioNombre = ejercicioNombre
        self.numero = numero
        self.repeticiones = repeticiones
        self.pesoKg = pesoKg
        self.fecha = fecha
    }
}
