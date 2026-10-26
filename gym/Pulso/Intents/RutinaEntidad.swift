import AppIntents
import SwiftData

/// Permite a Siri y a Atajos referirse a una rutina por su nombre.
struct RutinaEntidad: AppEntity {
    static let typeDisplayRepresentation: TypeDisplayRepresentation = "Rutina"
    static let defaultQuery = ConsultaRutinas()

    var id: UUID
    var nombre: String

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(nombre)")
    }
}

struct ConsultaRutinas: EntityQuery {
    @MainActor
    func entities(for identifiers: [UUID]) async throws -> [RutinaEntidad] {
        try todas().filter { identifiers.contains($0.id) }
    }

    @MainActor
    func suggestedEntities() async throws -> [RutinaEntidad] {
        try todas()
    }

    @MainActor
    private func todas() throws -> [RutinaEntidad] {
        let descriptor = FetchDescriptor<Rutina>(sortBy: [SortDescriptor(\.nombre)])
        return try Persistencia.contenedor.mainContext.fetch(descriptor)
            .map { RutinaEntidad(id: $0.id, nombre: $0.nombre) }
    }
}
