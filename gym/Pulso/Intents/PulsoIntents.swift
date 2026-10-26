import AppIntents
import SwiftData

struct IniciarRutinaIntent: AppIntent {
    static let title: LocalizedStringResource = "Iniciar rutina"
    static let description = IntentDescription("Empieza un entrenamiento con la rutina que elijas.")
    static let openAppWhenRun = true

    @Parameter(title: "Rutina")
    var rutina: RutinaEntidad

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let contexto = Persistencia.contenedor.mainContext
        let id = rutina.id
        let descriptor = FetchDescriptor<Rutina>(predicate: #Predicate<Rutina> { $0.id == id })
        guard let encontrada = try contexto.fetch(descriptor).first else {
            throw EntrenamientoError.rutinaNoEncontrada
        }
        guard !encontrada.plan.isEmpty else { throw EntrenamientoError.rutinaVacia }
        let sesion = EntrenamientoService.iniciar(encontrada, en: contexto)
        let primero = sesion.ejercicioActual?.nombre ?? "tu primer ejercicio"
        let mensaje = "Rutina \(encontrada.nombre) iniciada. Empieza con \(primero)."
        return .result(dialog: "\(mensaje)")
    }
}

struct RegistrarSerieIntent: AppIntent {
    static let title: LocalizedStringResource = "Registrar serie"
    static let description = IntentDescription("Anota las repeticiones y el peso de la serie que acabas de hacer.")

    @Parameter(title: "Repeticiones", requestValueDialog: "¿Cuántas repeticiones hiciste?")
    var repeticiones: Int

    @Parameter(title: "Peso en kilos", requestValueDialog: "¿Con cuántos kilos?")
    var pesoKg: Double

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let contexto = Persistencia.contenedor.mainContext
        let sesion = try EntrenamientoService.requerirSesionActiva(en: contexto)
        let resumen = try EntrenamientoService.registrarSerie(
            en: sesion, contexto: contexto, repeticiones: repeticiones, pesoKg: pesoKg)
        let mensaje = resumen.mensaje
        return .result(dialog: "\(mensaje)")
    }
}

struct SiguienteEjercicioIntent: AppIntent {
    static let title: LocalizedStringResource = "Siguiente ejercicio"
    static let description = IntentDescription("Pasa al siguiente ejercicio de la rutina.")

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let contexto = Persistencia.contenedor.mainContext
        let sesion = try EntrenamientoService.requerirSesionActiva(en: contexto)
        let plan = try EntrenamientoService.siguienteEjercicio(en: sesion, contexto: contexto)
        let mensaje = "Siguiente: \(plan.nombre), \(plan.objetivo)."
        return .result(dialog: "\(mensaje)")
    }
}

struct TerminarEntrenamientoIntent: AppIntent {
    static let title: LocalizedStringResource = "Terminar entrenamiento"
    static let description = IntentDescription("Cierra el entrenamiento en curso y lo guarda en el historial.")

    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let contexto = Persistencia.contenedor.mainContext
        let sesion = try EntrenamientoService.requerirSesionActiva(en: contexto)
        let total = sesion.series.count
        let volumen = Int(sesion.volumenKg.rounded())
        EntrenamientoService.terminar(sesion, en: contexto)
        let mensaje = "Entrenamiento guardado: \(total) series y \(volumen) kilos de volumen."
        return .result(dialog: "\(mensaje)")
    }
}

struct PulsoAtajos: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: IniciarRutinaIntent(),
            phrases: [
                "Inicia \(\.$rutina) en \(.applicationName)",
                "Empieza la rutina \(\.$rutina) en \(.applicationName)"
            ],
            shortTitle: "Iniciar rutina",
            systemImageName: "figure.strengthtraining.traditional")
        AppShortcut(
            intent: RegistrarSerieIntent(),
            phrases: [
                "Registra una serie en \(.applicationName)",
                "Anota una serie en \(.applicationName)"
            ],
            shortTitle: "Registrar serie",
            systemImageName: "plus.circle")
        AppShortcut(
            intent: SiguienteEjercicioIntent(),
            phrases: ["Siguiente ejercicio en \(.applicationName)"],
            shortTitle: "Siguiente ejercicio",
            systemImageName: "forward.fill")
        AppShortcut(
            intent: TerminarEntrenamientoIntent(),
            phrases: [
                "Termina el entrenamiento en \(.applicationName)",
                "Termina mi entrenamiento en \(.applicationName)"
            ],
            shortTitle: "Terminar entrenamiento",
            systemImageName: "checkmark.circle")
    }
}
