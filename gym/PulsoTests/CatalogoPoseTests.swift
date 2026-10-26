import XCTest
import SwiftData
import SceneKit
@testable import Pulso

@MainActor
final class CatalogoPoseTests: XCTestCase {
    private var contenedor: ModelContainer?

    private func nuevoContexto() throws -> ModelContext {
        let esquema = Schema([Ejercicio.self, EjercicioPlan.self, Rutina.self, Sesion.self, SerieRegistrada.self])
        let nuevo = try ModelContainer(for: esquema, configurations: ModelConfiguration(isStoredInMemoryOnly: true))
        contenedor = nuevo
        DatosIniciales.sembrar(en: nuevo.mainContext)
        return nuevo.mainContext
    }

    private func ficha(_ id: String) throws -> FichaEjercicio {
        try XCTUnwrap(CatalogoEjercicios.compartido.ficha(id: id), "Falta la ficha \(id)")
    }

    private func igual(_ a: Pose, _ b: Pose, accuracy: Double = 1e-9, file: StaticString = #filePath, line: UInt = #line) {
        XCTAssertEqual(a.pitch, b.pitch, accuracy: accuracy, file: file, line: line)
        for i in 0..<3 { XCTAssertEqual(a.posicion[i], b.posicion[i], accuracy: accuracy, file: file, line: line) }
        for j in Articulacion.allCases {
            XCTAssertEqual(a.angulos(j).flexion, b.angulos(j).flexion, accuracy: accuracy, "\(j)", file: file, line: line)
            XCTAssertEqual(a.angulos(j).abduccion, b.angulos(j).abduccion, accuracy: accuracy, "\(j)", file: file, line: line)
            XCTAssertEqual(a.angulos(j).rotacion, b.angulos(j).rotacion, accuracy: accuracy, "\(j)", file: file, line: line)
        }
    }

    // MARK: - Catálogo

    func testElCatalogoCargaYEsValido() {
        let catalogo = CatalogoEjercicios.compartido
        XCTAssertNil(catalogo.error)
        XCTAssertEqual(catalogo.fichas.count, 7)
        XCTAssertEqual(Set(catalogo.fichas.map(\.id)).count, catalogo.fichas.count)
        XCTAssertEqual(catalogo.categorias, ["Tríceps", "Piernas", "Hombros"])
    }

    func testElPesoMuertoRumanoNoEsDeTriceps() throws {
        let rdl = try ficha("peso-muerto-rumano-mancuernas")
        XCTAssertEqual(rdl.categoria, "Piernas")
        XCTAssertEqual(rdl.principales, [.isquiotibiales, .gluteos])
        XCTAssertFalse(rdl.principales.contains(.triceps) || rdl.secundarios.contains(.triceps))
        XCTAssertEqual(rdl.rol(de: .lumbar), .secundario)
        XCTAssertEqual(rdl.rol(de: .biceps), .ninguno)
    }

    func testLaElevacionLateralTrabajaElDeltoidesYNoElTriceps() throws {
        let ficha = try ficha("elevacion-lateral-polea-una-mano")
        XCTAssertEqual(ficha.categoria, "Hombros")
        XCTAssertEqual(ficha.principales, [.deltoidesLateral])
        XCTAssertEqual(ficha.secundarios, [.deltoidesAnterior, .trapecio])
        XCTAssertEqual(ficha.fases.count, 3)
        // El brazo derecho sube: abducción creciente de la primera a la última fase.
        let abducciones = ficha.fases.map { $0.pose.angulos(.hombroD).abduccion }
        XCTAssertEqual(abducciones, abducciones.sorted())
        XCTAssertGreaterThan(abducciones.last ?? 0, 80)
    }

