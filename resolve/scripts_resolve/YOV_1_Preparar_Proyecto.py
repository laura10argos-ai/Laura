"""Your Own Voice · 1 · Preparar proyecto de entrevista

Crea la estructura de carpetas (bins) estándar del canal en el proyecto abierto.
Es seguro ejecutarlo varias veces: solo crea lo que falta.

Ejecutar desde DaVinci Resolve: Workspace > Scripts > YOV_1_Preparar_Proyecto
"""

CARPETAS = [
    "01 Cámaras entrevista",
    "02 Audio (micros)",
    "03 B-roll",
    "04 Música y efectos",
    "05 Marca (logo, intro, rótulos)",
    "06 Subtítulos",
    "07 Timelines largo (16x9)",
    "08 Shorts y Reels (9x16)",
    "09 Miniaturas (fotogramas)",
]


def obtener_resolve():
    try:
        return resolve  # noqa: F821  (Resolve lo define al lanzar desde Workspace > Scripts)
    except NameError:
        pass
    try:
        return bmd.scriptapp("Resolve")  # noqa: F821
    except NameError:
        import DaVinciResolveScript as dvr  # scripting externo (solo Resolve Studio)
        return dvr.scriptapp("Resolve")


def main():
    r = obtener_resolve()
    proyecto = r.GetProjectManager().GetCurrentProject()
    if not proyecto:
        print("Abre o crea un proyecto antes de ejecutar este script.")
        return
    pool = proyecto.GetMediaPool()
    raiz = pool.GetRootFolder()
    existentes = {c.GetName() for c in (raiz.GetSubFolderList() or [])}
    creadas = []
    for nombre in CARPETAS:
        if nombre not in existentes:
            if pool.AddSubFolder(raiz, nombre):
                creadas.append(nombre)
    pool.SetCurrentFolder(raiz)
    print("Proyecto:", proyecto.GetName())
    print("Carpetas creadas:", ", ".join(creadas) if creadas else "ninguna (ya existían)")
    print("Siguiente paso: importa el corte_bruto.fcpxml (File > Import > Timeline...)")


main()
