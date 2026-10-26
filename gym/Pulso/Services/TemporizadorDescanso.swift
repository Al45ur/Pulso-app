import Foundation
import Observation

/// Cuenta atrás de descanso basada en una fecha de fin, no en un contador:
/// así no se desfasa si la app pasa a segundo plano.
@Observable
final class TemporizadorDescanso {
    private(set) var fin: Date?

    var activo: Bool { fin != nil }

    func iniciar(segundos: Int, desde ahora: Date = .now) {
        fin = ahora.addingTimeInterval(Double(max(0, segundos)))
    }

    func detener() { fin = nil }

    func restantes(en ahora: Date) -> Int {
        guard let fin else { return 0 }
        return max(0, Int(fin.timeIntervalSince(ahora).rounded(.up)))
    }

    static func formato(_ segundos: Int) -> String {
        String(format: "%d:%02d", segundos / 60, segundos % 60)
    }
}