    func testElPressDeHombrosTrabajaElDeltoidesAnteriorYUsaElGiroDelHombro() throws {
        let ficha = try ficha("press-hombros-mancuernas-banco-inclinado")
        XCTAssertEqual(ficha.categoria, "Hombros")
        XCTAssertEqual(ficha.principales, [.deltoidesAnterior])
        XCTAssertEqual(ficha.secundarios, [.triceps, .pectorales])
        XCTAssertTrue(ficha.props.contains { $0.tipo == "bancoInclinado" && $0.angulo == 65 })
        // El hombro del press incluye rotación externa al empezar (tercer valor de la articulación).
        XCTAssertEqual(ficha.fases[0].pose.angulos(.hombroI).rotacion, 20, accuracy: 1e-9)
        // El press y la elevación lateral no marcan las mismas cabezas del deltoides como principales.
        let lateral = try self.ficha("elevacion-lateral-polea-una-mano")
        XCTAssertTrue(ficha.principales.isDisjoint(with: lateral.principales))
    }

    func testLaRotacionDelHombroSeDecodificaYSeInterpola() throws {
        let json = #"{"raiz":{"pos":[0,0.9,0]},"art":{"hombroI":[10,20,30]}}"#
        let pose = try JSONDecoder().decode(Pose.self, from: Data(json.utf8))
        XCTAssertEqual(pose.angulos(.hombroI), Angulos(flexion: 10, abduccion: 20, rotacion: 30))
        let medio = Pose.mezclar(pose, .neutra, t: 0.5)
        XCTAssertEqual(medio.angulos(.hombroI).rotacion, 15, accuracy: 1e-9)
        let invalida = #"{"raiz":{"pos":[0,0.9,0]},"art":{"hombroI":[1,2,3,4]}}"#
        XCTAssertThrowsError(try JSONDecoder().decode(Pose.self, from: Data(invalida.utf8)))
    }

    func testTodosLosEjerciciosDeTricepsTrabajanElTriceps() {
        for ficha in CatalogoEjercicios.compartido.fichas where ficha.categoria == "Tríceps" {
            XCTAssertEqual(ficha.principales, [.triceps], ficha.id)
            XCTAssertEqual(ficha.fases.count, 3, ficha.id)
        }
    }

    func testValidarRechazaUnEjercicioSinMusculosPrincipales() throws {
        let json = """
        {"id":"x","nombre":"X","categoria":"C","equipo":"E","musculosPrincipales":[],"musculosSecundarios":[],
         "descripcion":"d","pasos":[],"errores":[],"seguridad":[],"series":3,"repsMin":8,"repsMax":12,"descansoSeg":60,
         "props":[],"camara":{"azimut":0,"altura":1,"distancia":3,"objetivoY":1},"faseMiniatura":0,
         "fases":[{"nombre":"a","descripcion":"","pose":{"raiz":{"pos":[0,0.9,0]}}},
                  {"nombre":"b","descripcion":"","pose":{"raiz":{"pos":[0,0.9,0]}}}],
         "pendienteValidacion":[]}
        """
        let ficha = try JSONDecoder().decode(FichaEjercicio.self, from: Data(json.utf8))
        XCTAssertThrowsError(try CatalogoEjercicios.validar([ficha]))
    }

    func testUnaArticulacionDesconocidaFallaAlDecodificar() {
        let json = #"{"raiz":{"pos":[0,0.9,0]},"art":{"codoCentral":[10]}}"#
        XCTAssertThrowsError(try JSONDecoder().decode(Pose.self, from: Data(json.utf8)))
    }

    // MARK: - Poses y animación

    func testMezclarEnLosExtremosYEnElPuntoMedio() {
        let a = Pose(posicion: [0, 1, 0], pitch: 0, articulaciones: [.codoI: Angulos(flexion: 100)])
        let b = Pose(posicion: [0, 0, 2], pitch: -90, articulaciones: [.codoI: Angulos(flexion: 0)])
        igual(Pose.mezclar(a, b, t: 0), a)
        igual(Pose.mezclar(a, b, t: 1), b)
        let medio = Pose.mezclar(a, b, t: 0.5)
        XCTAssertEqual(medio.posicion, [0, 0.5, 1])
        XCTAssertEqual(medio.pitch, -45, accuracy: 1e-9)
        XCTAssertEqual(medio.angulos(.codoI).flexion, 50, accuracy: 1e-9)
        XCTAssertEqual(Pose.suavizar(0), 0)
        XCTAssertEqual(Pose.suavizar(1), 1)
        XCTAssertEqual(Pose.suavizar(0.5), 0.5, accuracy: 1e-9)
    }

