import SceneKit
import UIKit
import simd

/// Medidas del esqueleto en metros. Deben coincidir con tools/verificar_poses.py,
/// que se usa para comprobar las poses sin Xcode.
enum Medidas {
    static let columna = SIMD3<Float>(0, 0.05, 0)       // relativo a la pelvis
    static let hombro = SIMD3<Float>(0.19, 0.45, 0)     // relativo a la columna (izquierda = +x)
    static let cuello = SIMD3<Float>(0, 0.50, 0)        // relativo a la columna
    static let cabeza = SIMD3<Float>(0, 0.14, 0)        // relativo al cuello
    static let cadera = SIMD3<Float>(0.09, 0, 0)        // relativo a la pelvis (izquierda = +x)
    static let brazo: Float = 0.30
    static let antebrazo: Float = 0.27
    static let mano: Float = 0.04                       // el agarre está a antebrazo + mano del codo
    static let muslo: Float = 0.42
    static let pantorrilla: Float = 0.41
    static let tobilloSuelo: Float = 0.07
    static let bancoAltura: Float = 0.38
}

enum Paleta {
    static let cuerpo = UIColor(red: 0.20, green: 0.28, blue: 0.38, alpha: 1)
    static let musculoNeutro = UIColor(red: 0.30, green: 0.40, blue: 0.53, alpha: 1)
    static let principal = UIColor(red: 1.0, green: 0.25, blue: 0.20, alpha: 1)
    static let secundario = UIColor(red: 1.0, green: 0.60, blue: 0.15, alpha: 1)
    static let metal = UIColor(red: 0.82, green: 0.85, blue: 0.9, alpha: 1)
    static let cable = UIColor(red: 0.45, green: 0.78, blue: 1.0, alpha: 1)
    static let plataforma = UIColor(red: 0.05, green: 0.11, blue: 0.18, alpha: 1)
}

private func rotX(_ grados: Double) -> simd_quatf {
    simd_quatf(angle: Float(grados * .pi / 180), axis: SIMD3<Float>(1, 0, 0))
}

private func rotZ(_ grados: Double) -> simd_quatf {
    simd_quatf(angle: Float(grados * .pi / 180), axis: SIMD3<Float>(0, 0, 1))
}

/// Maniquí humano articulado. Cada articulación es un nodo; al aplicar una `Pose` se giran los nodos,
/// no se deforma ninguna imagen. Los volúmenes musculares son nodos con nombre «musculo:<id>».
///
/// Convención (personaje mirando a +z, +y arriba, +x = su izquierda):
/// - flexión positiva: hombro, cadera, codo, tobillo (dorsiflexión) y rodilla llevan el segmento
///   hacia delante o el talón hacia el glúteo; columna y cuello se inclinan hacia delante.
/// - abducción positiva: separa el brazo o la pierna del cuerpo.
final class Maniqui {
    let raiz = SCNNode()
    private(set) var manoI = SCNNode()
    private(set) var manoD = SCNNode()
    private var juntas: [Articulacion: SCNNode] = [:]
    private var volumenes: [Musculo: [SCNNode]] = [:]

    /// Verdadero si se cargó el personaje de Resources/maniqui.*; falso si se usa el maniquí procedural de respaldo.
    private(set) var usaMalla = false

    var musculosDisponibles: Set<Musculo> { Set(volumenes.keys) }

    init() {
        raiz.name = "pelvis"
        construirEsqueleto()
        if let piezas = MallasManiqui.geometrias() {
            adjuntar(piezas)
            usaMalla = true
        } else {
            construir()
        }
        resaltar(principales: [], secundarios: [])
    }

    // MARK: - Pose

    func aplicar(_ pose: Pose) {
        let p = pose.posicion
        raiz.simdPosition = SIMD3<Float>(Float(p[0]), Float(p[1]), Float(p[2]))
        raiz.simdOrientation = rotX(pose.pitch)
        for (articulacion, nodo) in juntas {
            nodo.simdOrientation = orientacion(articulacion, pose.angulos(articulacion))
        }
    }

