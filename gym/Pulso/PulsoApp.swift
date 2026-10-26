import SwiftUI
import SwiftData

@main
struct PulsoApp: App {
    var body: some Scene {
        WindowGroup {
            RaizView()
        }
        .modelContainer(Persistencia.contenedor)
    }
}