    func testLaLineaDeTiempoPasaPorCadaFaseYVuelveAlInicio() throws {
        let ficha = try ficha("jalon-triceps-barra-recta")
        let linea = ficha.lineaTiempo
        for (indice, fase) in ficha.fases.enumerated() {
            igual(linea.pose(en: linea.tiempo(deFase: indice)), fase.pose, accuracy: 1e-9)
            XCTAssertEqual(linea.faseCercana(a: linea.tiempo(deFase: indice)), indice)
        }
        igual(linea.pose(en: linea.duracion), ficha.fases[0].pose, accuracy: 1e-9)
        igual(linea.pose(en: -linea.segundosPorTramo * 3), ficha.fases[0].pose, accuracy: 1e-9)
    }

    func testElReproductorSoloAvanzaMientrasReproduce() throws {
        let reproductor = ReproductorAnimacion(linea: try ficha("jalon-triceps-barra-recta").lineaTiempo)
        reproductor.avanzar(1)
        XCTAssertEqual(reproductor.tiempo, 0)

        reproductor.reproduciendo = true
        reproductor.velocidad = 2
        reproductor.avanzar(0.5)
        XCTAssertEqual(reproductor.tiempo, 1, accuracy: 1e-9)

        reproductor.irAFase(2)
        XCTAssertFalse(reproductor.reproduciendo)
        XCTAssertEqual(reproductor.faseActual, 2)

        reproductor.progreso = 0.5
        XCTAssertEqual(reproductor.tiempo, reproductor.linea.duracion / 2, accuracy: 1e-9)
        reproductor.reiniciar()
        XCTAssertEqual(reproductor.tiempo, 0)
    }

    // MARK: - Maniquí 3D

    func testElManiquiTieneVolumenParaTodosLosMusculosDelCatalogo() {
        let disponibles = Maniqui().musculosDisponibles
        for ficha in CatalogoEjercicios.compartido.fichas {
            for musculo in ficha.principales.union(ficha.secundarios) {
                XCTAssertTrue(disponibles.contains(musculo), "\(ficha.id) usa \(musculo) sin volumen 3D")
            }
        }
    }

    /// Las posiciones esperadas salen de tools/verificar_poses.py, que replica la misma cinemática.
    /// Si esta prueba falla, la cinemática de Maniqui.swift y la del verificador se han desincronizado.
    func testLaCinematicaDeSceneKitCoincideConElVerificador() throws {
        let esperado: [(id: String, fase: Int, x: Float, y: Float, z: Float)] = [
            ("jalon-triceps-barra-recta", 0, 0.190, 1.119, 0.387),
            ("jalon-triceps-barra-recta", 2, 0.190, 0.785, 0.121),
            ("extension-triceps-acostado-barra", 0, 0.190, 1.083, -0.527),
            ("extension-triceps-acostado-barra", 2, 0.190, 0.694, -0.799),
            ("extension-triceps-sobre-cabeza-cuerda", 0, 0.179, 1.616, -0.043),
            ("extension-triceps-sobre-cabeza-cuerda", 2, 0.137, 1.933, 0.371),
            ("peso-muerto-rumano-mancuernas", 1, 0.190, 0.696, 0.158),
            ("peso-muerto-rumano-mancuernas", 2, 0.190, 0.377, 0.233),
            ("elevacion-lateral-polea-una-mano", 2, 0.274, 0.798, 0.054),
            ("press-hombros-mancuernas-banco-inclinado", 0, 0.400, 1.142, 0.039),
            ("press-hombros-mancuernas-banco-inclinado", 1, 0.432, 1.337, -0.173),
            ("press-hombros-mancuernas-banco-inclinado", 2, 0.274, 1.540, -0.221)
        ]
        let maniqui = Maniqui()
        for caso in esperado {
            maniqui.aplicar(try ficha(caso.id).fases[caso.fase].pose)
            let mano = maniqui.manoI.simdWorldPosition
            XCTAssertEqual(mano.x, caso.x, accuracy: 0.005, "\(caso.id) fase \(caso.fase) x")
            XCTAssertEqual(mano.y, caso.y, accuracy: 0.005, "\(caso.id) fase \(caso.fase) y")
            XCTAssertEqual(mano.z, caso.z, accuracy: 0.005, "\(caso.id) fase \(caso.fase) z")
        }
    }

