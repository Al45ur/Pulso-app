import SwiftUI

/// Las pantallas de un ejercicio. Todas reciben solo el identificador de la ficha,
/// así el ejercicio elegido se mantiene al pasar de la ficha a la animación, la anatomía, etc.
enum DestinoEjercicio: Hashable {
    case detalle(String)
    case animacion(String, fase: Int)
    case anatomia(String)
    case tecnica(String)
    case mapa(String)
    case guia(String)
    case resumen(String)
}

extension View {
    /// Registra el destino de navegación de ejercicios. Se aplica a la raíz de cada NavigationStack.
    func conDestinosEjercicio() -> some View {
        navigationDestination(for: DestinoEjercicio.self) { destino in
            PantallaDestino(destino: destino)
        }
    }
}

private struct PantallaDestino: View {
    let destino: DestinoEjercicio

    var body: some View {
        switch destino {
        case .detalle(let id):
            conFicha(id) { DetalleEjercicioView(ficha: $0) }
        case .animacion(let id, let fase):
            conFicha(id) { AnimacionView(ficha: $0, faseInicial: fase) }
        case .anatomia(let id):
            conFicha(id) { AnatomiaView(ficha: $0) }
        case .tecnica(let id):
            conFicha(id) { TecnicaView(ficha: $0) }
        case .mapa(let id):
            conFicha(id) { MapaMusculosView(ficha: $0) }
        case .guia(let id):
            conFicha(id) { GuiaPasoView(ficha: $0) }
        case .resumen(let id):
            conFicha(id) { ResumenView(ficha: $0) }
        }
    }

    @ViewBuilder
    private func conFicha<Contenido: View>(_ id: String,
                                           @ViewBuilder _ contenido: (FichaEjercicio) -> Contenido) -> some View {
        if let ficha = CatalogoEjercicios.compartido.ficha(id: id) {
            contenido(ficha)
        } else {
            VStack {
                TarjetaError(mensaje: "No se encontró el ejercicio «\(id)» en el catálogo.")
                Spacer()
            }
            .padding()
            .background(Tema.fondo)
        }
    }
}
