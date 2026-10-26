import Foundation
import SwiftData

/// Contenedor único compartido por la app y por los intents de Siri.
@MainActor
enum Persistencia {
    static let contenedor: ModelContainer = {
        let esquema = Schema([Ejercicio.self, EjercicioPlan.self, Rutina.self, Sesion.self, SerieRegistrada.self])
        do {
            let contenedor = try ModelContainer(for: esquema)
            DatosIniciales.sembrar(en: contenedor.mainContext)
            return contenedor
        } catch {
            fatalError("No se pudo crear la base de datos: \(error)")
        }
    }()
}