    func testElManiquiUsaElPersonajeDeMallasYApoyaEnElSuelo() throws {
        XCTAssertTrue(MallasManiqui.disponible, "Faltan maniqui.json/maniqui.bin: ejecuta tools/generar_maniqui.py")
        let maniqui = Maniqui()
        XCTAssertTrue(maniqui.usaMalla)

        maniqui.aplicar(.neutra)
        for nombre in ["pie_I", "pie_D"] {
            let pie = try XCTUnwrap(maniqui.raiz.childNode(withName: nombre, recursively: true))
            let (minimo, _) = pie.boundingBox
            let suelo = pie.simdConvertPosition(SIMD3<Float>(minimo.x, minimo.y, minimo.z), to: nil)
            XCTAssertEqual(suelo.y, 0, accuracy: 0.01, "\(nombre) debe apoyar en el suelo")
        }
        // Cada músculo del lado izquierdo y del derecho debe poder resaltarse.
        XCTAssertEqual(maniqui.musculosDisponibles, Set(Musculo.allCases))
    }

    func testLaEscenaSeConfiguraParaCadaEjercicio() {
        let escena = EscenaEntrenamiento()
        for ficha in CatalogoEjercicios.compartido.fichas {
            escena.configurar(ficha: ficha)
            for fase in ficha.fases { escena.mostrar(fase.pose) }
            escena.configurarAnatomia(ficha: ficha, vista: .posterior)
            XCTAssertNotNil(escena.camara.camera)
        }
    }

    func testElAspectoPielMuestraSoloLosMusculosMarcadosYAnatomiaTodos() throws {
        let rdl = try ficha("peso-muerto-rumano-mancuernas")
        let maniqui = Maniqui()
        func nodosMusculo(_ musculo: Musculo) -> [SCNNode] {
            var nodos: [SCNNode] = []
            maniqui.raiz.enumerateHierarchy { nodo, _ in if nodo.name == "musculo:" + musculo.rawValue { nodos.append(nodo) } }
            return nodos
        }
        let short = try XCTUnwrap(maniqui.raiz.childNode(withName: "short_pelvis", recursively: true))
        let pie = try XCTUnwrap(maniqui.raiz.childNode(withName: "pie_I", recursively: true))

        maniqui.resaltar(principales: rdl.principales, secundarios: rdl.secundarios, aspecto: .piel)
        XCTAssertTrue(nodosMusculo(.gluteos).allSatisfy { !$0.isHidden }, "el músculo marcado se ve")
        XCTAssertTrue(nodosMusculo(.biceps).allSatisfy(\.isHidden), "un músculo sin relación no se dibuja sobre la piel")
        XCTAssertFalse(short.isHidden)
        XCTAssertLessThan(try XCTUnwrap(short.geometry?.firstMaterial).transparency, 0.5, "el short se aclara si el glúteo está bajo la prenda")

        maniqui.resaltar(principales: [.triceps], secundarios: [], aspecto: .piel)
        XCTAssertEqual(try XCTUnwrap(short.geometry?.firstMaterial).transparency, 1, accuracy: 0.001)

        maniqui.resaltar(principales: [], secundarios: [], seleccionado: .biceps, aspecto: .anatomia)
        XCTAssertTrue(Musculo.allCases.allSatisfy { m in nodosMusculo(m).allSatisfy { !$0.isHidden } }, "en anatomía se ven todos")
        XCTAssertTrue(short.isHidden && pie.isHidden, "en anatomía no hay ropa ni calzado")
    }

