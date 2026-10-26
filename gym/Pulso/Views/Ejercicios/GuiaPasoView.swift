import SwiftUI

/// Pantalla 7: guía visual. Cada fase del ejercicio tiene un fotograma generado del mismo modelo 3D
/// y se puede abrir la animación justo en esa fase.
struct GuiaPasoView: View {
    let ficha: FichaEjercicio
    @State private var seleccionada = 0

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                ForEach(Array(ficha.fases.enumerated()), id: \.offset) { indice, fase in
                    Button {
                        seleccionada = indice
                    } label: {
                        filaDeFase(indice, fase)
                    }
                    .buttonStyle(.plain)
                }

                HStack(spacing: 10) {
                    Button {
                        seleccionada = max(seleccionada - 1, 0)
                    } label: {
                        Label("Anterior", systemImage: "chevron.left")
                    }
                    .buttonStyle(BotonSecundario())
                    .disabled(seleccionada == 0)

                    Button {
                        seleccionada = min(seleccionada + 1, ficha.fases.count - 1)
                    } label: {
                        Label("Siguiente", systemImage: "chevron.right")
                    }
                    .buttonStyle(BotonSecundario())
                    .disabled(seleccionada >= ficha.fases.count - 1)
                }

                NavigationLink(value: DestinoEjercicio.animacion(ficha.id, fase: seleccionada)) {
                    EtiquetaEnlace(titulo: "Ver «\(ficha.fases[seleccionada].nombre)» en 3D",
                                   icono: "play.fill", principal: true)
                }
                .buttonStyle(.plain)

                TarjetaPendientes(notas: ficha.pendienteValidacion)
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle("Guía visual")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func filaDeFase(_ indice: Int, _ fase: Fase) -> some View {
        let activa = indice == seleccionada
        return HStack(alignment: .top, spacing: 12) {
            Text("\(indice + 1)")
                .font(.subheadline.bold())
                .foregroundStyle(activa ? Tema.fondo : Tema.acento)
                .frame(width: 28, height: 28)
                .background(activa ? Tema.acento : Tema.tarjeta, in: Circle())
                .overlay(Circle().stroke(Tema.acento, lineWidth: 1))
            MiniaturaView(ficha: ficha, fase: indice, lado: 96)
            VStack(alignment: .leading, spacing: 4) {
                Text(fase.nombre).font(.headline)
                Text(fase.descripcion).font(.footnote).foregroundStyle(Tema.textoSecundario)
                    .multilineTextAlignment(.leading)
            }
            .foregroundStyle(.primary)
            Spacer(minLength: 0)
        }
        .padding(10)
        .background(Tema.tarjeta, in: RoundedRectangle(cornerRadius: 16))
        .overlay(RoundedRectangle(cornerRadius: 16).stroke(activa ? Tema.acento : Tema.borde, lineWidth: activa ? 2 : 1))
    }
}
