#!/usr/bin/env python3
"""Prepara una entrevista para editarla en DaVinci Resolve (versión gratuita o Studio).

A partir de un vídeo (o audio) de entrevista genera, en una carpeta de salida:

  * corte_bruto.fcpxml      Timeline con los silencios largos ya recortados.
                            Resolve: File > Import > Timeline...
  * marcadores.edl          Marcadores de colores (muletillas, repeticiones,
                            candidatos a Short) alineados con ese timeline.
                            Resolve: en el Media Pool, clic derecho en el
                            timeline > Timelines > Import > Timeline Markers
                            from EDL...
  * subtitulos.srt          Subtítulos alineados con el timeline recortado.
  * subtitulos_original.srt Subtítulos alineados con el archivo original.
  * transcripcion.txt       Texto completo con marcas de tiempo.
  * informe.md              Resumen: tiempo ahorrado, muletillas y los mejores
                            momentos candidatos a Shorts/Reels.
  * transcripcion.json      Transcripción de Whisper (para reutilizar con
                            --transcripcion y no volver a transcribir).

Uso básico:
    python resolve/preparar_entrevista.py entrevista.mp4

Más opciones:
    python resolve/preparar_entrevista.py entrevista.mp4 --modelo small --idioma es \\
        --estilo natural --shorts 5
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------

# Estilos de corte. "natural" respeta las pausas reflexivas, que forman parte
# del tono íntimo de una entrevista de desarrollo personal; "dinamico" es para
# piezas cortas (Shorts/Reels) donde el ritmo manda.
ESTILOS = {
    "natural": {"silencio_min": 1.2, "margen": 0.30, "umbral_db": -38},
    "equilibrado": {"silencio_min": 0.8, "margen": 0.20, "umbral_db": -35},
    "dinamico": {"silencio_min": 0.5, "margen": 0.12, "umbral_db": -33},
}

MULETILLAS = {
    "es": ["eh", "ehm", "em", "mmm", "mm", "este", "o sea", "en plan", "sabes",
           "vale", "digamos", "tipo", "bueno", "pues nada"],
    "en": ["uh", "um", "uhm", "erm", "like", "you know", "i mean", "sort of",
           "kind of", "basically", "actually", "literally"],
}
# Palabras que solo son muletilla si van solas o al principio de frase.
MULETILLAS_AMBIGUAS = {"este", "vale", "tipo", "bueno", "sabes", "like", "actually",
                       "basically", "literally"}

# Señales de un buen momento para Short/Reel en contenido de desarrollo
# personal: ganchos, revelaciones, consejos accionables y emoción.
GANCHOS = {
    "es": ["nunca", "nadie", "secreto", "error", "errores", "la clave", "el problema",
           "la verdad", "lo que", "tienes que", "deja de", "si tu", "si tú", "cuando yo",
           "me di cuenta", "cambió mi vida", "lo más importante", "por qué", "porque",
           "el mayor", "la mayoría", "nadie te cuenta", "el día que", "aprendí",
           "consejo", "primero", "paso", "realmente"],
    "en": ["never", "nobody", "secret", "mistake", "the key", "the problem", "the truth",
           "you have to", "stop", "if you", "when i", "i realized", "changed my life",
           "most important", "why", "the biggest", "most people", "learned", "advice"],
}
TEMAS = {
    "es": ["trauma", "miedo", "ansiedad", "autoestima", "emociones", "emoción", "dinero",
           "finanzas", "ahorro", "inversión", "liderazgo", "líder", "relaciones", "pareja",
           "propósito", "hábitos", "hábito", "infancia", "sanar", "culpa", "vergüenza",
           "límites", "éxito", "fracaso", "felicidad", "cerebro", "estrés", "cuerpo",
           "amor", "soledad", "confianza", "voz", "valor"],
    "en": ["trauma", "fear", "anxiety", "self-esteem", "emotions", "money", "finance",
           "invest", "leadership", "leader", "relationship", "purpose", "habits", "childhood",
           "heal", "shame", "guilt", "boundaries", "success", "failure", "happiness", "brain",
           "stress", "love", "lonely", "confidence", "voice", "worth"],
}

COLOR_MULETILLA = "Yellow"
COLOR_REPETICION = "Cream"
COLOR_SHORT = "Purple"


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def localizar_ffmpeg() -> None:
    """Usa el ffmpeg incluido en static-ffmpeg si está instalado; si no, el del sistema."""
    try:
        import static_ffmpeg  # type: ignore

        static_ffmpeg.add_paths()
    except ImportError:
        pass
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("No encuentro ffmpeg/ffprobe. Ejecuta: pip install -r requirements.txt")


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^\w\s'-]", " ", texto).strip()


@dataclass
class Media:
    ruta: Path
    duracion: float
    tiene_video: bool
    fps: Fraction
    ancho: int
    alto: int
    canales_audio: int
    frecuencia_audio: int


def analizar_media(ruta: Path) -> Media:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format",
         str(ruta)],
        capture_output=True, text=True, check=True,
    ).stdout
    info = json.loads(salida)
    video = next((s for s in info["streams"] if s.get("codec_type") == "video"
                  and not s.get("disposition", {}).get("attached_pic")), None)
    audio = next((s for s in info["streams"] if s.get("codec_type") == "audio"), None)
    fps = Fraction(25)
    if video:
        tasa = video.get("avg_frame_rate") or video.get("r_frame_rate") or "25/1"
        if tasa in ("0/0", "0"):
            tasa = video.get("r_frame_rate", "25/1")
        fps = Fraction(tasa).limit_denominator(1001)
    return Media(
        ruta=ruta.resolve(),
        duracion=float(info["format"]["duration"]),
        tiene_video=video is not None,
        fps=fps,
        ancho=int(video["width"]) if video else 1920,
        alto=int(video["height"]) if video else 1080,
        canales_audio=int(audio.get("channels", 2)) if audio else 0,
        frecuencia_audio=int(audio.get("sample_rate", 48000)) if audio else 48000,
    )


# --------------------------------------------------------------------------
# Silencios y tramos que se conservan
# --------------------------------------------------------------------------

def detectar_silencios(ruta: Path, umbral_db: float, minimo: float) -> list[tuple[float, float]]:
    proceso = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(ruta), "-vn",
         "-af", f"silencedetect=noise={umbral_db}dB:d={minimo}", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    silencios, inicio = [], None
    for linea in proceso.stderr.splitlines():
        if m := re.search(r"silence_start: (-?[\d.]+)", linea):
            inicio = max(0.0, float(m.group(1)))
        elif (m := re.search(r"silence_end: ([\d.]+)", linea)) and inicio is not None:
            silencios.append((inicio, float(m.group(1))))
            inicio = None
    if inicio is not None:  # el archivo termina en silencio
        silencios.append((inicio, float("inf")))
    return silencios


def tramos_a_conservar(duracion: float, silencios: list[tuple[float, float]],
                       margen: float, tramo_min: float = 0.4) -> list[tuple[float, float]]:
    tramos, cursor = [], 0.0
    for ini, fin in silencios:
        corte_ini = ini + margen
        corte_fin = min(fin, duracion) - margen
        if corte_fin - corte_ini <= 0.05:
            continue
        if corte_ini > cursor:
            tramos.append((cursor, corte_ini))
        cursor = max(cursor, corte_fin)
    if cursor < duracion:
        tramos.append((cursor, duracion))
    return [t for t in tramos if t[1] - t[0] >= tramo_min] or [(0.0, duracion)]


class Mapa:
    """Convierte tiempos del archivo original a tiempos del timeline recortado (en frames)."""

    def __init__(self, tramos_seg: list[tuple[float, float]], fps: Fraction):
        self.fps = fps
        self.tramos: list[tuple[int, int, int]] = []  # (src_ini, src_fin, tl_ini) en frames
        tl = 0
        for ini, fin in tramos_seg:
            a, b = self.frame(ini), self.frame(fin)
            if b > a:
                self.tramos.append((a, b, tl))
                tl += b - a
        self.total = tl

    def frame(self, segundos: float) -> int:
        return int(round(Fraction(segundos).limit_denominator(100000) * self.fps))

    def a_timeline(self, segundos: float, ajustar: bool = False) -> int | None:
        f = self.frame(segundos)
        for a, b, tl in self.tramos:
            if a <= f < b:
                return tl + f - a
            if ajustar and f < a:  # cae en un silencio recortado: salta al siguiente tramo
                return tl
        return self.total if ajustar else None

    def segundos(self, frames: int) -> float:
        return float(Fraction(frames) / self.fps)


# --------------------------------------------------------------------------
# Transcripción
# --------------------------------------------------------------------------

def transcribir(ruta: Path, modelo: str, idioma: str | None) -> dict:
    try:
        import whisper  # type: ignore
    except ImportError:
        sys.exit("Falta Whisper. Ejecuta: pip install -r requirements.txt")
    print(f"Transcribiendo con Whisper ({modelo})… puede tardar un rato.")
    m = whisper.load_model(modelo)
    return m.transcribe(str(ruta), language=idioma, word_timestamps=True, verbose=False)


def palabras(transcripcion: dict) -> list[dict]:
    lista = []
    for seg in transcripcion.get("segments", []):
        for w in seg.get("words", []) or []:
            lista.append({"texto": w["word"].strip(), "ini": float(w["start"]),
                          "fin": float(w["end"])})
    return lista


def detectar_muletillas(lista: list[dict], idioma: str) -> list[dict]:
    claves = sorted({normalizar(m) for m in MULETILLAS.get(idioma, []) + MULETILLAS["es"]
                     + MULETILLAS["en"]}, key=lambda m: -len(m.split()))
    resultados, i = [], 0
    norm = [normalizar(w["texto"]) for w in lista]
    while i < len(lista):
        encontrado = False
        for clave in claves:
            n = len(clave.split())
            if " ".join(norm[i:i + n]) == clave:
                previo = lista[i - 1]["texto"] if i else "."
                aislada = (previo.endswith((".", ",", "?", "!", "¿"))
                           or lista[i + n - 1]["texto"].endswith((",", ".", "?")))
                if clave not in MULETILLAS_AMBIGUAS or aislada:
                    resultados.append({"tipo": "Muletilla", "texto": clave,
                                       "ini": lista[i]["ini"], "fin": lista[i + n - 1]["fin"]})
                    i += n
                    encontrado = True
                    break
        if not encontrado:
            if (i and norm[i] and norm[i] == norm[i - 1] and len(norm[i]) > 1
                    and lista[i]["ini"] - lista[i - 1]["fin"] < 0.6):
                resultados.append({"tipo": "Repetición", "texto": f"{norm[i]} {norm[i]}",
                                   "ini": lista[i - 1]["ini"], "fin": lista[i]["fin"]})
            i += 1
    return resultados


def candidatos_short(segmentos: list[dict], idioma: str, cantidad: int,
                     dur_min: float = 25, dur_max: float = 60) -> list[dict]:
    """Puntúa ventanas de 25-60 s que empiezan al inicio de una frase.

    Es una heurística (ganchos, temas del canal, preguntas, densidad de habla):
    sirve para no revisar 1 hora de entrevista a ciegas, pero la decisión final
    es tuya.
    """
    ganchos = [normalizar(g) for g in GANCHOS.get(idioma, []) + GANCHOS["es"] + GANCHOS["en"]]
    temas = [normalizar(t) for t in TEMAS.get(idioma, []) + TEMAS["es"] + TEMAS["en"]]
    ventanas = []
    for i, seg in enumerate(segmentos):
        texto_ini = seg["text"].strip()
        if i and not segmentos[i - 1]["text"].strip().endswith((".", "?", "!")):
            continue  # el Short debe empezar en una frase completa
        fin_idx = i
        while (fin_idx + 1 < len(segmentos)
               and segmentos[fin_idx + 1]["end"] - seg["start"] <= dur_max):
            fin_idx += 1
        # termina en el último final de frase dentro del rango
        while fin_idx > i and not segmentos[fin_idx]["text"].strip().endswith((".", "?", "!")):
            fin_idx -= 1
        dur = segmentos[fin_idx]["end"] - seg["start"]
        if dur < dur_min:
            continue
        cuerpo = " ".join(s["text"] for s in segmentos[i:fin_idx + 1])
        n_cuerpo, n_ini = f" {normalizar(cuerpo)} ", f" {normalizar(texto_ini)} "
        puntos = 0.0
        puntos += 3 * sum(f" {g} " in n_ini for g in ganchos)        # gancho en los primeros segundos
        puntos += 2 if "?" in texto_ini else 0                        # empieza con pregunta
        puntos += 1.5 * sum(f" {t} " in n_cuerpo for t in temas)      # temas del canal
        puntos += 0.5 * sum(f" {g} " in n_cuerpo for g in ganchos)
        puntos += min(3.0, len(cuerpo.split()) / max(dur, 1) - 1.5)   # energía (palabras/s)
        puntos += 1 if re.search(r"\d", cuerpo) else 0                # datos concretos
        ventanas.append({"ini": seg["start"], "fin": segmentos[fin_idx]["end"],
                         "puntos": round(puntos, 1), "texto": cuerpo.strip(),
                         "gancho": texto_ini})
    elegidos: list[dict] = []
    for v in sorted(ventanas, key=lambda v: -v["puntos"]):
        if all(v["fin"] <= e["ini"] or v["ini"] >= e["fin"] for e in elegidos):
            elegidos.append(v)
        if len(elegidos) == cantidad:
            break
    return sorted(elegidos, key=lambda v: v["ini"])


# --------------------------------------------------------------------------
# Escritura de archivos
# --------------------------------------------------------------------------

def tc(frames: int, fps: Fraction, separador: str = ":") -> str:
    base = int(round(fps))
    h, resto = divmod(frames, base * 3600)
    m, resto = divmod(resto, base * 60)
    s, f = divmod(resto, base)
    return f"{h:02d}:{m:02d}:{s:02d}{separador}{f:02d}"


def tiempo_srt(segundos: float) -> str:
    ms = int(round(segundos * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def tiempo_corto(segundos: float) -> str:
    s = int(segundos)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def bloques_subtitulos(lista: list[dict], max_chars: int, max_dur: float = 4.0) -> list[dict]:
    bloques, actual = [], []
    for w in lista:
        texto = " ".join(x["texto"] for x in actual + [w])
        if actual and (len(texto) > max_chars or w["fin"] - actual[0]["ini"] > max_dur
                       or w["ini"] - actual[-1]["fin"] > 0.8):
            bloques.append(actual)
            actual = []
        actual.append(w)
        if w["texto"].endswith((".", "?", "!")):
            bloques.append(actual)
            actual = []
    if actual:
        bloques.append(actual)
    return [{"ini": b[0]["ini"], "fin": b[-1]["fin"],
             "texto": " ".join(x["texto"] for x in b).strip()} for b in bloques]


def escribir_srt(destino: Path, bloques: list[dict], mapa: Mapa | None) -> None:
    lineas, n = [], 0
    for b in bloques:
        ini, fin = b["ini"], b["fin"]
        if mapa:
            fi = mapa.a_timeline(ini, ajustar=True)
            ff = mapa.a_timeline(max(ini, fin - 0.01), ajustar=True)
            if fi is None or ff is None or ff <= fi:
                continue
            ini, fin = mapa.segundos(fi), mapa.segundos(ff)
        n += 1
        lineas += [str(n), f"{tiempo_srt(ini)} --> {tiempo_srt(fin)}", b["texto"], ""]
    destino.write_text("\n".join(lineas), encoding="utf-8")


def escribir_edl(destino: Path, marcadores: list[dict], mapa: Mapa, inicio_tc: int,
                 titulo: str) -> int:
    fps = mapa.fps
    lineas = [f"TITLE: {titulo}", "FCM: NON-DROP FRAME", ""]
    n = 0
    for mk in sorted(marcadores, key=lambda m: m["ini"]):
        f_ini = mapa.a_timeline(mk["ini"])
        if f_ini is None:
            continue
        f_fin = mapa.a_timeline(mk["fin"], ajustar=True) or f_ini + 1
        dur = max(1, f_fin - f_ini)
        n += 1
        a, b = tc(inicio_tc + f_ini, fps), tc(inicio_tc + f_ini + 1, fps)
        nombre = mk["nombre"].replace("|", "/")
        lineas.append(f"{n:03d}  001      V     C        {a} {b} {a} {b}  ")
        lineas.append(f" |C:ResolveColor{mk['color']} |M:{nombre} |D:{dur}")
        lineas.append("")
    destino.write_text("\n".join(lineas), encoding="utf-8")
    return n


def escribir_fcpxml(destino: Path, media: Media, mapa: Mapa, inicio_tc: int,
                    nombre_proyecto: str) -> None:
    fd = 1 / media.fps  # duración de un frame en segundos (Fraction)

    def t(frames: int) -> str:
        valor = frames * fd
        return f"{valor.numerator}/{valor.denominator}s" if valor.denominator != 1 else f"{valor.numerator}s"

    total_frames = mapa.frame(media.duracion)
    ruta_posix = media.ruta.as_posix()
    if not ruta_posix.startswith("/"):  # Windows: C:/Users/... -> /C:/Users/...
        ruta_posix = "/" + ruta_posix
    src = "file://" + quote(ruta_posix, safe="/:")
    nombre_clip = escape(media.ruta.stem)
    clips = []
    for a, b, tl in mapa.tramos:
        clips.append(
            f'        <asset-clip ref="r2" name="{nombre_clip}" offset="{t(inicio_tc + tl)}" '
            f'start="{t(a)}" duration="{t(b - a)}" format="r1" tcFormat="NDF"/>'
        )
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.9">
  <resources>
    <format id="r1" frameDuration="{t(1)}" width="{media.ancho}" height="{media.alto}"/>
    <asset id="r2" name="{nombre_clip}" start="0s" duration="{t(total_frames)}" hasVideo="1" format="r1" hasAudio="1" audioSources="1" audioChannels="{max(1, media.canales_audio)}" audioRate="{media.frecuencia_audio}">
      <media-rep kind="original-media" src="{escape(src)}"/>
    </asset>
  </resources>
  <library>
    <event name="Your Own Voice">
      <project name="{escape(nombre_proyecto)}">
        <sequence format="r1" duration="{t(mapa.total)}" tcStart="{t(inicio_tc)}" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
          <spine>
{chr(10).join(clips)}
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
'''
    destino.write_text(xml, encoding="utf-8")


# --------------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path, help="Vídeo o audio de la entrevista")
    p.add_argument("--salida", type=Path, help="Carpeta de salida (por defecto: <archivo>_resolve)")
    p.add_argument("--modelo", default="small", choices=["tiny", "base", "small", "medium", "large",
                                                         "turbo"],
                   help="Modelo de Whisper. 'small' o 'medium' van bien en español (defecto: small)")
    p.add_argument("--idioma", default="es", help="Idioma de la entrevista: es, en… (defecto: es)")
    p.add_argument("--estilo", default="natural", choices=ESTILOS.keys(),
                   help="Cuánto silencio recortar (defecto: natural, respeta las pausas)")
    p.add_argument("--sin-cortes", action="store_true",
                   help="No recortar silencios; solo marcadores, subtítulos e informe")
    p.add_argument("--shorts", type=int, default=6, help="Nº de candidatos a Short (defecto: 6)")
    p.add_argument("--max-caracteres", type=int, default=42,
                   help="Caracteres por subtítulo (42 horizontal; usa ~25 para vertical)")
    p.add_argument("--transcripcion", type=Path,
                   help="Reutilizar un transcripcion.json previo en lugar de volver a transcribir")
    p.add_argument("--inicio-timecode", default="01:00:00:00",
                   help="Timecode de inicio del timeline en Resolve (defecto: 01:00:00:00)")
    args = p.parse_args()

    if not args.archivo.exists():
        sys.exit(f"No existe el archivo: {args.archivo}")
    localizar_ffmpeg()
    salida = args.salida or args.archivo.with_name(args.archivo.stem + "_resolve")
    salida.mkdir(parents=True, exist_ok=True)

    media = analizar_media(args.archivo)
    estilo = ESTILOS[args.estilo]
    print(f"Archivo: {media.ruta.name} · {tiempo_corto(media.duracion)} · "
          f"{float(media.fps):.3f} fps · {media.ancho}x{media.alto}")

    # 1. Silencios
    if args.sin_cortes:
        tramos = [(0.0, media.duracion)]
    else:
        print("Buscando silencios…")
        silencios = detectar_silencios(media.ruta, estilo["umbral_db"], estilo["silencio_min"])
        tramos = tramos_a_conservar(media.duracion, silencios, estilo["margen"])
    mapa = Mapa(tramos, media.fps)

    # 2. Transcripción
    if args.transcripcion:
        transcripcion = json.loads(args.transcripcion.read_text(encoding="utf-8"))
    else:
        transcripcion = transcribir(media.ruta, args.modelo, args.idioma)
        (salida / "transcripcion.json").write_text(
            json.dumps(transcripcion, ensure_ascii=False, indent=1), encoding="utf-8")
    idioma = transcripcion.get("language") or args.idioma
    lista = palabras(transcripcion)
    segmentos = transcripcion.get("segments", [])

    # 3. Análisis
    muletillas = detectar_muletillas(lista, idioma)
    shorts = candidatos_short(segmentos, idioma, args.shorts)

    marcadores = [{"ini": m["ini"], "fin": m["fin"],
                   "color": COLOR_MULETILLA if m["tipo"] == "Muletilla" else COLOR_REPETICION,
                   "nombre": f"{m['tipo']}: {m['texto']}"} for m in muletillas]
    for n, s in enumerate(shorts, 1):
        marcadores.append({"ini": s["ini"], "fin": s["fin"], "color": COLOR_SHORT,
                           "nombre": f"SHORT {n} - {s['gancho'][:60]}"})

    # 4. Archivos
    inicio_tc = sum(int(x) * k for x, k in zip(args.inicio_timecode.split(":"),
                                               (3600 * round(media.fps), 60 * round(media.fps),
                                                round(media.fps), 1)))
    titulo = f"{args.archivo.stem} - corte bruto"
    if media.tiene_video:
        escribir_fcpxml(salida / "corte_bruto.fcpxml", media, mapa, inicio_tc, titulo)
    n_marc = escribir_edl(salida / "marcadores.edl", marcadores, mapa, inicio_tc, titulo)
    bloques = bloques_subtitulos(lista, args.max_caracteres)
    escribir_srt(salida / "subtitulos.srt", bloques, mapa)
    escribir_srt(salida / "subtitulos_original.srt", bloques, None)
    (salida / "transcripcion.txt").write_text(
        "\n".join(f"[{tiempo_corto(s['start'])}] {s['text'].strip()}" for s in segmentos),
        encoding="utf-8")

    ahorro = media.duracion - mapa.segundos(mapa.total)
    informe = [
        f"# {args.archivo.stem} — preparación para DaVinci Resolve", "",
        f"- Duración original: **{tiempo_corto(media.duracion)}**",
        f"- Duración tras recortar silencios (estilo *{args.estilo}*): "
        f"**{tiempo_corto(mapa.segundos(mapa.total))}** (−{tiempo_corto(ahorro)}, "
        f"{len(mapa.tramos)} tramos)",
        f"- Muletillas/repeticiones marcadas en amarillo/crema: **{len(muletillas)}**",
        f"- Marcadores escritos en la EDL: **{n_marc}**", "",
        "## Candidatos a Short / Reel (marcadores morados)", "",
        "Tiempos del **archivo original** y del **timeline recortado**. "
        "La puntuación es orientativa: escucha cada uno y quédate con los que "
        "transmitan una idea completa con tu voz.", "",
    ]
    for n, s in enumerate(shorts, 1):
        tl = mapa.a_timeline(s["ini"], ajustar=True) or 0
        informe += [
            f"### SHORT {n} · {tiempo_corto(s['ini'])}–{tiempo_corto(s['fin'])} "
            f"({round(s['fin'] - s['ini'])} s) · timeline {tc(inicio_tc + tl, media.fps)} · "
            f"puntos {s['puntos']}", "",
            f"**Gancho:** {s['gancho']}", "", f"> {s['texto']}", "",
        ]
    contador: dict[str, int] = {}
    for m in muletillas:
        contador[m["texto"]] = contador.get(m["texto"], 0) + 1
    if contador:
        informe += ["## Muletillas más frecuentes", ""]
        informe += [f"- «{k}»: {v}" for k, v in sorted(contador.items(), key=lambda x: -x[1])[:10]]
        informe += ["", "_Whisper tiende a omitir sonidos como «eh» o «mmm», así que el "
                        "recuento real suele ser mayor._", ""]
    (salida / "informe.md").write_text("\n".join(informe), encoding="utf-8")

    print(f"\nListo en: {salida}")
    print(f"  Recortado {tiempo_corto(ahorro)} de silencios · {len(muletillas)} muletillas · "
          f"{len(shorts)} candidatos a Short")
    print("  Siguiente paso en Resolve: File > Import > Timeline… > corte_bruto.fcpxml")


if __name__ == "__main__":
    main()
