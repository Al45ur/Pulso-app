import SwiftUI

/// Pantalla 6: mapa de músculos desde dos ángulos. Al cambiar de ejercicio, la anatomía se actualiza.
struct MapaMusculosView: View {
    @State private var ficha: FichaEjercicio
    @State private var escenaFrontal = EscenaEntrenamiento()
    @State private var escenaPosterior = EscenaEntrenamiento()

    init(ficha: FichaEjercicio) {
        _ficha = State(initialValue: ficha)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Menu {
                    ForEach(CatalogoEjercicios.compartido.fichas) { opcion in
                        Button(opcion.nombre) { ficha = opcion }
                    }
                } label: {
                    HStack {
                        Text(ficha.nombre).font(.headline).multilineTextAlignment(.leading)
                        Spacer()
                        Image(systemName: "chevron.up.chevron.down")
                    }
                    .foregroundStyle(Tema.acento)
                    .tarjeta()
                }

                HStack(spacing: 10) {
                    columna("Frontal", escenaFrontal)
                    columna("Posterior", escenaPosterior)
                }

                LeyendaMusculos()

                grupo("Principales", ficha.musculosPrincipales, color: Tema.principal)
                if !ficha.musculosSecundarios.isEmpty {
                    grupo("Secundarios", ficha.musculosSecundarios, color: Tema.secundario)
                }

                Text(TextosAnatomia.aviso).font(.caption).foregroundStyle(Tema.textoSecundario)
                TarjetaPendientes(notas: ficha.pendienteValidacion)
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle("Músculos principales")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear(perform: actualizar)
        .onChange(of: ficha) { _, _ in actualizar() }
    }

    private func actualizar() {
        escenaFrontal.configurarAnatomia(ficha: ficha, vista: .frontal)
        escenaPosterior.configurarAnatomia(ficha: ficha, vista: .posterior)
    }

    private func columna(_ titulo: String, _ escena: EscenaEntrenamiento) -> some View {
        VStack(spacing: 4) {
            Text(titulo).font(.caption.bold()).foregroundStyle(Tema.textoSecundario)
            VistaEscena(escena: escena, permitirRotar: false)
                .frame(height: 330)
        }
        .padding(.vertical, 8)
        .marcoTarjeta()
    }

    private func grupo(_ titulo: String, _ musculos: [Musculo], color: Color) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(titulo).font(.headline)
            ForEach(musculos) { musculo in
                VStack(alignment: .leading, spacing: 2) {
                    HStack {
                        Circle().fill(color).frame(width: 10, height: 10)
                        Text(musculo.nombre).font(.subheadline.bold())
                    }
                    Text(musculo.descripcion).font(.caption).foregroundStyle(Tema.textoSecundario)
                }
            }
        }
        .tarjeta()
    }
}
