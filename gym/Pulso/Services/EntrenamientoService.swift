import Foundation
import SwiftData

enum EntrenamientoError: Error, Equatable, CustomLocalizedStringResourceConvertible {
    case sinSesionActiva
    case sinEjercicio
    case valorInvalido
    case ultimoEjercicio
    case primerEjercicio
    case rutinaNoEncontrada

    var localizedStringResource: LocalizedStringResource {
        switch self {
        case .sinSesionActiva: return "No hay un entrenamiento en curso. Inicia una rutina primero."
        case .sinEjercicio: return "La rutina no tiene un ejercicio actual."
        case .valorInvalido: return "Las repeticiones deben estar entre 1 y 100, y el peso entre 0 y 500 kilos."
        case .ultimoEjercicio: return "Ya estás en el último ejercicio."
        case .primerEjercicio: return "Ya estás en el primer ejercicio."
        case .rutinaNoEncontrada: return "No encontré esa rutina."
        }
    }
}

struct ResumenSerie: Equatable {
    let ejercicio: String
    let numero: Int
    let seriesObjetivo: Int
    let descansoSeg: Int

    var completoEjercicio: Bool { numero >= seriesObjetivo }

    var mensaje: String {
        let base = "Serie \(numero) de \(seriesObjetivo) en \(ejercicio) registrada."
        return completoEjercicio ? base + " Ejercicio completado." : base + " Descansa \(descansoSeg) segundos."
    }
}

/// Lógica del entrenamiento. La usan las pantallas y los intents de Siri,
/// así ambos comparten las mismas reglas.
enum EntrenamientoService {
    static func sesionActiva(en contexto: ModelContext) -> Sesion? {
        var descriptor = FetchDescriptor<Sesion>(
            predicate: #Predicate<Sesion> { $0.fin == nil },
            sortBy: [SortDescriptor(\.inicio, order: .reverse)])
        descriptor.fetchLimit = 1
        return try? contexto.fetch(descriptor).first
    }

    static func requerirSesionActiva(en contexto: ModelContext) throws -> Sesion {
        guard let sesion = sesionActiva(en: contexto) else { throw EntrenamientoError.sinSesionActiva }
        return sesion
    }

    /// Inicia un entrenamiento. Si ya hay uno de la misma rutina lo devuelve;
    /// si es de otra rutina, lo cierra y empieza el nuevo.
    @discardableResult
    static func iniciar(_ rutina: Rutina, en contexto: ModelContext) -> Sesion {
        if let activa = sesionActiva(en: contexto) {
            if activa.rutina?.id == rutina.id { return activa }
            terminar(activa, en: contexto)
        }
        let sesion = Sesion()
        contexto.insert(sesion)
        sesion.rutina = rutina
        try? contexto.save()
        return sesion
    }

    @discardableResult
    static func registrarSerie(en sesion: Sesion, contexto: ModelContext,
                               repeticiones: Int, pesoKg: Double,
                               fecha: Date = .now) throws -> ResumenSerie {
        guard (1...100).contains(repeticiones), (0...500).contains(pesoKg) else {
            throw EntrenamientoError.valorInvalido
        }
        guard let plan = sesion.ejercicioActual else { throw EntrenamientoError.sinEjercicio }

        let indice = sesion.indiceEjercicio
        let numero = sesion.seriesRegistradas(enEjercicio: indice).count + 1
        let serie = SerieRegistrada(indiceEjercicio: indice, ejercicioNombre: plan.nombre,
                                    numero: numero, repeticiones: repeticiones,
                                    pesoKg: pesoKg, fecha: fecha)
        contexto.insert(serie)
        serie.sesion = sesion
        try contexto.save()
        return ResumenSerie(ejercicio: plan.nombre, numero: numero,
                            seriesObjetivo: plan.series, descansoSeg: plan.descansoSeg)
    }

    @discardableResult
    static func siguienteEjercicio(en sesion: Sesion, contexto: ModelContext) throws -> EjercicioPlan {
        guard sesion.indiceEjercicio + 1 < sesion.planOrdenado.count else {
            throw EntrenamientoError.ultimoEjercicio
        }
        sesion.indiceEjercicio += 1
        try contexto.save()
        guard let plan = sesion.ejercicioActual else { throw EntrenamientoError.sinEjercicio }
        return plan
    }

    @discardableResult
    static func ejercicioAnterior(en sesion: Sesion, contexto: ModelContext) throws -> EjercicioPlan {
        guard sesion.indiceEjercicio > 0 else { throw EntrenamientoError.primerEjercicio }
        sesion.indiceEjercicio -= 1
        try contexto.save()
        guard let plan = sesion.ejercicioActual else { throw EntrenamientoError.sinEjercicio }
        return plan
    }

    /// Cierra el entrenamiento. No se borra aunque no tenga series: la pantalla de
    /// entrenamiento aún puede estar leyendo el modelo mientras se cierra, y leer un
    /// modelo borrado es un error en SwiftData. El historial oculta las sesiones vacías.
    static func terminar(_ sesion: Sesion, en contexto: ModelContext) {
        sesion.fin = .now
        try? contexto.save()
    }
}
