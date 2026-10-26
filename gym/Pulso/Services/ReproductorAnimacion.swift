import Foundation
import Observation

/// Estado de la reproducción de la animación 3D: tiempo, pausa y velocidad.
@Observable
final class ReproductorAnimacion {
    static let velocidades: [Double] = [0.25, 0.5, 1, 1.5, 2]

    let linea: LineaTiempo
    var tiempo: Double = 0
    var reproduciendo = false
    var velocidad: Double = 1

    init(linea: LineaTiempo) {
        self.linea = linea
    }

    var pose: Pose { linea.pose(en: tiempo) }
    var faseActual: Int { linea.faseCercana(a: tiempo) }

    /// Posición en el ciclo, de 0 a 1.
    var progreso: Double {
        get { linea.duracion > 0 ? linea.normalizar(tiempo) / linea.duracion : 0 }
        set { tiempo = min(max(newValue, 0), 1) * linea.duracion }
    }

    func avanzar(_ segundos: Double) {
        guard reproduciendo, segundos > 0 else { return }
        tiempo = linea.normalizar(tiempo + segundos * velocidad)
    }

    func reiniciar() {
        reproduciendo = false
        tiempo = 0
    }

    func irAFase(_ indice: Int) {
        reproduciendo = false
        tiempo = linea.tiempo(deFase: indice)
    }

    func siguienteFase() { irAFase(min(faseActual + 1, linea.poses.count - 1)) }
    func faseAnterior() { irAFase(max(faseActual - 1, 0)) }
}
