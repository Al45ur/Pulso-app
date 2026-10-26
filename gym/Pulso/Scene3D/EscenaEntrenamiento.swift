import SceneKit
import UIKit
import simd

enum VistaCamara: String, CaseIterable, Identifiable {
    case frontal, lateral, posterior
    var id: String { rawValue }

    var titulo: String {
        switch self {
        case .frontal: return "Frontal"
        case .lateral: return "Lateral"
        case .posterior: return "Posterior"
        }
    }

    /// Grados alrededor del personaje: 0 = de frente, 90 = desde su izquierda, 180 = de espaldas.
    var azimut: Double {
        switch self {
        case .frontal: return 0
        case .lateral: return 90
        case .posterior: return 180
        }
    }
}

/// Escena 3D con el maniquí, el equipo del ejercicio (banco, barra, cable, mancuernas), luces y cámara.
/// La animación y el resaltado muscular salen de la misma `FichaEjercicio`.
final class EscenaEntrenamiento {
    let escena = SCNScene()
    let maniqui = Maniqui()
    let camara = SCNNode()
    private(set) var objetivoCamara: Float = 0.9

    private let contenedorEquipo = SCNNode()
    private var equipo: [(prop: PropDTO, nodo: SCNNode)] = []
    private var camaraInicial: (azimut: Double, altura: Float, distancia: Float, objetivoY: Float)?

    init(fondo: UIColor? = nil) {
        escena.background.contents = fondo ?? UIColor.clear
        escena.rootNode.addChildNode(maniqui.raiz)
        escena.rootNode.addChildNode(contenedorEquipo)

        let lente = SCNCamera()
        lente.fieldOfView = 32
        lente.zNear = 0.1
        lente.zFar = 30
        camara.camera = lente
        escena.rootNode.addChildNode(camara)

        let plataforma = SCNCylinder(radius: 1.1, height: 0.02)
        let materialPlataforma = SCNMaterial()
        materialPlataforma.diffuse.contents = Paleta.plataforma
        materialPlataforma.lightingModel = .constant
        plataforma.materials = [materialPlataforma]
        let nodoPlataforma = SCNNode(geometry: plataforma)
        nodoPlataforma.position = SCNVector3(0, -0.01, 0)
        escena.rootNode.addChildNode(nodoPlataforma)

        agregarLuz(tipo: .ambient, intensidad: 650, color: UIColor(white: 0.85, alpha: 1), euler: nil)
        agregarLuz(tipo: .directional, intensidad: 900, color: .white, euler: SCNVector3(-0.7, 0.6, 0))
        agregarLuz(tipo: .directional, intensidad: 450, color: UIColor(red: 0.6, green: 0.8, blue: 1, alpha: 1),
                   euler: SCNVector3(-0.4, .pi + 0.5, 0))
    }

    private func agregarLuz(tipo: SCNLight.LightType, intensidad: CGFloat, color: UIColor, euler: SCNVector3?) {
        let luz = SCNLight()
        luz.type = tipo
        luz.intensity = intensidad
        luz.color = color
        let nodo = SCNNode()
        nodo.light = luz
        if let euler { nodo.eulerAngles = euler }
        escena.rootNode.addChildNode(nodo)
    }

    // MARK: - Configuración

    /// Prepara la escena para un ejercicio: equipo, cámara y músculos resaltados.
    func configurar(ficha: FichaEjercicio) {
        construirEquipo(ficha.props)
        maniqui.resaltar(principales: ficha.principales, secundarios: ficha.secundarios, aspecto: .piel)
        let c = ficha.camara
        colocarCamara(azimut: c.azimut, altura: Float(c.altura), distancia: Float(c.distancia), objetivoY: Float(c.objetivoY))
        mostrar(ficha.fases[ficha.faseMiniatura].pose)
    }

    /// Prepara la escena para estudiar la anatomía: sin equipo, postura neutra y cámara fija.
    func configurarAnatomia(ficha: FichaEjercicio?, vista: VistaCamara, seleccionado: Musculo? = nil) {
        construirEquipo([])
        maniqui.resaltar(principales: ficha?.principales ?? [], secundarios: ficha?.secundarios ?? [],
                         seleccionado: seleccionado, aspecto: .anatomia)
        colocarCamara(azimut: vista.azimut, altura: 1.0, distancia: 3.0, objetivoY: 0.95)
        mostrar(.neutra)
    }

    func mostrar(_ pose: Pose) {
        maniqui.aplicar(pose)
        actualizarEquipo()
    }