    private func orientacion(_ articulacion: Articulacion, _ a: Angulos) -> simd_quatf {
        switch articulacion {
        case .columna, .cuello:
            return rotX(a.flexion)
        case .hombroI, .caderaI:
            return rotX(-a.flexion) * rotZ(a.abduccion)
        case .hombroD, .caderaD:
            return rotX(-a.flexion) * rotZ(-a.abduccion)
        case .codoI, .codoD, .tobilloI, .tobilloD:
            return rotX(-a.flexion)
        case .rodillaI, .rodillaD:
            return rotX(a.flexion)
        }
    }

    // MARK: - Resaltado muscular

    /// Pinta de rojo los músculos principales y de naranja los secundarios; el resto queda neutro.
    func resaltar(principales: Set<Musculo>, secundarios: Set<Musculo>, seleccionado: Musculo? = nil) {
        for (musculo, nodos) in volumenes {
            let color: UIColor
            var brillo: CGFloat = 0
            if principales.contains(musculo) {
                color = Paleta.principal; brillo = 0.35
            } else if secundarios.contains(musculo) {
                color = Paleta.secundario; brillo = 0.30
            } else {
                color = Paleta.musculoNeutro
            }
            if musculo == seleccionado { brillo = 0.95 }
            for nodo in nodos {
                guard let material = nodo.geometry?.firstMaterial else { continue }
                material.diffuse.contents = color
                material.emission.contents = color
                material.emission.intensity = brillo
            }
        }
    }

    static func musculo(de nodo: SCNNode) -> Musculo? {
        var actual: SCNNode? = nodo
        while let n = actual {
            if let nombre = n.name, nombre.hasPrefix("musculo:") {
                return Musculo(rawValue: String(nombre.dropFirst("musculo:".count)))
            }
            actual = n.parent
        }
        return nil
    }

    // MARK: - Construcción

    private func material(_ color: UIColor) -> SCNMaterial {
        let m = SCNMaterial()
        m.lightingModel = .blinn
        m.diffuse.contents = color
        m.specular.contents = UIColor(white: 0.25, alpha: 1)
        return m
    }

    private func forma(_ geometria: SCNGeometry, color: UIColor = Paleta.cuerpo,
                       en padre: SCNNode, pos: SIMD3<Float>,
                       escala: SIMD3<Float> = SIMD3<Float>(repeating: 1)) {
        geometria.materials = [material(color)]
        let nodo = SCNNode(geometry: geometria)
        nodo.simdPosition = pos
        nodo.simdScale = escala
        padre.addChildNode(nodo)
    }

    private func musculo(_ musculo: Musculo, _ geometria: SCNGeometry, en padre: SCNNode,
                         pos: SIMD3<Float>, escala: SIMD3<Float> = SIMD3<Float>(repeating: 1)) {
        geometria.materials = [material(Paleta.musculoNeutro)]
        let nodo = SCNNode(geometry: geometria)
        nodo.name = "musculo:" + musculo.rawValue
        nodo.simdPosition = pos
        nodo.simdScale = escala
        padre.addChildNode(nodo)
        volumenes[musculo, default: []].append(nodo)
    }

    private func junta(_ articulacion: Articulacion, en padre: SCNNode, pos: SIMD3<Float>) -> SCNNode {
        let nodo = SCNNode()
        nodo.name = articulacion.rawValue
        nodo.simdPosition = pos
        padre.addChildNode(nodo)
        juntas[articulacion] = nodo
        return nodo
    }

    private func nodoDe(_ articulacion: Articulacion) -> SCNNode {
        juntas[articulacion] ?? SCNNode()
    }

    // MARK: - Esqueleto (común a los dos modelos)

    private func construirEsqueleto() {
        let columna = junta(.columna, en: raiz, pos: Medidas.columna)
        _ = junta(.cuello, en: columna, pos: Medidas.cuello)
        esqueletoBrazo(hombro: .hombroI, codo: .codoI, lado: 1, columna: columna)
        esqueletoBrazo(hombro: .hombroD, codo: .codoD, lado: -1, columna: columna)
        esqueletoPierna(cadera: .caderaI, rodilla: .rodillaI, tobillo: .tobilloI, lado: 1)
        esqueletoPierna(cadera: .caderaD, rodilla: .rodillaD, tobillo: .tobilloD, lado: -1)
    }

