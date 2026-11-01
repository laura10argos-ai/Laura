"""Your Own Voice · 4 · Limpiar marcadores de revisión

Cuando ya has revisado las muletillas y repeticiones, borra los marcadores
amarillos (Yellow) y crema (Cream) del timeline actual. Conserva los azules
(capítulos) y los morados (Shorts).

Ejecutar desde DaVinci Resolve: Workspace > Scripts > YOV_4_Limpiar_Marcadores_Revision
"""

COLORES = ["Yellow", "Cream"]


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


def main():
    proyecto = obtener_resolve().GetProjectManager().GetCurrentProject()
    tl = proyecto.GetCurrentTimeline() if proyecto else None
    if not tl:
        print("Abre un timeline antes de ejecutar este script.")
        return
    antes = len(tl.GetMarkers() or {})
    for color in COLORES:
        tl.DeleteMarkersByColor(color)
    print(f"Marcadores borrados: {antes - len(tl.GetMarkers() or {})}")


main()
