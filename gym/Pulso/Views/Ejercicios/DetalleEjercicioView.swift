import SwiftUI

/// Pantalla 2: ficha del ejercicio con el modelo 3D, la vista previa de músculos y la configuración.
struct DetalleEjercicioView: View {
    let ficha: FichaEjercicio

    @State private var config: ConfigEjercicio
    @State private var escenaModelo = EscenaEntrenamiento()
    @State private var escenaAnatomia = EscenaEntrenamiento()

    init(ficha: FichaEjercicio) {
        self.ficha = ficha
        _config = State(initialValue: ConfigEjercicio.cargar(ficha))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                ChipsMusculosEjercicio(ficha: ficha)

                HStack(spacing: 10) {
                    VistaEscena(escena: escenaModelo)
                        .frame(height: 300)
                        .marcoTarjeta()
                    VStack(spacing: 6) {
                        Text("Músculos").font(.caption.bold()).foregroundStyle(Tema.textoSecundario)
                        NavigationLink(value: DestinoEjercicio.anatomia(ficha.id)) {
                            VistaEscena(escena: escenaAnatomia, permitirRotar: false)
                                .frame(height: 260)
                                .allowsHitTesting(false)
                        }
                        .buttonStyle(.plain)
                    }
                    .frame(width: 110)
                    .padding(.vertical, 8)
                    .marcoTarjeta()
                }

                NavigationLink(value: DestinoEjercicio.animacion(ficha.id, fase: 0)) {
                    EtiquetaEnlace(titulo: "Iniciar animación 3D", icono: "play.fill", principal: true)
                }
                .buttonStyle(.plain)

                HStack(spacing: 10) {
                    NavigationLink(value: DestinoEjercicio.guia(ficha.id)) {
                        EtiquetaEnlace(titulo: "Guía paso a paso", icono: "list.number")
                    }
                    NavigationLink(value: DestinoEjercicio.anatomia(ficha.id)) {
                        EtiquetaEnlace(titulo: "Anatomía 3D", icono: "figure.arms.open")
                    }
                }
                .buttonStyle(.plain)

                Text("Tu objetivo").font(.headline)
                EditorConfigEjercicio(config: $config)

                Text("Descripción").font(.headline)
                Text(ficha.descripcion).foregroundStyle(Tema.textoSecundario).tarjeta()

                HStack(spacing: 10) {
                    NavigationLink(value: DestinoEjercicio.tecnica(ficha.id)) {
                        EtiquetaEnlace(titulo: "Técnica", icono: "checkmark.seal")
                    }
                    NavigationLink(value: DestinoEjercicio.resumen(ficha.id)) {
                        EtiquetaEnlace(titulo: "Resumen y rutina", icono: "plus.circle")
                    }
                }
                .buttonStyle(.plain)
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle(ficha.nombre)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            escenaModelo.configurar(ficha: ficha)
            escenaAnatomia.configurarAnatomia(ficha: ficha, vista: .posterior)
        }
        .onChange(of: config) { _, nueva in nueva.guardar(ficha) }
    }
}

extension View {
    /// Marco de tarjeta sin relleno interno, para contener vistas 3D.
    func marcoTarjeta() -> some View {
        background(Tema.tarjeta, in: RoundedRectangle(cornerRadius: 16))
            .overlay(RoundedRectangle(cornerRadius: 16).stroke(Tema.borde, lineWidth: 1))
            .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}
