import Foundation

/// Articulaciones del maniquí. I = izquierda, D = derecha.
enum Articulacion: String, CaseIterable {
    case columna, cuello
    case hombroI, hombroD, codoI, codoD
    case caderaI, caderaD, rodillaI, rodillaD, tobilloI, tobilloD
}

/// Grados. `flexion` y `abduccion` siguen la convención de Maniqui.swift
/// (flexión positiva = hacia delante; en la rodilla, el talón hacia el glúteo).
/// `rotacion` solo la usa el hombro: giro del brazo sobre su propio eje (positivo = rotación externa,
/// el antebrazo flexionado sale hacia fuera). Con ella el antebrazo puede quedar vertical con el codo abierto, como en un press.
struct Angulos: Equatable {
    var flexion: Double = 0
    var abduccion: Double = 0
    var rotacion: Double = 0
}

/// Postura completa del cuerpo: dónde está la pelvis, cuánto se inclina y el ángulo de cada articulación.
struct Pose: Equatable {
    var posicion: [Double] = [0, 0.9, 0]
    var pitch: Double = 0
    var articulaciones: [Articulacion: Angulos] = [:]

    func angulos(_ articulacion: Articulacion) -> Angulos {
        articulaciones[articulacion] ?? Angulos()
    }

    /// De pie, brazos ligeramente separados: sirve para mostrar la anatomía.
    static let neutra = Pose(
        posicion: [0, 0.9, 0],
        pitch: 0,
        articulaciones: [
            .hombroI: Angulos(flexion: 0, abduccion: 12),
            .hombroD: Angulos(flexion: 0, abduccion: 12)
        ])

    static func mezclar(_ a: Pose, _ b: Pose, t: Double) -> Pose {
        func lerp(_ x: Double, _ y: Double) -> Double { x + (y - x) * t }
        var resultado = Pose()
        resultado.posicion = zip(a.posicion, b.posicion).map(lerp)
        resultado.pitch = lerp(a.pitch, b.pitch)
        for articulacion in Articulacion.allCases {
            let p = a.angulos(articulacion)
            let q = b.angulos(articulacion)
            resultado.articulaciones[articulacion] = Angulos(
                flexion: lerp(p.flexion, q.flexion),
                abduccion: lerp(p.abduccion, q.abduccion),
                rotacion: lerp(p.rotacion, q.rotacion))
        }
        return resultado
    }

    /// Aceleración y frenado suaves entre dos posturas.
    static func suavizar(_ t: Double) -> Double {
        let x = min(max(t, 0), 1)
        return x * x * (3 - 2 * x)
    }
}

extension Pose: Decodable {
    private enum Claves: String, CodingKey { case raiz, art }

    private struct Raiz: Decodable {
        let pos: [Double]
        let pitch: Double?
    }

    init(from decoder: Decoder) throws {
        let contenedor = try decoder.container(keyedBy: Claves.self)
        let raiz = try contenedor.decode(Raiz.self, forKey: .raiz)
        guard raiz.pos.count == 3 else {
            throw DecodingError.dataCorruptedError(
                forKey: .raiz, in: contenedor, debugDescription: "raiz.pos debe tener 3 valores")
        }
        // Se decodifica como [String: [Double]] porque Codable codifica los diccionarios con claves
        // enum como una lista plana, no como un objeto JSON.
        let crudo = try contenedor.decodeIfPresent([String: [Double]].self, forKey: .art) ?? [:]
        var articulaciones: [Articulacion: Angulos] = [:]
        for (nombre, valores) in crudo {
            guard let articulacion = Articulacion(rawValue: nombre), (1...3).contains(valores.count) else {
                throw DecodingError.dataCorruptedError(
                    forKey: .art, in: contenedor,
                    debugDescription: "Articulación desconocida o con valores inválidos: \(nombre)")
            }
            articulaciones[articulacion] = Angulos(
                flexion: valores[0],
                abduccion: valores.count > 1 ? valores[1] : 0,
                rotacion: valores.count > 2 ? valores[2] : 0)
        }
        self.init(posicion: raiz.pos, pitch: raiz.pitch ?? 0, articulaciones: articulaciones)
    }
}

/// Recorre las fases de un ejercicio en bucle: cada fase pasa a la siguiente y la última vuelve a la primera.
struct LineaTiempo {
    let poses: [Pose]
    let segundosPorTramo: Double

    init(poses: [Pose], segundosPorTramo: Double = 1.4) {
        self.poses = poses
        self.segundosPorTramo = segundosPorTramo
    }

    var duracion: Double { Double(poses.count) * segundosPorTramo }

    func normalizar(_ tiempo: Double) -> Double {
        let d = duracion
        guard d > 0 else { return 0 }
        let resto = tiempo.truncatingRemainder(dividingBy: d)
        return resto < 0 ? resto + d : resto
    }

    func pose(en tiempo: Double) -> Pose {
        guard poses.count > 1 else { return poses.first ?? .neutra }
        let posicion = normalizar(tiempo) / segundosPorTramo
        let i = min(Int(posicion), poses.count - 1)
        let fraccion = posicion - Double(i)
        return Pose.mezclar(poses[i], poses[(i + 1) % poses.count], t: Pose.suavizar(fraccion))
    }

    func tiempo(deFase indice: Int) -> Double {
        Double(min(max(indice, 0), max(poses.count - 1, 0))) * segundosPorTramo
    }

    /// Fase más cercana al instante indicado.
    func faseCercana(a tiempo: Double) -> Int {
        guard !poses.isEmpty, segundosPorTramo > 0 else { return 0 }
        return Int((normalizar(tiempo) / segundosPorTramo).rounded()) % poses.count
    }
}
