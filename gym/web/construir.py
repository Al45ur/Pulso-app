#!/usr/bin/env python3
"""Genera gym/web/pulso-gym.html: la versión web de la app, con el personaje y los ejercicios incrustados.

Lee Pulso/Resources/{maniqui.json, maniqui.bin, ejercicios.json}, así que la web y la app nativa comparten datos.
Uso:  python3 gym/web/construir.py
"""
import base64
import json
from pathlib import Path

aqui = Path(__file__).resolve().parent
recursos = aqui.parent / "Pulso" / "Resources"
datos = {
    "manifiesto": json.loads((recursos / "maniqui.json").read_text()),
    "bin": base64.b64encode((recursos / "maniqui.bin").read_bytes()).decode(),
    "ejercicios": json.loads((recursos / "ejercicios.json").read_text())["ejercicios"],
}
carga = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = (aqui / "plantilla.html").read_text().replace("__DATOS__", carga)
(aqui / "pulso-gym.html").write_text(html)
print(f"pulso-gym.html: {len(html) / 1e6:.2f} MB")
