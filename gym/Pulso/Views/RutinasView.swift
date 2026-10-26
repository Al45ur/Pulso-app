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
                            Text(rutina.detalle).font(.subheadline).foregroundStyle(.secondary)
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
        .navigationTitle("Pulso")
    }
}

struct RutinaDetalleView: View {
    @Environment(\.modelContext) private var contexto
    let rutina: Rutina

    var body: some View {
        ScrollView {
            VStack(spacing: 12) {
                ForEach(rutina.planOrdenado) { plan in
                    if let ejercicio = plan.ejercicio {
                        NavigationLink {
                            EjercicioDetalleView(ejercicio: ejercicio)
                        } label: {
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(plan.nombre).font(.headline)
                                    Text("\(plan.objetivo) · descanso \(plan.descansoSeg) s")
                                        .font(.subheadline).foregroundStyle(.secondary)
                                }
                                Spacer()
                                Image(systemName: "chevron.right").foregroundStyle(.secondary)
                            }
                            .foregroundStyle(.primary)
                            .tarjeta()
                        }
                    }
                }
                Text("Series, repeticiones y descansos son valores sugeridos (3–4 × 8–12 para crecimiento); ajústalos a tu nivel.")
                    .font(.footnote).foregroundStyle(.secondary)
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle(rutina.nombre)
        .safeAreaInset(edge: .bottom) {
            Button {
                EntrenamientoService.iniciar(rutina, en: contexto)
            } label: {
                Text("Iniciar entrenamiento").font(.headline).frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .padding()
            .background(.ultraThinMaterial)
        }
    }
}

struct EjercicioDetalleView: View {
    let ejercicio: Ejercicio

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(ejercicio.equipo).font(.subheadline).foregroundStyle(.secondary)
                    Text("Énfasis: \(ejercicio.enfasis)").font(.subheadline.bold()).foregroundStyle(Tema.acento)
                }
                .tarjeta()

                bloque("Cómo hacerlo", items: ejercicio.pasos, icono: "checkmark.circle.fill")
                bloque("Errores comunes", items: ejercicio.errores, icono: "exclamationmark.triangle.fill")
            }
            .padding()
        }
        .background(Tema.fondo)
        .navigationTitle(ejercicio.nombre)
        .navigationBarTitleDisplayMode(.inline)
    }

    private func bloque(_ titulo: String, items: [String], icono: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(titulo).font(.headline)
            ForEach(Array(items.enumerated()), id: \.offset) { _, texto in
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: icono).foregroundStyle(Tema.acento)
                    Text(texto)
                }
            }
        }
        .tarjeta()
    }
}