    func testElMapaDelCuerpoRelacionaCadaMusculoConSusEjercicios() throws {
        let catalogo = CatalogoEjercicios.compartido
        let triceps = catalogo.ejercicios(para: .triceps)
        XCTAssertEqual(triceps.principal.count, 4)
        XCTAssertTrue(triceps.secundario.contains { $0.id == "press-hombros-mancuernas-banco-inclinado" })
        XCTAssertTrue(catalogo.ejercicios(para: .biceps).principal.isEmpty, "un músculo sin ejercicios es una brecha visible")
        for ficha in catalogo.fichas {
            for musculo in ficha.principales {
                XCTAssertTrue(catalogo.ejercicios(para: musculo).principal.contains(ficha), "\(ficha.id) debe aparecer en \(musculo)")
            }
        }
    }

    // MARK: - Rutinas

    func testAgregarYQuitarEjerciciosDeMiRutina() throws {
        let contexto = try nuevoContexto()
        let rdl = try ficha("peso-muerto-rumano-mancuernas")
        let jalon = try ficha("jalon-triceps-barra-recta")
        XCTAssertFalse(RutinaUsuarioService.contiene(rdl, en: contexto))

        let config = ConfigEjercicio(series: 4, repsMin: 6, repsMax: 10, descansoSeg: 120)
        let plan = RutinaUsuarioService.agregar(rdl, config: config, en: contexto)
        XCTAssertEqual(plan.series, 4)
        XCTAssertEqual(plan.descansoSeg, 120)
        XCTAssertTrue(RutinaUsuarioService.contiene(rdl, en: contexto))

        // El jalón ya existía como Ejercicio por la rutina de Tríceps: se reutiliza, no se duplica.
        RutinaUsuarioService.agregar(jalon, config: .sugerida(jalon), en: contexto)
        XCTAssertEqual(try contexto.fetchCount(FetchDescriptor<Ejercicio>()), 5)
        let mia = try XCTUnwrap(RutinaUsuarioService.buscarRutina(en: contexto))
        XCTAssertEqual(mia.planOrdenado.map(\.nombre), [rdl.nombre, jalon.nombre])

        // Añadir otra vez solo actualiza la configuración.
        RutinaUsuarioService.agregar(rdl, config: ConfigEjercicio(series: 5, repsMin: 5, repsMax: 8, descansoSeg: 150), en: contexto)
        XCTAssertEqual(mia.plan.count, 2)
        XCTAssertEqual(mia.planOrdenado.first?.series, 5)

        RutinaUsuarioService.quitar(rdl, en: contexto)
        XCTAssertFalse(RutinaUsuarioService.contiene(rdl, en: contexto))
        XCTAssertEqual(mia.planOrdenado.map(\.nombre), [jalon.nombre])
        XCTAssertEqual(mia.planOrdenado.map(\.orden), [0])
    }

    func testLaConfiguracionSeGuardaPorEjercicio() throws {
        let defaults = try XCTUnwrap(UserDefaults(suiteName: "PulsoTests.\(UUID().uuidString)"))
        let rdl = try ficha("peso-muerto-rumano-mancuernas")
        XCTAssertEqual(ConfigEjercicio.cargar(rdl, defaults: defaults), .sugerida(rdl))

        let elegida = ConfigEjercicio(series: 5, repsMin: 4, repsMax: 6, descansoSeg: 180)
        elegida.guardar(rdl, defaults: defaults)
        XCTAssertEqual(ConfigEjercicio.cargar(rdl, defaults: defaults), elegida)

        let invalida = ConfigEjercicio(series: 0, repsMin: 10, repsMax: 5, descansoSeg: 60)
        XCTAssertFalse(invalida.esValida)
        invalida.guardar(rdl, defaults: defaults)
        XCTAssertEqual(ConfigEjercicio.cargar(rdl, defaults: defaults), elegida)
    }
}
