import Foundation

struct PropDTO: Decodable, Hashable {
    let tipo: String
    let ancla: [Double]?
    let hacia: String?
    let mano: String?
    let alargue: Double?
    let discos: Bool?
}

struct CamaraDTO: Decodable, Hashable {
    let azimut: Double
    let altura: Double
    let distancia: Double
    let objetivoY: Double
}

struct Fase: Decodable {
    let nombre: String
    let descripcion: String
    let pose: Pose
}

/// Toda la información de un ejercicio, leída de ejercicios.json.
/// Es la única fuente para el catálogo, la animación, la anatomía y las rutinas.
struct FichaEjercicio: Decodable, Identifiable, Hashable {
    let id: String
    let nombre: String
    let categoria: String
    let equipo: String
    let musculosPrincipales: [Musculo]
    let musculosSecundarios: [Musculo]
    let descripcion: String
    let pasos: [String]
    let errores: [String]
    let seguridad: [String]
    let series: Int
    let repsMin: Int
    let repsMax: Int
    let descansoSeg: Int
    let props: [PropDTO]
    let camara: CamaraDTO
    let faseMiniatura: Int
    let fases: [Fase]
    let pendienteValidacion: [String]

    static func == (a: FichaEjercicio, b: FichaEjercicio) -> Bool { a.id == b.id }
    func hash(into hasher: inout Hasher) { hasher.combine(id) }

    var principales: Set<Musculo> { Set(musculosPrincipales) }
    var secundarios: Set<Musculo> { Set(musculosSecundarios) }

    func rol(de musculo: Musculo) -> RolMuscular {
        if principales.contains(musculo) { return .principal }
        if secundarios.contains(musculo) { return .secundario }
        return .ninguno
    }

    var etiquetaMusculos: String {
        musculosPrincipales.map(\.nombre).joined(separator: " · ")
    }

    var lineaTiempo: LineaTiempo { LineaTiempo(poses: fases.map(\.pose)) }

    var objetivoSugerido: String {
        repsMin == repsMax ? "\(series) × \(repsMin)" : "\(series) × \(repsMin)–\(repsMax)"
    }
}

/// Series, repeticiones y descanso que la persona decide para un ejercicio. Se guarda en el dispositivo.
struct ConfigEjercicio: Codable, Equatable {
    var series: Int
    var repsMin: Int
    var repsMax: Int
    var descansoSeg: Int

    static func sugerida(_ ficha: FichaEjercicio) -> ConfigEjercicio {
        ConfigEjercicio(series: ficha.series, repsMin: ficha.repsMin,
                        repsMax: ficha.repsMax, descansoSeg: ficha.descansoSeg)
    }

    var esValida: Bool {
        (1...10).contains(series) && (1...50).contains(repsMin)
            && repsMin <= repsMax && repsMax <= 50 && (0...600).contains(descansoSeg)
    }

    private static func clave(_ ficha: FichaEjercicio) -> String { "config.\(ficha.id)" }

    static func cargar(_ ficha: FichaEjercicio, defaults: UserDefaults = .standard) -> ConfigEjercicio {
        guard let datos = defaults.data(forKey: clave(ficha)),
              let guardada = try? JSONDecoder().decode(ConfigEjercicio.self, from: datos),
              guardada.esValida else { return sugerida(ficha) }
        return guardada
    }

    func guardar(_ ficha: FichaEjercicio, defaults: UserDefaults = .standard) {
        guard esValida, let datos = try? JSONEncoder().encode(self) else { return }
        defaults.set(datos, forKey: Self.clave(ficha))
    }
}
