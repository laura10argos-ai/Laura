"""Your Own Voice · 3 · Exportar capítulos de YouTube desde marcadores azules

Pon un marcador AZUL al inicio de cada bloque temático y escribe el título
del capítulo en su nombre. Este script genera el texto listo para pegar en la
descripción de YouTube (y en las notas del episodio de Spotify) y lo guarda
en el Escritorio.

Reglas de YouTube que comprueba: el primer capítulo empieza en 0:00, hay al
menos 3 capítulos y cada uno dura 10 segundos o más.

Ejecutar desde DaVinci Resolve: Workspace > Scripts > YOV_3_Exportar_Capitulos_YouTube
"""
import os
import re

COLOR = "Blue"


def obtener_resolve():
    try:
        return resolve  # noqa: F821
    except NameError:
        pass
    try:
        return bmd.scriptapp("Resolve")  # noqa: F821
    except NameError:
        import DaVinciResolveScript as dvr
        return dvr.scriptapp("Resolve")


def formato(segundos, largo):
    s = int(segundos)
    if largo:
        return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"
    return f"{s // 60}:{s % 60:02d}"


def main():
    r = obtener_resolve()
    proyecto = r.GetProjectManager().GetCurrentProject()
    tl = proyecto.GetCurrentTimeline() if proyecto else None
    if not tl:
        print("Abre el timeline final antes de ejecutar este script.")
        return
    fps_txt = tl.GetSetting("timelineFrameRate") or proyecto.GetSetting("timelineFrameRate")
    fps = float(re.search(r"[\d.]+", str(fps_txt)).group())
    duracion = (tl.GetEndFrame() - tl.GetStartFrame()) / fps

    capitulos = sorted(
        (int(f) / fps, (m.get("name") or "").strip() or "Capítulo")
        for f, m in (tl.GetMarkers() or {}).items() if m.get("color") == COLOR
    )
    if not capitulos or capitulos[0][0] >= 1:
        capitulos.insert(0, (0.0, "Introducción"))
    else:
        capitulos[0] = (0.0, capitulos[0][1])

    avisos = []
    if len(capitulos) < 3:
        avisos.append("YouTube necesita al menos 3 capítulos.")
    limites = [c[0] for c in capitulos] + [duracion]
    for i, (t, titulo) in enumerate(capitulos):
        if limites[i + 1] - t < 10:
            avisos.append(f"«{titulo}» dura menos de 10 s; YouTube podría ignorar los capítulos.")

    largo = duracion >= 3600
    lineas = [f"{formato(t, largo)} {titulo}" for t, titulo in capitulos]
    texto = "\n".join(lineas)

    carpeta = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(carpeta):
        carpeta = os.path.expanduser("~")
    nombre = re.sub(r'[\\/:*?"<>|]', "_", tl.GetName())
    ruta = os.path.join(carpeta, f"{nombre} - capitulos YouTube.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto + "\n")

    print("Capítulos (copia y pega en la descripción):\n")
    print(texto)
    print("\nGuardado en:", ruta)
    for a in avisos:
        print("AVISO:", a)


main()
