import SwiftUI
import SwiftData

struct HistorialView: View {
    @Environment(\.modelContext) private var contexto
    @Query(filter: #Predicate<Sesion> { $0.fin != nil }, sort: \Sesion.inicio, order: .reverse)
    private var terminadas: [Sesion]

    /// Una sesión cerrada sin series (se abrió y se cerró sin entrenar) no aporta nada.
    private var sesiones: [Sesion] { terminadas.filter { !$0.series.isEmpty } }

    var body: some View {
        List {
            if sesiones.isEmpty {
                Text("Todavía no has terminado ningún entrenamiento.").foregroundStyle(.secondary)
            }
            ForEach(sesiones) { sesion in
                NavigationLink {
                    HistorialDetalleView(sesion: sesion)
                } label: {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(sesion.rutina?.nombre ?? "Entrenamiento").font(.headline)
                        Text(sesion.inicio.formatted(date: .abbreviated, time: .shortened))
                            .font(.subheadline).foregroundStyle(.secondary)
                        Text("\(sesion.series.count) series · \(Int(sesion.volumenKg.rounded())) kg de volumen")
                            .font(.caption).foregroundStyle(Tema.acento)
                    }
                }
            }
            .onDelete(perform: borrar)
        }
        .scrollContentBackground(.hidden)
        .background(Tema.fondo)
        .navigationTitle("Historial")
    }

    private func borrar(en posiciones: IndexSet) {
        let lista = sesiones
        for posicion in posiciones { contexto.delete(lista[posicion]) }
        try? contexto.save()
    }
}

struct HistorialDetalleView: View {
    let sesion: Sesion

    var body: some View {
        List {
            ForEach(Array(sesion.planOrdenado.enumerated()), id: \.offset) { indice, plan in
                let series = sesion.seriesRegistradas(enEjercicio: indice)
                if !series.isEmpty {
                    Section(plan.nombre) {
                        ForEach(series) { serie in
                            HStack {
                                Text("Serie \(serie.numero)").foregroundStyle(.secondary)
                                Spacer()
                                Text("\(formatoPeso(serie.pesoKg)) kg × \(serie.repeticiones)").bold()
                            }
                        }
                    }
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(Tema.fondo)
        .navigationTitle(sesion.inicio.formatted(date: .abbreviated, time: .omitted))
        .navigationBarTitleDisplayMode(.inline)
    }
}
