import SwiftUI

/// Pantalla 3: animación 3D. El maniquí se mueve girando sus articulaciones entre las fases del ejercicio.
struct AnimacionView: View {
    let ficha: FichaEjercicio

    @State private var reproductor: ReproductorAnimacion
    @State private var escena = EscenaEntrenamiento()
    @State private var versionCamara = 0

    init(ficha: FichaEjercicio, faseInicial: Int) {
        self.ficha = ficha
        let reproductor = ReproductorAnimacion(linea: ficha.lineaTiempo)
        reproductor.irAFase(faseInicial)
        _reproductor = State(initialValue: reproductor)
    }

    private var fases: [Fase] { ficha.fases }

    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                HStack {
                    ChipsMusculosEjercicio(ficha: ficha)
                    Spacer()
                    Text("\(reproductor.faseActual + 1)/\(fases.count)")
                        .font(.subheadline.bold().monospacedDigit()).foregroundStyle(Tema.textoSecundario)
                }

                ZStack(alignment: .topTrailing) {
                    VistaEscena(escena: escena, continuo: reproductor.reproduciendo, versionCamara: versionCamara)
                    Button {
                        versionCamara += 1
                    } label: {
                        Image(systemName: "arrow.counterclockwise.circle")
                            .font(.title2).padding(8).foregroundStyle(Tema.acento)
                    }
                    .accessibilityLabel("Restablecer cámara")
                }
                .frame(height: 340)
                .marcoTarjeta()

                selectorDeFase
                controles
                detalles
                navegacion
                TarjetaPendientes(notas: ficha.pendienteValidacion)
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle("Animación 3D")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            escena.configurar(ficha: ficha)
            aplicarPose()
        }
        .onChange(of: reproductor.tiempo) { _, _ in aplicarPose() }
        .onDisappear { reproductor.reproduciendo = false }
        // Reloj de la animación: avanza el tiempo ~60 veces por segundo mientras se reproduce.
        .task { @MainActor in
            var marca = Date.now
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 16_000_000)
                let ahora = Date.now
                reproductor.avanzar(min(ahora.timeIntervalSince(marca), 0.1))
                marca = ahora
            }
        }
    }

    private func aplicarPose() {
        escena.mostrar(reproductor.pose)
    }

    // MARK: - Secciones

    private var selectorDeFase: some View {
        HStack(spacing: 8) {
            ForEach(Array(fases.enumerated()), id: \.offset) { indice, fase in
                let activa = reproductor.faseActual == indice
                Button {
                    reproductor.irAFase(indice)
                } label: {
                    Text("\(indice + 1). \(fase.nombre)")
                        .font(.footnote.bold())
                        .foregroundStyle(activa ? Tema.fondo : Tema.textoSecundario)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(activa ? Tema.acento : Tema.tarjeta, in: Capsule())
                        .overlay(Capsule().stroke(Tema.borde, lineWidth: activa ? 0 : 1))
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var controles: some View {
        VStack(spacing: 12) {
            HStack(spacing: 14) {
                Button {
                    reproductor.reproduciendo.toggle()
                } label: {
                    Image(systemName: reproductor.reproduciendo ? "pause.fill" : "play.fill")
                        .font(.title2).foregroundStyle(Tema.fondo)
                        .frame(width: 52, height: 52)
                        .background(Tema.acento, in: Circle())
                }
                .accessibilityLabel(reproductor.reproduciendo ? "Pausar" : "Reproducir")

                Slider(
                    value: Binding(get: { reproductor.progreso }, set: { reproductor.progreso = $0 }),
                    in: 0...1,
                    onEditingChanged: { editando in
                        if editando { reproductor.reproduciendo = false }
                    })
                    .tint(Tema.acento)

                Button {
                    reproductor.reiniciar()
                } label: {
                    Image(systemName: "backward.end.fill").font(.title3).foregroundStyle(Tema.acento)
                }
                .accessibilityLabel("Reiniciar animación")
            }

            HStack {
                Text("Velocidad").font(.subheadline).foregroundStyle(Tema.textoSecundario)
                Picker("Velocidad", selection: Binding(get: { reproductor.velocidad },
                                                       set: { reproductor.velocidad = $0 })) {
                    ForEach(ReproductorAnimacion.velocidades, id: \.self) { valor in
                        Text("\(valor.formatted())×").tag(valor)
                    }
                }
                .pickerStyle(.segmented)
            }
        }
        .tarjeta()
    }

    private var detalles: some View {
        let fase = fases[reproductor.faseActual]
        return VStack(alignment: .leading, spacing: 6) {
            Label("Detalles del movimiento", systemImage: "lightbulb")
                .font(.subheadline.bold()).foregroundStyle(Tema.acento)
            Text(fase.nombre).font(.headline)
            Text(fase.descripcion).font(.subheadline).foregroundStyle(Tema.textoSecundario)
        }
        .tarjeta()
    }

    private var navegacion: some View {
        HStack(spacing: 10) {
            Button {
                reproductor.faseAnterior()
            } label: {
                Label("Anterior", systemImage: "chevron.left")
            }
            .buttonStyle(BotonSecundario())
            .disabled(reproductor.faseActual == 0)

            Button {
                reproductor.siguienteFase()
            } label: {
                Label("Siguiente", systemImage: "chevron.right")
            }
            .buttonStyle(BotonPrimario())
            .disabled(reproductor.faseActual >= fases.count - 1)
        }
    }
}
