import Foundation

enum RolMuscular {
    case principal, secundario, ninguno
}

/// Músculos que la app sabe dibujar y explicar. El `rawValue` es el identificador usado en ejercicios.json.
enum Musculo: String, CaseIterable, Identifiable, Decodable {
    case triceps, biceps, deltoides, pectorales, dorsales, trapecio, lumbar, abdomen
    case gluteos, cuadriceps, isquiotibiales, gemelos, antebrazos, aductores

    var id: String { rawValue }

    var nombre: String {
        switch self {
        case .triceps: return "Tríceps"
        case .biceps: return "Bíceps"
        case .deltoides: return "Deltoides"
        case .pectorales: return "Pectorales"
        case .dorsales: return "Dorsales"
        case .trapecio: return "Trapecio"
        case .lumbar: return "Zona lumbar"
        case .abdomen: return "Abdomen"
        case .gluteos: return "Glúteos"
        case .cuadriceps: return "Cuádriceps"
        case .isquiotibiales: return "Isquiotibiales"
        case .gemelos: return "Gemelos"
        case .antebrazos: return "Antebrazos"
        case .aductores: return "Aductores"
        }
    }

    /// Explicación breve y general. Es material educativo, no una medición.
    var descripcion: String {
        switch self {
        case .triceps:
            return "Tríceps braquial. Ocupa la parte posterior del brazo y extiende el codo. Tiene tres cabezas (larga, lateral y medial); la larga también cruza el hombro."
        case .biceps:
            return "Bíceps braquial. Parte frontal del brazo; flexiona el codo y gira el antebrazo."
        case .deltoides:
            return "Deltoides. Cubre el hombro y levanta el brazo en distintas direcciones."
        case .pectorales:
            return "Pectorales. Músculos del pecho; acercan el brazo al cuerpo y lo empujan hacia delante."
        case .dorsales:
            return "Dorsal ancho. Zona amplia de la espalda; lleva el brazo hacia abajo y hacia atrás."
        case .trapecio:
            return "Trapecio. Entre el cuello, los hombros y la espalda media; mueve y estabiliza los omóplatos."
        case .lumbar:
            return "Erectores espinales de la zona lumbar. Mantienen la columna extendida y estable, por ejemplo al inclinar el torso con carga."
        case .abdomen:
            return "Abdomen. Estabiliza el tronco y flexiona la columna."
        case .gluteos:
            return "Glúteos. El glúteo mayor es el principal extensor de la cadera, por ejemplo al subir en un peso muerto."
        case .cuadriceps:
            return "Cuádriceps. Parte frontal del muslo; extiende la rodilla."
        case .isquiotibiales:
            return "Isquiotibiales (bíceps femoral, semitendinoso y semimembranoso). Parte posterior del muslo; extienden la cadera y flexionan la rodilla."
        case .gemelos:
            return "Gemelos. Pantorrilla; empujan el pie hacia abajo."
        case .antebrazos:
            return "Antebrazos. Mueven la muñeca y los dedos y sostienen el agarre."
        case .aductores:
            return "Aductores. Parte interna del muslo; acercan la pierna al cuerpo. El aductor mayor también ayuda a extender la cadera."
        }
    }
}

enum TextosAnatomia {
    static let aviso = "Visualización educativa: marca los músculos asociados al ejercicio. No mide la activación real ni es una valoración médica."
}
