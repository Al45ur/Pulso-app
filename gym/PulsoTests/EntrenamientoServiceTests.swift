import XCTest
import SwiftData
@testable import Pulso

@MainActor
final class EntrenamientoServiceTests: XCTestCase {
    // El contenedor debe vivir tanto como el contexto: si se libera, el contexto falla.
    private var contenedor: ModelContainer?

    private func nuevoContexto(sembrar: Bool = true) throws -> ModelContext {
        let esquema = Schema([Ejercicio.self, EjercicioPlan.self, Rutina.self, Sesion.self, SerieRegistrada.self])
        let configuracion = ModelConfiguration(isStoredInMemoryOnly: true)
        let nuevo = try ModelContainer(for: esquema, configurations: configuracion)
        contenedor = nuevo
        if sembrar { DatosIniciales.sembrar(en: nuevo.mainContext) }
        return nuevo.mainContext
    }

    private func rutinaTriceps(_ contexto: ModelContext) throws -> Rutina {
        try XCTUnwrap(try contexto.fetch(FetchDescriptor<Rutina>()).first)
    }

    func testSiembraLaRutinaDeTricepsConCuatroEjerciciosEnOrden() throws {
        let contexto = try nuevoContexto()
        let rutina = try rutinaTriceps(contexto)
        XCTAssertEqual(rutina.nombre, "Tríceps")
        XCTAssertEqual(rutina.planOrdenado.map(\.orden), [0, 1, 2, 3])
        XCTAssertEqual(rutina.planOrdenado.first?.nombre, "Jalón de tríceps con barra recta")
        XCTAssertEqual(rutina.planOrdenado.last?.nombre, "Jalón de tríceps a una mano")
    }

    func testSembrarDosVecesNoDuplicaDatos() throws {
        let contexto = try nuevoContexto()
        DatosIniciales.sembrar(en: contexto)
        XCTAssertEqual(try contexto.fetchCount(FetchDescriptor<Rutina>()), 1)
        XCTAssertEqual(try contexto.fetchCount(FetchDescriptor<Ejercicio>()), 4)
    }

    func testIniciarCreaSesionActivaYRepetirDevuelveLaMisma() throws {
        let contexto = try nuevoContexto()
        let rutina = try rutinaTriceps(contexto)
        XCTAssertNil(EntrenamientoService.sesionActiva(en: contexto))

        let primera = EntrenamientoService.iniciar(rutina, en: contexto)
        let segunda = EntrenamientoService.iniciar(rutina, en: contexto)
        XCTAssertTrue(primera === segunda)
        XCTAssertEqual(try contexto.fetchCount(FetchDescriptor<Sesion>()), 1)
        XCTAssertEqual(primera.indiceEjercicio, 0)
    }

    func testIniciarOtraRutinaCierraLaActiva() throws {
        let contexto = try nuevoContexto()
        let triceps = try rutinaTriceps(contexto)
        let otra = Rutina(nombre: "Otra", detalle: "")
        contexto.insert(otra)

        let primera = EntrenamientoService.iniciar(triceps, en: contexto)
        let segunda = EntrenamientoService.iniciar(otra, en: contexto)
        XCTAssertNotNil(primera.fin)
        XCTAssertNil(segunda.fin)
        XCTAssertTrue(EntrenamientoService.sesionActiva(en: contexto) === segunda)
    }

    func testRegistrarSerieNumeraYDevuelveResumen() throws {
        let contexto = try nuevoContexto()
        let sesion = EntrenamientoService.iniciar(try rutinaTriceps(contexto), en: contexto)

        let uno = try EntrenamientoService.registrarSerie(en: sesion, contexto: contexto, repeticiones: 10, pesoKg: 25)
        let dos = try EntrenamientoService.registrarSerie(en: sesion, contexto: contexto, repeticiones: 9, pesoKg: 25)
        XCTAssertEqual(uno.numero, 1)
        XCTAssertEqual(dos.numero, 2)
        XCTAssertEqual(dos.seriesObjetivo, 3)
        XCTAssertFalse(dos.completoEjercicio)

        let tres = try EntrenamientoService.registrarSerie(en: sesion, contexto: contexto, repeticiones: 8, pesoKg: 27.5)
        XCTAssertTrue(tres.completoEjercicio)
        XCTAssertEqual(sesion.seriesRegistradas(enEjercicio: 0).map(\.repeticiones), [10, 9, 8])
        XCTAssertEqual(sesion.volumenKg, 10 * 25 + 9 * 25 + 8 * 27.5, accuracy: 0.001)
    }