    func colocarCamara(azimut: Double, altura: Float, distancia: Float, objetivoY: Float) {
        camaraInicial = (azimut, altura, distancia, objetivoY)
        objetivoCamara = objetivoY
        let a = Float(azimut * .pi / 180)
        camara.simdPosition = SIMD3<Float>(distancia * sin(a), altura, distancia * cos(a))
        camara.simdLook(at: SIMD3<Float>(0, objetivoY, 0))
    }

    func reiniciarCamara() {
        guard let c = camaraInicial else { return }
        colocarCamara(azimut: c.azimut, altura: c.altura, distancia: c.distancia, objetivoY: c.objetivoY)
    }

    // MARK: - Equipo

    private func material(_ color: UIColor) -> SCNMaterial {
        let m = SCNMaterial()
        m.lightingModel = .blinn
        m.diffuse.contents = color
        return m
    }

    private func construirEquipo(_ props: [PropDTO]) {
        equipo.forEach { $0.nodo.removeFromParentNode() }
        equipo.removeAll()
        // Las mancuernas y manijas cuelgan de las manos del maniquí: se quitan al cambiar de ejercicio.
        for mano in [maniqui.manoI, maniqui.manoD] {
            mano.childNodes.filter { $0.name == "equipo" }.forEach { $0.removeFromParentNode() }
        }

        for prop in props {
            switch prop.tipo {
            case "banco":
                let nodo = SCNNode()
                let tablero = SCNBox(width: 0.32, height: 0.08, length: 1.15, chamferRadius: 0.02)
                tablero.materials = [material(UIColor(red: 0.12, green: 0.17, blue: 0.24, alpha: 1))]
                let nTablero = SCNNode(geometry: tablero)
                nTablero.position = SCNVector3(0, Medidas.bancoAltura - 0.04, -0.325)
                nodo.addChildNode(nTablero)
                for z: Float in [-0.8, 0.15] {
                    let pata = SCNBox(width: 0.06, height: CGFloat(Medidas.bancoAltura - 0.08), length: 0.06, chamferRadius: 0)
                    pata.materials = [material(UIColor(red: 0.18, green: 0.23, blue: 0.30, alpha: 1))]
                    let nPata = SCNNode(geometry: pata)
                    nPata.position = SCNVector3(0, (Medidas.bancoAltura - 0.08) / 2, z)
                    nodo.addChildNode(nPata)
                }
                contenedorEquipo.addChildNode(nodo)
                equipo.append((prop, nodo))
            case "bancoInclinado":
                // Asiento y respaldo; el respaldo gira desde el borde trasero del asiento.
                let nodo = SCNNode()
                let angulo = Float((prop.angulo ?? 65) * .pi / 180)
                let color = UIColor(red: 0.12, green: 0.17, blue: 0.24, alpha: 1)
                let asiento = SCNBox(width: 0.32, height: 0.08, length: 0.48, chamferRadius: 0.02)
                asiento.materials = [material(color)]
                let nAsiento = SCNNode(geometry: asiento)
                nAsiento.position = SCNVector3(0, Medidas.bancoAltura - 0.04, 0.06)
                nodo.addChildNode(nAsiento)
                let respaldo = SCNBox(width: 0.32, height: 0.8, length: 0.08, chamferRadius: 0.02)
                respaldo.materials = [material(color)]
                let nRespaldo = SCNNode(geometry: respaldo)
                let direccion = SIMD3<Float>(0, sin(angulo), -cos(angulo))
                nRespaldo.simdPosition = SIMD3<Float>(0, Medidas.bancoAltura, -0.18) + direccion * 0.4
                nRespaldo.eulerAngles = SCNVector3(-(Float.pi / 2 - angulo), 0, 0)
                nodo.addChildNode(nRespaldo)
                for z: Float in [-0.12, 0.25] {
                    let pata = SCNBox(width: 0.06, height: CGFloat(Medidas.bancoAltura - 0.08), length: 0.06, chamferRadius: 0)
                    pata.materials = [material(UIColor(red: 0.18, green: 0.23, blue: 0.30, alpha: 1))]
                    let nPata = SCNNode(geometry: pata)
                    nPata.position = SCNVector3(0, (Medidas.bancoAltura - 0.08) / 2, z)
                    nodo.addChildNode(nPata)
                }
                contenedorEquipo.addChildNode(nodo)
                equipo.append((prop, nodo))
            case "cable":
                let cilindro = SCNCylinder(radius: 0.004, height: 1)
                cilindro.materials = [material(Paleta.cable)]
                let nodo = SCNNode(geometry: cilindro)
                contenedorEquipo.addChildNode(nodo)
                equipo.append((prop, nodo))
            case "barra":
                let cilindro = SCNCylinder(radius: 0.012, height: 0.5)
                cilindro.materials = [material(Paleta.metal)]
                let nodo = SCNNode(geometry: cilindro)
                if prop.discos == true {
                    for signo: Float in [-1, 1] {
                        let disco = SCNCylinder(radius: 0.12, height: 0.03)
                        disco.materials = [material(UIColor(white: 0.12, alpha: 1))]
                        let nDisco = SCNNode(geometry: disco)
                        nDisco.name = "disco"
                        nDisco.simdPosition = SIMD3<Float>(0, signo * 0.22, 0)
                        nodo.addChildNode(nDisco)
                    }
                }
                contenedorEquipo.addChildNode(nodo)
                equipo.append((prop, nodo))
            case "mancuernas":
                for mano in [maniqui.manoI, maniqui.manoD] { mano.addChildNode(mancuerna()) }
            case "manija":
                let mano = prop.mano == "I" ? maniqui.manoI : maniqui.manoD
                let cilindro = SCNCylinder(radius: 0.014, height: 0.12)
                cilindro.materials = [material(Paleta.metal)]
                let nodo = SCNNode(geometry: cilindro)
                nodo.name = "equipo"
                nodo.eulerAngles = SCNVector3(0, 0, Float.pi / 2)
                mano.addChildNode(nodo)
            default:
                break
            }
        }
    }