    private func esqueletoBrazo(hombro: Articulacion, codo: Articulacion, lado: Float, columna: SCNNode) {
        let h = junta(hombro, en: columna, pos: SIMD3<Float>(lado * Medidas.hombro.x, Medidas.hombro.y, Medidas.hombro.z))
        let c = junta(codo, en: h, pos: SIMD3<Float>(0, -Medidas.brazo, 0))
        let punto = SCNNode()
        punto.name = "agarre"
        punto.simdPosition = SIMD3<Float>(0, -(Medidas.antebrazo + Medidas.mano), 0)
        c.addChildNode(punto)
        if lado > 0 { manoI = punto } else { manoD = punto }
    }

    private func esqueletoPierna(cadera: Articulacion, rodilla: Articulacion, tobillo: Articulacion, lado: Float) {
        let ch = junta(cadera, en: raiz, pos: SIMD3<Float>(lado * Medidas.cadera.x, Medidas.cadera.y, Medidas.cadera.z))
        let r = junta(rodilla, en: ch, pos: SIMD3<Float>(0, -Medidas.muslo, 0))
        _ = junta(tobillo, en: r, pos: SIMD3<Float>(0, -Medidas.pantorrilla, 0))
    }

    // MARK: - Personaje a partir de las mallas

    /// Cuelga cada pieza (piel o capa muscular) del nodo de su articulación. Los músculos quedan
    /// registrados en `volumenes` para poder resaltarlos y para detectar toques.
    private func adjuntar(_ piezas: [(parte: ParteMalla, geometria: SCNGeometry)]) {
        for (parte, geometria) in piezas {
            let padre: SCNNode?
            if parte.junta == "raiz" {
                padre = raiz
            } else {
                padre = Articulacion(rawValue: parte.junta).flatMap { juntas[$0] }
            }
            guard let padre else { continue }

            let esMusculo = parte.rol == "musculo"
            geometria.materials = [material(esMusculo ? Paleta.musculoNeutro : Paleta.cuerpo)]
            let nodo = SCNNode(geometry: geometria)
            if esMusculo, let id = parte.musculo, let musculo = Musculo(rawValue: id) {
                nodo.name = "musculo:" + id
                volumenes[musculo, default: []].append(nodo)
            } else {
                nodo.name = parte.nombre
            }
            padre.addChildNode(nodo)
        }
    }

    // MARK: - Maniquí procedural de respaldo

    private func capsula(_ radio: CGFloat, _ largo: CGFloat) -> SCNCapsule {
        SCNCapsule(capRadius: radio, height: max(largo, radio * 2 + 0.001))
    }

    private func construir() {
        // Pelvis
        forma(SCNSphere(radius: 0.11), en: raiz, pos: .zero, escala: SIMD3<Float>(1.25, 0.85, 0.95))

        // Tronco
        let columna = nodoDe(.columna)
        forma(capsula(0.12, 0.52), en: columna, pos: SIMD3<Float>(0, 0.26, 0), escala: SIMD3<Float>(1.3, 1, 0.8))
        musculo(.pectorales, SCNSphere(radius: 0.075), en: columna, pos: SIMD3<Float>(0.085, 0.36, 0.085), escala: SIMD3<Float>(1.2, 0.8, 0.6))
        musculo(.pectorales, SCNSphere(radius: 0.075), en: columna, pos: SIMD3<Float>(-0.085, 0.36, 0.085), escala: SIMD3<Float>(1.2, 0.8, 0.6))
        musculo(.abdomen, SCNBox(width: 0.20, height: 0.22, length: 0.04, chamferRadius: 0.02), en: columna, pos: SIMD3<Float>(0, 0.16, 0.098))
        musculo(.dorsales, SCNBox(width: 0.30, height: 0.25, length: 0.04, chamferRadius: 0.02), en: columna, pos: SIMD3<Float>(0, 0.24, -0.095))
        musculo(.trapecio, SCNBox(width: 0.24, height: 0.12, length: 0.04, chamferRadius: 0.02), en: columna, pos: SIMD3<Float>(0, 0.43, -0.08))
        musculo(.lumbar, capsula(0.025, 0.18), en: columna, pos: SIMD3<Float>(0.045, 0.08, -0.098))
        musculo(.lumbar, capsula(0.025, 0.18), en: columna, pos: SIMD3<Float>(-0.045, 0.08, -0.098))

        // Cuello y cabeza
        let cuello = nodoDe(.cuello)
        forma(SCNCylinder(radius: 0.04, height: 0.09), en: cuello, pos: SIMD3<Float>(0, 0.04, 0))
        forma(SCNSphere(radius: 0.105), en: cuello, pos: Medidas.cabeza, escala: SIMD3<Float>(0.9, 1.05, 1))

        // Glúteos
        musculo(.gluteos, SCNSphere(radius: 0.075), en: raiz, pos: SIMD3<Float>(0.07, -0.03, -0.085))
        musculo(.gluteos, SCNSphere(radius: 0.075), en: raiz, pos: SIMD3<Float>(-0.07, -0.03, -0.085))

        construirBrazo(hombro: .hombroI, codo: .codoI, lado: 1, columna: columna)
        construirBrazo(hombro: .hombroD, codo: .codoD, lado: -1, columna: columna)
        construirPierna(cadera: .caderaI, rodilla: .rodillaI, tobillo: .tobilloI, lado: 1)
        construirPierna(cadera: .caderaD, rodilla: .rodillaD, tobillo: .tobilloD, lado: -1)
    }

