import SwiftUI
import SwiftData

struct SesionView: View {
    @Environment(\.modelContext) private var contexto
    let sesion: Sesion

    @State private var descanso = TemporizadorDescanso()
    @State private var peso: Double = 0
    @State private var reps: Int = 10
    @State private var mensajeError: String?
    @State private var confirmandoFin = false
    @FocusState private var pesoEnfocado: Bool

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    if let plan = sesion.ejercicioActual {
                        cabecera(plan)
                        seriesHechas(plan)
                        controles(plan)
                        if descanso.activo { tarjetaDescanso }
                        navegacion
                    } else {
                        Text("Esta rutina no tiene ejercicios.").tarjeta()
                    }
                }
                .padding()
            }
            .background(Tema.fondo)
            .navigationTitle(sesion.rutina?.nombre ?? "Entrenamiento")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Text(sesion.inicio, style: .timer)
                        .monospacedDigit().foregroundStyle(.secondary)
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Terminar") { confirmandoFin = true }
                }
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Listo") { pesoEnfocado = false }
                }
            }
            .confirmationDialog("¿Terminar el entrenamiento?", isPresented: $confirmandoFin, titleVisibility: .visible) {
                Button("Terminar", role: .destructive) {
                    EntrenamientoService.terminar(sesion, en: contexto)
                }
                Button("Seguir entrenando", role: .cancel) {}
            }
        }
        .onAppear(perform: prepararValores)
        .onChange(of: sesion.indiceEjercicio) { _, _ in prepararValores() }
        .sensoryFeedback(.success, trigger: sesion.series.count)
    }

    // MARK: - Secciones

    private func cabecera(_ plan: EjercicioPlan) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Ejercicio \(sesion.indiceEjercicio + 1) de \(sesion.planOrdenado.count)")
                .font(.caption.bold()).foregroundStyle(Tema.acento)
            Text(plan.nombre).font(.title2.bold())
            Text("Objetivo: \(plan.objetivo) · descanso \(plan.descansoSeg) s")
                .font(.subheadline).foregroundStyle(.secondary)
            if let ejercicio = plan.ejercicio {
                DisclosureGroup("Cómo hacerlo") {
                    VStack(alignment: .leading, spacing: 6) {
                        ForEach(Array(ejercicio.pasos.enumerated()), id: \.offset) { _, paso in
                            Text("• \(paso)").font(.footnote)
                        }
                    }
                    .padding(.top, 4)
                }
            }
        }
        .tarjeta()
    }

    private func seriesHechas(_ plan: EjercicioPlan) -> some View {
        let hechas = sesion.seriesRegistradas(enEjercicio: sesion.indiceEjercicio)
        return VStack(alignment: .leading, spacing: 8) {
            Text("Series: \(hechas.count) de \(plan.series)").font(.headline)
            if hechas.isEmpty {
                Text("Aún no registras ninguna serie.").font(.subheadline).foregroundStyle(.secondary)
            }
            ForEach(hechas) { serie in
                HStack {
                    Text("Serie \(serie.numero)").foregroundStyle(.secondary)
                    Spacer()
                    Text("\(formatoPeso(serie.pesoKg)) kg × \(serie.repeticiones)").bold()
                }
            }
        }
        .tarjeta()
    }

    private func controles(_ plan: EjercicioPlan) -> some View {
        VStack(spacing: 12) {
            HStack {
                Text("Peso").font(.headline)
                Spacer()
                Button { peso = max(0, peso - 2.5) } label: { Image(systemName: "minus.circle.fill") }
                TextField("kg", value: $peso, format: .number)
                    .keyboardType(.decimalPad)
                    .multilineTextAlignment(.center)
                    .frame(width: 72)
                    .textFieldStyle(.roundedBorder)
                    .focused($pesoEnfocado)
                Button { peso += 2.5 } label: { Image(systemName: "plus.circle.fill") }
                Text("kg").foregroundStyle(.secondary)
            }
            .font(.title2)
            Stepper(value: $reps, in: 1...100) {
                Text("\(reps) repeticiones").font(.headline)
            }
            Button(action: registrar) {
                Text("Registrar serie")
            }
            .buttonStyle(BotonPrimario())
            if let mensajeError {
                Text(mensajeError).font(.footnote).foregroundStyle(.red)
            }
        }
        .tarjeta()
    }

    private var tarjetaDescanso: some View {
        TimelineView(.periodic(from: .now, by: 1)) { reloj in
            let restantes = descanso.restantes(en: reloj.date)
            VStack(spacing: 8) {
                if restantes > 0 {
                    Text("Descanso").font(.subheadline).foregroundStyle(.secondary)
                    Text(TemporizadorDescanso.formato(restantes))
                        .font(.system(size: 44, weight: .bold, design: .rounded))
                        .monospacedDigit()
                } else {
                    Text("¡Listo para la siguiente serie!").font(.headline)
                }
                Button(restantes > 0 ? "Omitir descanso" : "Cerrar") { descanso.detener() }
                    .font(.subheadline)
            }
            .frame(maxWidth: .infinity)
            .tarjeta()
        }
    }

    private var navegacion: some View {
        HStack {
            Button { mover(-1) } label: {
                HStack { Image(systemName: "chevron.left"); Text("Anterior") }
            }
            .disabled(sesion.indiceEjercicio == 0)
            Spacer()
            Button { mover(1) } label: {
                HStack { Text("Siguiente"); Image(systemName: "chevron.right") }
            }
            .disabled(sesion.indiceEjercicio + 1 >= sesion.planOrdenado.count)
        }
        .padding(.horizontal)
    }

    // MARK: - Acciones

    private func registrar() {
        pesoEnfocado = false
        do {
            let resumen = try EntrenamientoService.registrarSerie(
                en: sesion, contexto: contexto, repeticiones: reps, pesoKg: peso)
            mensajeError = nil
            if resumen.completoEjercicio { descanso.detener() } else { descanso.iniciar(segundos: resumen.descansoSeg) }
        } catch {
            mensajeError = errorLegible(error)
        }
    }

    private func mover(_ paso: Int) {
        do {
            if paso > 0 {
                try EntrenamientoService.siguienteEjercicio(en: sesion, contexto: contexto)
            } else {
                try EntrenamientoService.ejercicioAnterior(en: sesion, contexto: contexto)
            }
            descanso.detener()
            mensajeError = nil
        } catch {
            mensajeError = errorLegible(error)
        }
    }

    /// Valores de partida: la última serie del ejercicio o, si no hay, el máximo de repeticiones del objetivo.
    private func prepararValores() {
        guard let plan = sesion.ejercicioActual else { return }
        if let ultima = sesion.seriesRegistradas(enEjercicio: sesion.indiceEjercicio).last {
            peso = ultima.pesoKg
            reps = ultima.repeticiones
        } else {
            peso = 0
            reps = plan.repsMax
        }
    }

    private func errorLegible(_ error: Error) -> String {
        if let propio = error as? EntrenamientoError {
            return String(localized: propio.localizedStringResource)
        }
        return error.localizedDescription
    }
}
