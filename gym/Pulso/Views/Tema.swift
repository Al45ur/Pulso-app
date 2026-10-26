import SwiftUI

/// Estilo de la imagen de referencia: azul marino muy oscuro, tarjetas negro-azuladas con borde fino,
/// verde neón para acciones y selección, rojo/naranja solo para músculos y errores de técnica.
enum Tema {
    static let acento = Color(red: 0.18, green: 0.95, blue: 0.62)
    static let fondo = Color(red: 0.03, green: 0.07, blue: 0.12)
    static let tarjeta = Color(red: 0.04, green: 0.09, blue: 0.15)
    static let borde = Color(red: 0.11, green: 0.22, blue: 0.33)
    static let textoSecundario = Color(red: 0.56, green: 0.65, blue: 0.75)
    static let principal = Color(red: 1.0, green: 0.25, blue: 0.20)
    static let secundario = Color(red: 1.0, green: 0.60, blue: 0.15)
}

extension View {
    func tarjeta() -> some View {
        padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Tema.tarjeta, in: RoundedRectangle(cornerRadius: 16))
            .overlay(RoundedRectangle(cornerRadius: 16).stroke(Tema.borde, lineWidth: 1))
    }
}

/// Botón principal: verde neón con texto oscuro (el blanco sobre verde neón no se lee bien).
struct BotonPrimario: ButtonStyle {
    @Environment(\.isEnabled) private var habilitado

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundStyle(Tema.fondo)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(Tema.acento.opacity(habilitado ? (configuration.isPressed ? 0.8 : 1) : 0.35),
                        in: RoundedRectangle(cornerRadius: 14))
    }
}

/// Botón secundario: borde verde y texto verde.
struct BotonSecundario: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.subheadline.bold())
            .foregroundStyle(Tema.acento)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(Tema.tarjeta.opacity(configuration.isPressed ? 0.6 : 1), in: RoundedRectangle(cornerRadius: 14))
            .overlay(RoundedRectangle(cornerRadius: 14).stroke(Tema.acento.opacity(0.7), lineWidth: 1))
    }
}

/// Contenido de un `NavigationLink` con aspecto de botón principal o secundario.
struct EtiquetaEnlace: View {
    let titulo: String
    let icono: String
    var principal = false

    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: icono)
            Text(titulo)
        }
        .font(principal ? .headline : .subheadline.bold())
        .foregroundStyle(principal ? Tema.fondo : Tema.acento)
        .frame(maxWidth: .infinity)
        .padding(.vertical, principal ? 14 : 12)
        .background(principal ? Tema.acento : Tema.tarjeta, in: RoundedRectangle(cornerRadius: 14))
        .overlay(RoundedRectangle(cornerRadius: 14).stroke(Tema.acento.opacity(principal ? 0 : 0.7), lineWidth: 1))
    }
}

func formatoPeso(_ kg: Double) -> String {
    kg.formatted(.number.precision(.fractionLength(0...1)))
}

extension Musculo {
    func color(en ficha: FichaEjercicio?) -> Color {
        switch ficha?.rol(de: self) ?? .ninguno {
        case .principal: return Tema.principal
        case .secundario: return Tema.secundario
        case .ninguno: return Tema.textoSecundario
        }
    }
}

// MARK: - Componentes compartidos

struct LeyendaMusculos: View {
    var body: some View {
        HStack(spacing: 14) {
            item(Tema.principal, "Principal")
            item(Tema.secundario, "Secundario")
            item(Tema.textoSecundario, "Sin relación")
        }
        .font(.caption)
    }

    private func item(_ color: Color, _ texto: String) -> some View {
        HStack(spacing: 5) {
            Circle().fill(color).frame(width: 9, height: 9)
            Text(texto).foregroundStyle(Tema.textoSecundario)
        }
    }
}

struct ChipMusculo: View {
    let musculo: Musculo
    let color: Color

    var body: some View {
        HStack(spacing: 6) {
            Circle().fill(color).frame(width: 8, height: 8)
            Text(musculo.nombre).font(.caption.bold())
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(Tema.tarjeta, in: Capsule())
        .overlay(Capsule().stroke(Tema.borde, lineWidth: 1))
    }
}

/// Muestra los músculos de un ejercicio como chips, rojos los principales y naranjas los secundarios.
struct ChipsMusculosEjercicio: View {
    let ficha: FichaEjercicio

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack {
                ForEach(ficha.musculosPrincipales) { ChipMusculo(musculo: $0, color: Tema.principal) }
                ForEach(ficha.musculosSecundarios) { ChipMusculo(musculo: $0, color: Tema.secundario) }
            }
        }
    }
}

struct TarjetaPendientes: View {
    let notas: [String]

    var body: some View {
        if !notas.isEmpty {
            VStack(alignment: .leading, spacing: 6) {
                Label("Pendiente de validar", systemImage: "questionmark.circle")
                    .font(.caption.bold()).foregroundStyle(Tema.secundario)
                ForEach(Array(notas.enumerated()), id: \.offset) { _, nota in
                    Text("• \(nota)").font(.caption).foregroundStyle(Tema.textoSecundario)
                }
            }
            .tarjeta()
        }
    }
}

struct TarjetaError: View {
    let mensaje: String

    var body: some View {
        Label(mensaje, systemImage: "exclamationmark.triangle.fill")
            .font(.subheadline)
            .foregroundStyle(Tema.principal)
            .tarjeta()
    }
}

/// Editor de series, repeticiones y descanso. Usado en la ficha y en el resumen.
struct EditorConfigEjercicio: View {
    @Binding var config: ConfigEjercicio

    var body: some View {
        VStack(spacing: 10) {
            Stepper(value: $config.series, in: 1...10) {
                fila("Series", "\(config.series)")
            }
            Stepper(value: $config.repsMin, in: 1...config.repsMax) {
                fila("Repeticiones mín.", "\(config.repsMin)")
            }
            Stepper(value: $config.repsMax, in: config.repsMin...50) {
                fila("Repeticiones máx.", "\(config.repsMax)")
            }
            Stepper(value: $config.descansoSeg, in: 15...300, step: 15) {
                fila("Descanso", "\(config.descansoSeg) s")
            }
        }
        .tarjeta()
    }

    private func fila(_ titulo: String, _ valor: String) -> some View {
        HStack {
            Text(titulo).foregroundStyle(Tema.textoSecundario)
            Spacer()
            Text(valor).bold().monospacedDigit()
        }
    }
}
