import Foundation
import SceneKit

/// Una pieza del personaje: piel de un segmento o capa de un músculo, ya en el sistema de su articulación.
struct ParteMalla: Decodable {
    let nombre: String
    /// «raiz» (la pelvis) o el nombre de una `Articulacion`.
    let junta: String
    /// «piel», «ropa», «calzado», «ojos» o «musculo».
    let rol: String
    let musculo: String?
    let v: Int
    let i: Int
    let o: Int
}

private struct ManifiestoManiqui: Decodable {
    let version: Int
    let partes: [ParteMalla]
}

/// Lee el personaje 3D de Resources/maniqui.json + maniqui.bin (lo genera tools/generar_maniqui.py).
/// Formato del .bin, por pieza y desde `o`: posiciones Float32×3, normales Float32×3 y triángulos UInt32.
enum MallasManiqui {
    private struct Pieza {
        let parte: ParteMalla
        let fuentes: [SCNGeometrySource]
        let elemento: SCNGeometryElement
    }

    /// Se decodifica una sola vez; las fuentes y elementos son inmutables y se comparten entre escenas.
    private static let piezas: [Pieza]? = leer()

    static var disponible: Bool { piezas != nil }

    /// Devuelve cada pieza con una geometría nueva (cada una con su propio material, para teñirla por separado).
    static func geometrias() -> [(parte: ParteMalla, geometria: SCNGeometry)]? {
        piezas?.map { ($0.parte, SCNGeometry(sources: $0.fuentes, elements: [$0.elemento])) }
    }

    private static func leer(bundle: Bundle = .main) -> [Pieza]? {
        guard let urlJSON = bundle.url(forResource: "maniqui", withExtension: "json"),
              let urlBin = bundle.url(forResource: "maniqui", withExtension: "bin"),
              let manifiesto = try? JSONDecoder().decode(ManifiestoManiqui.self, from: Data(contentsOf: urlJSON)),
              let binario = try? Data(contentsOf: urlBin) else { return nil }

        var resultado: [Pieza] = []
        for parte in manifiesto.partes {
            let bytesVertices = parte.v * 12
            let fin = parte.o + bytesVertices * 2 + parte.i * 4
            guard parte.v > 0, parte.i > 0, parte.i % 3 == 0, parte.o >= 0, fin <= binario.count else { return nil }

            let posiciones = binario.subdata(in: parte.o ..< parte.o + bytesVertices)
            let normales = binario.subdata(in: parte.o + bytesVertices ..< parte.o + 2 * bytesVertices)
            let indices = binario.subdata(in: parte.o + 2 * bytesVertices ..< fin)

            let fuentePosiciones = SCNGeometrySource(
                data: posiciones, semantic: .vertex, vectorCount: parte.v, usesFloatComponents: true,
                componentsPerVector: 3, bytesPerComponent: 4, dataOffset: 0, dataStride: 12)
            let fuenteNormales = SCNGeometrySource(
                data: normales, semantic: .normal, vectorCount: parte.v, usesFloatComponents: true,
                componentsPerVector: 3, bytesPerComponent: 4, dataOffset: 0, dataStride: 12)
            let elemento = SCNGeometryElement(
                data: indices, primitiveType: .triangles, primitiveCount: parte.i / 3, bytesPerIndex: 4)
            resultado.append(Pieza(parte: parte, fuentes: [fuentePosiciones, fuenteNormales], elemento: elemento))
        }
        return resultado.isEmpty ? nil : resultado
    }
}