    func testRegistrarSerieRechazaValoresInvalidos() throws {
        let contexto = try nuevoContexto()
        let sesion = EntrenamientoService.iniciar(try rutinaTriceps(contexto), en: contexto)

        for (reps, peso) in [(0, 10.0), (101, 10.0), (10, -1.0), (10, 501.0), (10, Double.nan)] {
            XCTAssertThrowsError(
                try EntrenamientoService.registrarSerie(en: sesion, contexto: contexto, repeticiones: reps, pesoKg: peso)
            ) { XCTAssertEqual($0 as? EntrenamientoError, .valorInvalido) }
        }
        XCTAssertTrue(sesion.series.isEmpty)
    }

    func testLasSeriesSeContabilizanPorEjercicio() throws {
        let contexto = try nuevoContexto()
        let sesion = EntrenamientoService.iniciar(try rutinaTriceps(contexto), en: contexto)

        try EntrenamientoService.registrarSerie(en: sesion, contexto: contexto, repeticiones: 10, pesoKg: 20)
        try EntrenamientoService.siguienteEjercicio(en: sesion, contexto: contexto)
        let resumen = try EntrenamientoService.registrarSerie(en: sesion, contexto: contexto, repeticiones: 8, pesoKg: 30)

        XCTAssertEqual(resumen.numero, 1)
        XCTAssertEqual(resumen.ejercicio, "Extensión de tríceps acostado con barra")
        XCTAssertEqual(sesion.seriesRegistradas(enEjercicio: 0).count, 1)
        XCTAssertEqual(sesion.seriesRegistradas(enEjercicio: 1).count, 1)
    }

    func testNavegacionEntreEjerciciosRespetaLosLimites() throws {
        let contexto = try nuevoContexto()
        let sesion = EntrenamientoService.iniciar(try rutinaTriceps(contexto), en: contexto)

        XCTAssertThrowsError(try EntrenamientoService.ejercicioAnterior(en: sesion, contexto: contexto)) {
            XCTAssertEqual($0 as? EntrenamientoError, .primerEjercicio)
        }
        for _ in 0..<3 { try EntrenamientoService.siguienteEjercicio(en: sesion, contexto: contexto) }
        XCTAssertEqual(sesion.indiceEjercicio, 3)
        XCTAssertThrowsError(try EntrenamientoService.siguienteEjercicio(en: sesion, contexto: contexto)) {
            XCTAssertEqual($0 as? EntrenamientoError, .ultimoEjercicio)
        }
        XCTAssertEqual(sesion.indiceEjercicio, 3)
    }

    func testTerminarCierraLaSesion() throws {
        let contexto = try nuevoContexto()
        let sesion = EntrenamientoService.iniciar(try rutinaTriceps(contexto), en: contexto)
        try EntrenamientoService.registrarSerie(en: sesion, contexto: contexto, repeticiones: 10, pesoKg: 20)

        EntrenamientoService.terminar(sesion, en: contexto)
        XCTAssertNotNil(sesion.fin)
        XCTAssertNil(EntrenamientoService.sesionActiva(en: contexto))
        XCTAssertThrowsError(try EntrenamientoService.requerirSesionActiva(en: contexto)) {
            XCTAssertEqual($0 as? EntrenamientoError, .sinSesionActiva)
        }
    }

    func testTemporizadorDescanso() {
        let temporizador = TemporizadorDescanso()
        let inicio = Date(timeIntervalSince1970: 1_000)
        XCTAssertFalse(temporizador.activo)
        XCTAssertEqual(temporizador.restantes(en: inicio), 0)

        temporizador.iniciar(segundos: 90, desde: inicio)
        XCTAssertTrue(temporizador.activo)
        XCTAssertEqual(temporizador.restantes(en: inicio), 90)
        XCTAssertEqual(temporizador.restantes(en: inicio.addingTimeInterval(30.4)), 60)
        XCTAssertEqual(temporizador.restantes(en: inicio.addingTimeInterval(500)), 0)
        XCTAssertEqual(TemporizadorDescanso.formato(90), "1:30")
        XCTAssertEqual(TemporizadorDescanso.formato(5), "0:05")

        temporizador.detener()
        XCTAssertFalse(temporizador.activo)
    }
}