    private func construirBrazo(hombro: Articulacion, codo: Articulacion, lado: Float, columna: SCNNode) {
        let h = nodoDe(hombro)
        forma(SCNSphere(radius: 0.05), en: h, pos: .zero)
        forma(capsula(0.04, CGFloat(Medidas.brazo)), en: h, pos: SIMD3<Float>(0, -Medidas.brazo / 2, 0))
        musculo(.deltoides, SCNSphere(radius: 0.055), en: h, pos: SIMD3<Float>(lado * 0.01, -0.01, 0))
        musculo(.triceps, capsula(0.032, 0.22), en: h, pos: SIMD3<Float>(0, -0.15, -0.032))
        musculo(.biceps, capsula(0.030, 0.20), en: h, pos: SIMD3<Float>(0, -0.15, 0.032))

        let c = nodoDe(codo)
        forma(SCNSphere(radius: 0.035), en: c, pos: .zero)
        forma(capsula(0.033, CGFloat(Medidas.antebrazo)), en: c, pos: SIMD3<Float>(0, -Medidas.antebrazo / 2, 0))
        musculo(.antebrazos, capsula(0.036, 0.20), en: c, pos: SIMD3<Float>(0, -0.14, 0))

        forma(SCNSphere(radius: 0.04), en: lado > 0 ? manoI : manoD, pos: .zero)
    }

    private func construirPierna(cadera: Articulacion, rodilla: Articulacion, tobillo: Articulacion, lado: Float) {
        let ch = nodoDe(cadera)
        forma(capsula(0.06, CGFloat(Medidas.muslo)), en: ch, pos: SIMD3<Float>(0, -Medidas.muslo / 2, 0))
        musculo(.cuadriceps, capsula(0.055, 0.32), en: ch, pos: SIMD3<Float>(0, -0.21, 0.035))
        musculo(.isquiotibiales, capsula(0.055, 0.32), en: ch, pos: SIMD3<Float>(0, -0.21, -0.035))
        musculo(.aductores, capsula(0.04, 0.28), en: ch, pos: SIMD3<Float>(-lado * 0.035, -0.2, 0))

        let r = nodoDe(rodilla)
        forma(SCNSphere(radius: 0.045), en: r, pos: .zero)
        forma(capsula(0.045, CGFloat(Medidas.pantorrilla)), en: r, pos: SIMD3<Float>(0, -Medidas.pantorrilla / 2, 0))
        musculo(.gemelos, capsula(0.04, 0.25), en: r, pos: SIMD3<Float>(0, -0.2, -0.035))

        let t = nodoDe(tobillo)
        forma(SCNBox(width: 0.09, height: 0.07, length: 0.24, chamferRadius: 0.02), en: t,
              pos: SIMD3<Float>(0, -0.035, 0.06))
    }
}
