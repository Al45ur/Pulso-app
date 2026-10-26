import SwiftUI
import SwiftData

/// Pantalla 8: resumen del ejercicio y botón real para añadirlo (o quitarlo) de «Mi rutina».
struct ResumenView: View {
    let ficha: FichaEjercicio

    @Environment(\.modelContext) private var contexto
    @State private var config: ConfigEjercicio
    @State private var escena = EscenaEntrenamiento()
    @State private var enRutina = false
    @State private var confirmacion: String?

    init(ficha: FichaEjercicio) {
        self.ficha = ficha
        _config = State(initialValue: ConfigEjercicio.cargar(ficha))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(ficha.nombre).font(.title2.bold())

                VistaEscena(escena: escena)
                    .frame(height: 280)
                    .marcoTarjeta()

                Text("Músculos trabajados").font(.headline)
                ChipsMusculosEjercicio(ficha: ficha)
                LeyendaMusculos()

                Text("Tu objetivo").font(.headline)
                EditorConfigEjercicio(config: $config)

                VStack(alignment: .leading, spacing: 8) {
                    Label("Recomendaciones técnicas", systemImage: "lightbulb").font(.headline)
                    ForEach(Array(ficha.seguridad.enumerated()), id: \.offset) { _, texto in
                        Text("• \(texto)").font(.subheadline).foregroundStyle(Tema.textoSecundario)
                    }
                }
                .tarjeta()

                TarjetaPendientes(notas: ficha.pendienteValidacion)
                acciones
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle("Resumen")
        .navigationBarTitleDisplayMode(.inline)
        .overlay(alignment: .bottom) {
            if let confirmacion {
                Label(confirmacion, systemImage: "checkmark.circle.fill")
                    .font(.subheadline.bold())
                    .foregroundStyle(Tema.fondo)
                    .padding(.horizontal, 18).padding(.vertical, 12)
                    .background(Tema.acento, in: Capsule())
                    .padding(.bottom, 24)
                    .transition(.move(edge: .bottom).combined(with: .opacity))
            }
        }
        .onAppear {
            escena.configurar(ficha: ficha)
            enRutina = RutinaUsuarioService.contiene(ficha, en: contexto)
        }
        .onChange(of: config) { _, nueva in nueva.guardar(ficha) }
        .sensoryFeedback(.success, trigger: enRutina)
        .task(id: confirmacion) { @MainActor in
            guard confirmacion != nil else { return }
            try? await Task.sleep(nanoseconds: 2_000_000_000)
            withAnimation { confirmacion = nil }
        }
    }

    @ViewBuilder
    private var acciones: some View {
        if enRutina {
            VStack(spacing: 10) {
                Button("Actualizar en Mi rutina") { agregar(mensaje: "Actualizado en Mi rutina") }
                    .buttonStyle(BotonPrimario())
                Button("Quitar de Mi rutina", role: .destructive) { quitar() }
                    .buttonStyle(BotonSecundario())
            }
        } else {
            Button {
                agregar(mensaje: "Añadido a Mi rutina")
            } label: {
                Label("Añadir a mi rutina", systemImage: "plus.circle.fill")
            }
            .buttonStyle(BotonPrimario())
        }
    }

    private func agregar(mensaje: String) {
        RutinaUsuarioService.agregar(ficha, config: config, en: contexto)
        enRutina = true
        withAnimation { confirmacion = mensaje }
    }

    private func quitar() {
        RutinaUsuarioService.quitar(ficha, en: contexto)
        enRutina = false
        withAnimation { confirmacion = "Quitado de Mi rutina" }
    }
}
