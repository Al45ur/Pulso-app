import SwiftUI
import SwiftData

struct RaizView: View {
    @Query(filter: #Predicate<Sesion> { $0.fin == nil }, sort: \Sesion.inicio, order: .reverse)
    private var activas: [Sesion]

    var body: some View {
        TabView {
            NavigationStack { RutinasView() }
                .tabItem { Label("Rutinas", systemImage: "dumbbell.fill") }
            NavigationStack { HistorialView() }
                .tabItem { Label("Historial", systemImage: "clock.arrow.circlepath") }
        }
        .tint(Tema.acento)
        .preferredColorScheme(.dark)
        // Si hay un entrenamiento abierto (también si lo inició Siri), se muestra a pantalla completa.
        .fullScreenCover(item: Binding(get: { activas.first }, set: { _ in })) { sesion in
            SesionView(sesion: sesion)
                .tint(Tema.acento)
                .preferredColorScheme(.dark)
        }
    }
}
