import Foundation

struct CatalogoEjercicios {
    let fichas: [FichaEjercicio]
    /// Si no es nil, el catálogo no se pudo cargar y las pantallas muestran este mensaje.
    let error: String?

    static let compartido = CatalogoEjercicios.cargar()

    private struct Raiz: Decodable { let ejercicios: [FichaEjercicio] }

    private static let tiposDeProp: Set<String> = ["cable", "barra", "banco", "mancuernas", "manija"]
    private static let destinosDeCable: Set<String> = ["centro", "manoI", "manoD"]

    static func cargar(bundle: Bundle = .main) -> CatalogoEjercicios {
        guard let url = bundle.url(forResource: "ejercicios", withExtension: "json") else {
            return CatalogoEjercicios(fichas: [], error: "No se encontró ejercicios.json dentro de la app.")
        }
        do {
            let raiz = try JSONDecoder().decode(Raiz.self, from: Data(contentsOf: url))
            try validar(raiz.ejercicios)
            return CatalogoEjercicios(fichas: raiz.ejercicios, error: nil)
        } catch {
            return CatalogoEjercicios(fichas: [], error: "No se pudo leer el catálogo de ejercicios: \(error)")
        }
    }

    /// Detecta datos incompletos o incoherentes al cargar, en lugar de fallar al dibujar.
    static func validar(_ fichas: [FichaEjercicio]) throws {
        var vistos = Set<String>()
        for ficha in fichas {
            func fallo(_ motivo: String) -> NSError {
                NSError(domain: "Catalogo", code: 1,
                        userInfo: [NSLocalizedDescriptionKey: "\(ficha.id): \(motivo)"])
            }
            guard vistos.insert(ficha.id).inserted else { throw fallo("identificador repetido") }
            guard !ficha.musculosPrincipales.isEmpty else { throw fallo("sin músculos principales") }
            guard ficha.fases.count >= 2 else { throw fallo("necesita al menos 2 fases") }
            guard ficha.fases.indices.contains(ficha.faseMiniatura) else { throw fallo("faseMiniatura fuera de rango") }
            guard (1...10).contains(ficha.series), ficha.repsMin >= 1, ficha.repsMin <= ficha.repsMax,
                  ficha.descansoSeg >= 0 else { throw fallo("series, repeticiones o descanso inválidos") }
            guard Set(ficha.musculosPrincipales).isDisjoint(with: ficha.musculosSecundarios) else {
                throw fallo("un músculo no puede ser principal y secundario")
            }
            for prop in ficha.props {
                guard tiposDeProp.contains(prop.tipo) else { throw fallo("prop desconocido: \(prop.tipo)") }
                if prop.tipo == "cable" {
                    guard prop.ancla?.count == 3 else { throw fallo("el cable necesita un ancla de 3 valores") }
                    guard destinosDeCable.contains(prop.hacia ?? "centro") else { throw fallo("destino de cable inválido") }
                }
                if prop.tipo == "manija" {
                    guard prop.mano == "I" || prop.mano == "D" else { throw fallo("la manija necesita mano I o D") }
                }
            }
        }
    }

    func ficha(id: String) -> FichaEjercicio? {
        fichas.first { $0.id == id }
    }

    /// Categorías en el orden en que aparecen en el catálogo.
    var categorias: [String] {
        var vistas: [String] = []
        for ficha in fichas where !vistas.contains(ficha.categoria) { vistas.append(ficha.categoria) }
        return vistas
    }
}
