import SwiftUI
import SwiftData

struct RutinasView: View {
    @Query(sort: \Rutina.nombre) private var rutinas: [Rutina]

    var body: some View {
        ScrollView {
            VStack(spacing: 12) {
                ForEach(rutinas) { rutina in
                    NavigationLink {
                        RutinaDetalleView(rutina: rutina)
                    } label: {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(rutina.nombre).font(.title2.bold())
                            Text(rutina.detalle).font(.subheadline).foregroundStyle(Tema.textoSecundario)
                            Text("\(rutina.plan.count) ejercicios")
                                .font(.caption.bold()).foregroundStyle(Tema.acento)
                        }
                        .foregroundStyle(.primary)
                        .multilineTextAlignment(.leading)
                        .tarjeta()
                    }
                }
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle("Rutinas")
    }
}

struct RutinaDetalleView: View {
    @Environment(\.modelContext) private var contexto
    let rutina: Rutina

    var body: some View {
        ScrollView {
            VStack(spacing: 12) {
                if rutina.plan.isEmpty {
                    Text("Esta rutina está vacía. Añade ejercicios desde la pestaña Ejercicios, con «Añadir a mi rutina».")
                        .foregroundStyle(Tema.textoSecundario)
                        .tarjeta()
                }
                ForEach(rutina.planOrdenado) { plan in
                    if let ejercicio = plan.ejercicio {
                        enlace(plan, ejercicio)
                    }
                }
                Text("Series, repeticiones y descansos son valores sugeridos (3–4 × 8–12 para crecimiento); ajústalos a tu nivel.")
                    .font(.footnote).foregroundStyle(Tema.textoSecundario)
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle(rutina.nombre)
        .safeAreaInset(edge: .bottom) {
            Button {
                EntrenamientoService.iniciar(rutina, en: contexto)
            } label: {
                Text("Iniciar entrenamiento")
            }
            .buttonStyle(BotonPrimario())
            .disabled(rutina.plan.isEmpty)
            .padding()
            .background(.ultraThinMaterial)
        }
    }

    /// Los ejercicios del catálogo abren su ficha 3D; los que no vienen del catálogo, la ficha de texto.
    @ViewBuilder
    private func enlace(_ plan: EjercicioPlan, _ ejercicio: Ejercicio) -> some View {
        if ejercicio.fichaID.isEmpty {
            NavigationLink {
                EjercicioDetalleView(ejercicio: ejercicio)
            } label: {
                fila(plan)
            }
        } else {
            NavigationLink(value: DestinoEjercicio.detalle(ejercicio.fichaID)) {
                fila(plan)
            }
        }
    }

    private func fila(_ plan: EjercicioPlan) -> some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(plan.nombre).font(.headline)
                Text("\(plan.objetivo) · descanso \(plan.descansoSeg) s")
                    .font(.subheadline).foregroundStyle(Tema.textoSecundario)
            }
            Spacer()
            Image(systemName: "chevron.right").foregroundStyle(Tema.textoSecundario)
        }
        .foregroundStyle(.primary)
        .multilineTextAlignment(.leading)
        .tarjeta()
    }
}

/// Ficha de texto para ejercicios que no vienen del catálogo.
struct EjercicioDetalleView: View {
    let ejercicio: Ejercicio

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(ejercicio.equipo).font(.subheadline).foregroundStyle(Tema.textoSecundario)
                    Text("Énfasis: \(ejercicio.enfasis)").font(.subheadline.bold()).foregroundStyle(Tema.acento)
                }
                .tarjeta()

                bloque("Cómo hacerlo", items: ejercicio.pasos, icono: "checkmark.circle.fill", color: Tema.acento)
                bloque("Errores comunes", items: ejercicio.errores, icono: "exclamationmark.triangle.fill", color: Tema.principal)
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle(ejercicio.nombre)
        .navigationBarTitleDisplayMode(.inline)
    }

    private func bloque(_ titulo: String, items: [String], icono: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(titulo).font(.headline)
            ForEach(Array(items.enumerated()), id: \.offset) { _, texto in
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: icono).foregroundStyle(color)
                    Text(texto)
                }
            }
        }
        .tarjeta()
    }
}
