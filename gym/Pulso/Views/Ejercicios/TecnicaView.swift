import SwiftUI

/// Pantalla 5: descripción y técnica, en pestañas.
struct TecnicaView: View {
    let ficha: FichaEjercicio

    private enum Pestana: String, CaseIterable, Identifiable {
        case descripcion = "Descripción"
        case tecnica = "Técnica"
        case musculos = "Músculos"
        case consejos = "Consejos"
        var id: String { rawValue }
    }

    @State private var pestana: Pestana = .descripcion

    var body: some View {
        VStack(spacing: 0) {
            barraDePestanas
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    switch pestana {
                    case .descripcion: descripcion
                    case .tecnica: tecnica
                    case .musculos: musculos
                    case .consejos: consejos
                    }
                    TarjetaPendientes(notas: ficha.pendienteValidacion)
                }
                .padding()
            }
        }
        .background(Tema.fondo)
        .navigationTitle(ficha.nombre)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var barraDePestanas: some View {
        HStack {
            ForEach(Pestana.allCases) { opcion in
                Button {
                    pestana = opcion
                } label: {
                    VStack(spacing: 6) {
                        Text(opcion.rawValue)
                            .font(.subheadline.bold())
                            .foregroundStyle(pestana == opcion ? Tema.acento : Tema.textoSecundario)
                        Rectangle()
                            .fill(pestana == opcion ? Tema.acento : Color.clear)
                            .frame(height: 2)
                    }
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal)
        .padding(.top, 8)
    }

    private func lista(_ items: [String], icono: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(items.enumerated()), id: \.offset) { _, texto in
                HStack(alignment: .top, spacing: 10) {
                    Image(systemName: icono).foregroundStyle(color)
                    Text(texto)
                }
            }
        }
    }

    private var descripcion: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 8) {
                Text("Descripción").font(.headline)
                Text(ficha.descripcion).foregroundStyle(Tema.textoSecundario)
                Label(ficha.equipo, systemImage: "dumbbell").font(.subheadline).foregroundStyle(Tema.textoSecundario)
            }
            .tarjeta()
            VStack(alignment: .leading, spacing: 8) {
                Text("Objetivo sugerido").font(.headline)
                Text("\(ficha.objetivoSugerido) · descanso \(ficha.descansoSeg) s")
                    .foregroundStyle(Tema.textoSecundario)
            }
            .tarjeta()
        }
    }

    private var tecnica: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 10) {
                Text("Paso a paso").font(.headline)
                ForEach(Array(ficha.pasos.enumerated()), id: \.offset) { indice, paso in
                    HStack(alignment: .top, spacing: 10) {
                        Text("\(indice + 1)")
                            .font(.caption.bold()).foregroundStyle(Tema.fondo)
                            .frame(width: 22, height: 22).background(Tema.acento, in: Circle())
                        Text(paso)
                    }
                }
            }
            .tarjeta()

            VStack(alignment: .leading, spacing: 10) {
                Label("Errores comunes", systemImage: "xmark.circle.fill")
                    .font(.headline).foregroundStyle(Tema.principal)
                lista(ficha.errores, icono: "circle.fill", color: Tema.principal)
            }
            .tarjeta()

            NavigationLink(value: DestinoEjercicio.guia(ficha.id)) {
                EtiquetaEnlace(titulo: "Ver guía visual", icono: "list.number")
            }
            .buttonStyle(.plain)
        }
    }

    private var musculos: some View {
        VStack(alignment: .leading, spacing: 14) {
            ForEach(ficha.musculosPrincipales) { fila($0, rol: "Principal", color: Tema.principal) }
            ForEach(ficha.musculosSecundarios) { fila($0, rol: "Secundario", color: Tema.secundario) }
            if ficha.musculosSecundarios.isEmpty {
                Text("Este ejercicio no tiene músculos secundarios registrados en el catálogo.")
                    .font(.caption).foregroundStyle(Tema.textoSecundario)
            }
            Text(TextosAnatomia.aviso).font(.caption).foregroundStyle(Tema.textoSecundario)
            NavigationLink(value: DestinoEjercicio.anatomia(ficha.id)) {
                EtiquetaEnlace(titulo: "Ver en 3D", icono: "figure.arms.open")
            }
            .buttonStyle(.plain)
        }
    }

    private func fila(_ musculo: Musculo, rol: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Circle().fill(color).frame(width: 10, height: 10)
                Text(musculo.nombre).font(.headline)
                Spacer()
                Text(rol).font(.caption).foregroundStyle(Tema.textoSecundario)
            }
            Text(musculo.descripcion).font(.subheadline).foregroundStyle(Tema.textoSecundario)
        }
        .tarjeta()
    }

    private var consejos: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 10) {
                Label("Seguridad", systemImage: "checkmark.shield.fill").font(.headline)
                lista(ficha.seguridad, icono: "checkmark.circle.fill", color: Tema.acento)
            }
            .tarjeta()
        }
    }
}
