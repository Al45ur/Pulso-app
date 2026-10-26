import SwiftUI

/// Estilo tomado del reel: fondo casi negro y acento rojo-naranja (el color del músculo resaltado).
enum Tema {
    static let acento = Color(red: 1.0, green: 0.28, blue: 0.22)
    static let fondo = Color(white: 0.07)
    static let tarjeta = Color(white: 0.13)
}

extension View {
    func tarjeta() -> some View {
        padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Tema.tarjeta, in: RoundedRectangle(cornerRadius: 16))
    }
}

func formatoPeso(_ kg: Double) -> String {
    kg.formatted(.number.precision(.fractionLength(0...1)))
}
