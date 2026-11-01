"""Your Own Voice · 2 · Crear Shorts/Reels desde marcadores morados

Para cada marcador MORADO con duración del timeline actual crea un timeline
vertical 1080x1920 con ese fragmento, ya ampliado para llenar la pantalla.
Después solo tienes que ajustar el encuadre (Inspector > Transform > Position)
para centrar a quien habla, añadir subtítulos grandes y tu gancho en texto.

Cómo marcar un Short a mano: coloca el cabezal al inicio, pulsa M, haz doble
clic en el marcador, elige color Purple y escribe la duración (o arrastra el
marcador con Alt/Option para alargarlo). Los marcadores morados que genera
preparar_entrevista.py ya vienen con su duración.

Ejecutar desde DaVinci Resolve: Workspace > Scripts > YOV_2_Crear_Shorts
"""

COLOR = "Purple"
ANCHO, ALTO = 1080, 1920
CARPETA = "08 Shorts y Reels (9x16)"


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


def inicio_fuente(item):
    """Frame de la media donde empieza este clip del timeline."""
    if hasattr(item, "GetSourceStartFrame"):
        valor = item.GetSourceStartFrame()
        if isinstance(valor, (int, float)):
            return int(valor)
    return int(item.GetLeftOffset())


def tramos(timeline, tipo, a, b):
    """Fragmentos de cada pista que caen entre los frames a y b del timeline."""
    resultado = []
    for pista in range(1, int(timeline.GetTrackCount(tipo)) + 1):
        if timeline.GetIsTrackEnabled(tipo, pista) is False:
            continue
        for item in timeline.GetItemListInTrack(tipo, pista) or []:
            mpi = item.GetMediaPoolItem()
            ini, fin = item.GetStart(), item.GetEnd()
            ov_a, ov_b = max(a, ini), min(b, fin)
            if not mpi or ov_b - ov_a < 2:
                continue
            base = inicio_fuente(item)
            resultado.append({
                "mediaPoolItem": mpi,
                "startFrame": base + ov_a - ini,
                "endFrame": base + ov_b - ini - 1,
                "pista": pista,
                "desplazamiento": ov_a - a,
            })
    return resultado


def nombre_libre(proyecto, nombre):
    usados = {proyecto.GetTimelineByIndex(i).GetName()
              for i in range(1, int(proyecto.GetTimelineCount()) + 1)}
    final, n = nombre, 2
    while final in usados:
        final, n = f"{nombre} ({n})", n + 1
    return final


def ampliar_para_vertical(timeline):
    for item in timeline.GetItemListInTrack("video", 1) or []:
        mpi = item.GetMediaPoolItem()
        try:
            w, h = (int(x) for x in mpi.GetClipProperty("Resolution").lower().split("x"))
        except Exception:
            w, h = 1920, 1080
        ajuste = min(ANCHO / w, ALTO / h)    # "Scale entire image to fit" (por defecto)
        relleno = max(ANCHO / w, ALTO / h)   # lo que necesitamos para llenar el 9:16
        zoom = round(relleno / ajuste, 3)
        item.SetProperty("ZoomX", zoom)
        item.SetProperty("ZoomY", zoom)


def main():
    r = obtener_resolve()
    proyecto = r.GetProjectManager().GetCurrentProject()
    original = proyecto.GetCurrentTimeline() if proyecto else None
    if not original:
        print("Abre el timeline de la entrevista antes de ejecutar este script.")
        return
    pool = proyecto.GetMediaPool()
    carpeta = next((c for c in pool.GetRootFolder().GetSubFolderList() or []
                    if c.GetName() == CARPETA), None)
    if carpeta:
        pool.SetCurrentFolder(carpeta)

    inicio = original.GetStartFrame()
    marcadores = [(int(f), m) for f, m in (original.GetMarkers() or {}).items()
                  if m.get("color") == COLOR and int(m.get("duration", 1)) > 1]
    if not marcadores:
        print("No hay marcadores morados con duración en este timeline.")
        return

    creados = []
    for n, (frame, m) in enumerate(sorted(marcadores, key=lambda x: x[0]), 1):
        a, b = inicio + frame, inicio + frame + int(m["duration"])
        nombre = nombre_libre(proyecto, (m.get("name") or f"SHORT {n}")[:70])
        nuevo = pool.CreateEmptyTimeline(nombre)
        if not nuevo:
            print("No se pudo crear el timeline", nombre)
            continue
        proyecto.SetCurrentTimeline(nuevo)
        nuevo.SetSetting("useCustomSettings", "1")
        nuevo.SetSetting("timelineResolutionWidth", str(ANCHO))
        nuevo.SetSetting("timelineResolutionHeight", str(ALTO))
        destino = nuevo.GetStartFrame()

        video, audio = tramos(original, "video", a, b), tramos(original, "audio", a, b)
        colocados = []
        for clip, tipo in [(c, 1) for c in video] + [(c, 2) for c in audio]:
            colocados.append({
                "mediaPoolItem": clip["mediaPoolItem"], "startFrame": clip["startFrame"],
                "endFrame": clip["endFrame"], "mediaType": tipo, "trackIndex": clip["pista"],
                "recordFrame": destino + clip["desplazamiento"],
            })
        ok = pool.AppendToTimeline(colocados)
        if not ok:  # versiones antiguas: añadir solo la pista V1 (con su audio) en orden
            pool.AppendToTimeline([{k: c[k] for k in ("mediaPoolItem", "startFrame", "endFrame")}
                                   for c in video if c["pista"] == 1])
        ampliar_para_vertical(nuevo)
        creados.append(nombre)

    proyecto.SetCurrentTimeline(original)
    print(f"Creados {len(creados)} Shorts verticales:")
    for c in creados:
        print("  ·", c)
    print("Revisa en cada uno: encuadre, subtítulos grandes (zona central), gancho en "
          "pantalla en los 2 primeros segundos y llamada a ver la entrevista completa.")


main()
