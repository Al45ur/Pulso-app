import SwiftUI

/// Pantalla 1: catálogo de ejercicios con búsqueda y filtros por categoría.
struct CatalogoView: View {
    @State private var busqueda = ""
    @State private var categoria: String?

    private var catalogo: CatalogoEjercicios { .compartido }

    private var filtradas: [FichaEjercicio] {
        catalogo.fichas.filter { ficha in
            let coincideCategoria = categoria == nil || ficha.categoria == categoria
            let coincideBusqueda = busqueda.isEmpty
                || ficha.nombre.localizedCaseInsensitiveContains(busqueda)
                || ficha.musculosPrincipales.contains { $0.nombre.localizedCaseInsensitiveContains(busqueda) }
            return coincideCategoria && coincideBusqueda
        }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                if let error = catalogo.error {
                    TarjetaError(mensaje: error)
                }
                filtros
                HStack {
                    Text(categoria ?? "Todos los ejercicios").font(.title3.bold())
                    Spacer()
                    Text("\(filtradas.count) ejercicios").font(.caption).foregroundStyle(Tema.textoSecundario)
                }
                if filtradas.isEmpty && catalogo.error == nil {
                    Text("Ningún ejercicio coincide con la búsqueda.")
                        .foregroundStyle(Tema.textoSecundario).tarjeta()
                }
                ForEach(filtradas) { ficha in
                    NavigationLink(value: DestinoEjercicio.detalle(ficha.id)) {
                        fila(ficha)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle("Ejercicios")
        .searchable(text: $busqueda, prompt: "Buscar ejercicio o músculo")
    }

    /// Solo se ofrecen las categorías que tienen ejercicios: no se muestran filtros vacíos.
    private var filtros: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                chip("Todos", seleccionado: categoria == nil) { categoria = nil }
                ForEach(catalogo.categorias, id: \.self) { nombre in
                    chip(nombre, seleccionado: categoria == nombre) { categoria = nombre }
                }
            }
        }
    }

    private func chip(_ titulo: String, seleccionado: Bool, accion: @escaping () -> Void) -> some View {
        Button(action: accion) {
            Text(titulo)
                .font(.subheadline.bold())
                .foregroundStyle(seleccionado ? Tema.fondo : Tema.textoSecundario)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(seleccionado ? Tema.acento : Tema.tarjeta, in: Capsule())
                .overlay(Capsule().stroke(Tema.borde, lineWidth: seleccionado ? 0 : 1))
        }
        .buttonStyle(.plain)
    }

    private func fila(_ ficha: FichaEjercicio) -> some View {
        HStack(spacing: 12) {
            MiniaturaView(ficha: ficha)
            VStack(alignment: .leading, spacing: 4) {
                Text(ficha.nombre).font(.headline).multilineTextAlignment(.leading)
                Text("\(ficha.categoria) · \(ficha.etiquetaMusculos)")
                    .font(.caption).foregroundStyle(Tema.textoSecundario)
                    .multilineTextAlignment(.leading)
            }
            .foregroundStyle(.primary)
            Spacer()
            Image(systemName: "chevron.right").foregroundStyle(Tema.textoSecundario)
        }
        .padding(10)
        .background(Tema.tarjeta, in: RoundedRectangle(cornerRadius: 16))
        .overlay(RoundedRectangle(cornerRadius: 16).stroke(Tema.borde, lineWidth: 1))
    }
}

/// Raíz de la pestaña Ejercicios.
struct EjerciciosRaiz: View {
    var body: some View {
        NavigationStack {
            CatalogoView().conDestinosEjercicio()
        }
    }
}
