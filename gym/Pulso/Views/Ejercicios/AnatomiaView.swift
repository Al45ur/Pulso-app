import SwiftUI

/// Pantalla 4: anatomía 3D. Vistas posterior, lateral y frontal; al tocar un músculo se explica.
struct AnatomiaView: View {
    let ficha: FichaEjercicio

    @Environment(\.dismiss) private var cerrar
    @State private var vista: VistaCamara = .posterior
    @State private var seleccionado: Musculo?
    @State private var escena = EscenaEntrenamiento()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Picker("Vista", selection: $vista) {
                    ForEach(VistaCamara.allCases) { Text($0.titulo).tag($0) }
                }
                .pickerStyle(.segmented)

                VistaEscena(escena: escena, permitirRotar: false, alTocarMusculo: { musculo in
                    seleccionado = musculo
                })
                .frame(height: 380)
                .marcoTarjeta()

                LeyendaMusculos()
                Text("Toca un músculo para ver su nombre y una breve explicación.")
                    .font(.caption).foregroundStyle(Tema.textoSecundario)

                if let seleccionado {
                    tarjetaMusculo(seleccionado)
                }

                Text("Zonas trabajadas").font(.headline)
                ForEach(ficha.musculosPrincipales) { tarjetaZona($0, rol: "Principal", color: Tema.principal) }
                ForEach(ficha.musculosSecundarios) { tarjetaZona($0, rol: "Secundario", color: Tema.secundario) }

                Text(TextosAnatomia.aviso).font(.caption).foregroundStyle(Tema.textoSecundario)
                TarjetaPendientes(notas: ficha.pendienteValidacion)

                NavigationLink(value: DestinoEjercicio.mapa(ficha.id)) {
                    EtiquetaEnlace(titulo: "Mapa de músculos", icono: "figure.stand")
                }
                .buttonStyle(.plain)

                Button("Volver al ejercicio") { cerrar() }
                    .buttonStyle(BotonPrimario())
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle("Vista anatómica")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear(perform: actualizarEscena)
        .onChange(of: vista) { _, _ in actualizarEscena() }
        .onChange(of: seleccionado) { _, _ in actualizarEscena() }
    }

    private func actualizarEscena() {
        escena.configurarAnatomia(ficha: ficha, vista: vista, seleccionado: seleccionado)
    }

    private func tarjetaMusculo(_ musculo: Musculo) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Circle().fill(musculo.color(en: ficha)).frame(width: 10, height: 10)
                Text(musculo.nombre).font(.headline)
                Spacer()
                Text(etiquetaRol(ficha.rol(de: musculo))).font(.caption).foregroundStyle(Tema.textoSecundario)
            }
            Text(musculo.descripcion).font(.subheadline).foregroundStyle(Tema.textoSecundario)
        }
        .tarjeta()
    }

    private func tarjetaZona(_ musculo: Musculo, rol: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Circle().fill(color).frame(width: 10, height: 10)
                Text(musculo.nombre).font(.subheadline.bold())
                Spacer()
                Text(rol).font(.caption).foregroundStyle(Tema.textoSecundario)
            }
            Text(musculo.descripcion).font(.caption).foregroundStyle(Tema.textoSecundario)
        }
        .tarjeta()
    }

    private func etiquetaRol(_ rol: RolMuscular) -> String {
        switch rol {
        case .principal: return "Principal en este ejercicio"
        case .secundario: return "Secundario en este ejercicio"
        case .ninguno: return "No asociado a este ejercicio"
        }
    }
}
