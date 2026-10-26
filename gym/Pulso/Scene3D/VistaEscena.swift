import SwiftUI
import SceneKit
import Metal

/// Muestra una `EscenaEntrenamiento` dentro de SwiftUI.
/// Nota: SceneKit está marcado como obsoleto a partir de iOS 26 pero sigue funcionando;
/// si se migra a RealityKit, solo hay que reemplazar esta vista y EscenaEntrenamiento/Maniqui.
struct VistaEscena: UIViewRepresentable {
    let escena: EscenaEntrenamiento
    var permitirRotar = true
    /// Render continuo: actívalo solo mientras algo se anima, para ahorrar batería.
    var continuo = false
    /// Al cambiar este número se restablece la cámara a su posición inicial.
    var versionCamara = 0
    var alTocarMusculo: ((Musculo) -> Void)?

    func makeCoordinator() -> Coordinador { Coordinador() }

    func makeUIView(context: Context) -> SCNView {
        let vista = SCNView()
        vista.scene = escena.escena
        vista.pointOfView = escena.camara
        vista.backgroundColor = .clear
        vista.antialiasingMode = .multisampling4X
        vista.autoenablesDefaultLighting = false
        vista.allowsCameraControl = permitirRotar
        vista.rendersContinuously = continuo
        configurarControlador(vista)

        let toque = UITapGestureRecognizer(target: context.coordinator, action: #selector(Coordinador.tocar(_:)))
        vista.addGestureRecognizer(toque)
        context.coordinator.vista = vista
        context.coordinator.versionAplicada = versionCamara
        return vista
    }

    func updateUIView(_ vista: SCNView, context: Context) {
        vista.allowsCameraControl = permitirRotar
        vista.rendersContinuously = continuo
        context.coordinator.alTocar = alTocarMusculo
        if context.coordinator.versionAplicada != versionCamara {
            context.coordinator.versionAplicada = versionCamara
            escena.reiniciarCamara()
            vista.pointOfView = escena.camara
            configurarControlador(vista)
        }
    }

    private func configurarControlador(_ vista: SCNView) {
        let controlador = vista.defaultCameraController
        controlador.interactionMode = .orbitTurntable
        controlador.target = SCNVector3(0, escena.objetivoCamara, 0)
        controlador.maximumVerticalAngle = 80
        controlador.minimumVerticalAngle = -10
        controlador.inertiaEnabled = true
    }

    final class Coordinador: NSObject {
        weak var vista: SCNView?
        var alTocar: ((Musculo) -> Void)?
        var versionAplicada = 0

        @objc func tocar(_ gesto: UITapGestureRecognizer) {
            guard let vista, let alTocar else { return }
            let resultados = vista.hitTest(gesto.location(in: vista), options: nil)
            // Solo cuenta lo que queda delante: si lo primero tocado es la piel, no se elige un músculo del otro lado.
            if let primero = resultados.first, let musculo = Maniqui.musculo(de: primero.node) {
                alTocar(musculo)
            }
        }
    }
}

/// Genera imágenes del maniquí en una fase concreta: se usan como miniaturas y como fotogramas de la guía.
/// Las imágenes salen del mismo modelo 3D que la animación, así que siempre coinciden con el ejercicio real.
@MainActor
final class MiniaturaCache {
    static let compartida = MiniaturaCache()

    private var imagenes: [String: UIImage] = [:]
    private let escena = EscenaEntrenamiento(fondo: UIColor(red: 0.04, green: 0.09, blue: 0.15, alpha: 1))
    private var renderizador: SCNRenderer?

    func imagen(para ficha: FichaEjercicio, fase: Int, lado: CGFloat = 240) -> UIImage? {
        guard ficha.fases.indices.contains(fase) else { return nil }
        let clave = "\(ficha.id)#\(fase)"
        if let guardada = imagenes[clave] { return guardada }

        if renderizador == nil, let dispositivo = MTLCreateSystemDefaultDevice() {
            renderizador = SCNRenderer(device: dispositivo, options: nil)
        }
        guard let renderizador else { return nil }

        escena.configurar(ficha: ficha)
        escena.mostrar(ficha.fases[fase].pose)
        renderizador.scene = escena.escena
        renderizador.pointOfView = escena.camara
        let imagen = renderizador.snapshot(atTime: 0, with: CGSize(width: lado, height: lado),
                                           antialiasingMode: .multisampling4X)
        imagenes[clave] = imagen
        return imagen
    }
}

struct MiniaturaView: View {
    let ficha: FichaEjercicio
    var fase: Int?
    var lado: CGFloat = 76

    @State private var imagen: UIImage?

    var body: some View {
        ZStack {
            Tema.tarjeta
            if let imagen {
                Image(uiImage: imagen).resizable().scaledToFill()
            } else {
                Image(systemName: "figure.strengthtraining.traditional").foregroundStyle(Tema.acento)
            }
        }
        .frame(width: lado, height: lado)
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .task(id: "\(ficha.id)#\(fase ?? -1)") { @MainActor in
            imagen = MiniaturaCache.compartida.imagen(para: ficha, fase: fase ?? ficha.faseMiniatura)
        }
    }
}