    private func mancuerna() -> SCNNode {
        let contenedor = SCNNode()
        contenedor.name = "equipo"
        contenedor.eulerAngles = SCNVector3(0, 0, Float.pi / 2)   // el mango queda a lo largo del eje x
        let mango = SCNCylinder(radius: 0.012, height: 0.12)
        mango.materials = [material(Paleta.metal)]
        contenedor.addChildNode(SCNNode(geometry: mango))
        for signo: Float in [-1, 1] {
            let disco = SCNCylinder(radius: 0.055, height: 0.035)
            disco.materials = [material(UIColor(white: 0.1, alpha: 1))]
            let nodo = SCNNode(geometry: disco)
            nodo.simdPosition = SIMD3<Float>(0, signo * 0.075, 0)
            contenedor.addChildNode(nodo)
        }
        return contenedor
    }

    /// Recoloca la barra y el cable según dónde estén ahora las manos.
    private func actualizarEquipo() {
        let manoI = maniqui.manoI.simdWorldPosition
        let manoD = maniqui.manoD.simdWorldPosition
        for (prop, nodo) in equipo {
            switch prop.tipo {
            case "barra":
                let d = manoI - manoD
                let largo = simd_length(d)
                guard largo > 1e-4 else { continue }
                let u = d / largo
                let alargue = Float(prop.alargue ?? 0.06)
                colocarSegmento(nodo, desde: manoD - u * alargue, hasta: manoI + u * alargue)
                for disco in nodo.childNodes where disco.name == "disco" {
                    let signo: Float = disco.simdPosition.y < 0 ? -1 : 1
                    disco.simdPosition = SIMD3<Float>(0, signo * (largo / 2 + alargue - 0.04), 0)
                }
            case "cable":
                guard let ancla = prop.ancla, ancla.count == 3 else { continue }
                let origen = SIMD3<Float>(Float(ancla[0]), Float(ancla[1]), Float(ancla[2]))
                let destino: SIMD3<Float>
                switch prop.hacia ?? "centro" {
                case "manoI": destino = manoI
                case "manoD": destino = manoD
                default: destino = (manoI + manoD) / 2
                }
                colocarSegmento(nodo, desde: origen, hasta: destino)
            default:
                break
            }
        }
    }

    /// Estira un cilindro entre dos puntos. El cilindro de SceneKit tiene su eje a lo largo de y.
    private func colocarSegmento(_ nodo: SCNNode, desde a: SIMD3<Float>, hasta b: SIMD3<Float>) {
        let d = b - a
        let largo = simd_length(d)
        guard largo > 1e-4 else { return }
        nodo.simdPosition = (a + b) / 2
        nodo.simdOrientation = simd_quatf(from: SIMD3<Float>(0, 1, 0), to: d / largo)
        (nodo.geometry as? SCNCylinder)?.height = CGFloat(largo)
    }
}
