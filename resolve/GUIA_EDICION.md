# Kit de edición de entrevistas · Your Own Voice × DaVinci Resolve

Este kit hace el trabajo mecánico de una entrevista larga (transcribir, quitar
silencios, marcar muletillas, encontrar momentos para Shorts y sacar los
capítulos) para que dediques tu tiempo a la parte que solo puedes hacer tú:
decidir qué historia cuenta el episodio.

Funciona con la **versión gratuita** de DaVinci Resolve. Solo se apoya en
funciones que existen en las dos versiones: importar timelines FCPXML,
marcadores desde EDL, subtítulos SRT y los scripts del menú *Workspace > Scripts*.

---

## 1. Instalación (una sola vez)

### 1.1 Herramienta de preparación (en tu ordenador)

```bash
pip install -r requirements.txt
```

Instala Whisper (transcripción local y gratuita, sin subir tus entrevistas a
ningún servicio) y ffmpeg.

### 1.2 Scripts dentro de Resolve

Copia los cuatro archivos de `resolve/scripts_resolve/` en esta carpeta
(créala si no existe):

| Sistema | Carpeta |
|---|---|
| macOS | `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit/` |
| Windows | `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\` |
| Linux | `~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/` |

Reinicia Resolve y aparecerán en **Workspace > Scripts**. Resolve necesita
Python 3 instalado en el ordenador para ejecutar scripts `.py`. Si no tienes
Python, instálalo desde python.org.

---

## 2. Flujo de trabajo de una entrevista

### Paso 1 — Preparar (≈ lo que tarde Whisper)

```bash
python resolve/preparar_entrevista.py "Entrevista Ana.mp4"
```

Si grabaste con varias cámaras o un micro aparte, primero sincroniza en
Resolve y exporta una pista de referencia (vídeo de la cámara principal con el
audio bueno). El script trabaja sobre un único archivo.

Opciones útiles:

| Opción | Para qué |
|---|---|
| `--estilo natural` (defecto) | Solo quita silencios de más de 1,2 s y deja aire. Es el que va con el tono pausado e íntimo del canal. |
| `--estilo equilibrado` | Silencios de más de 0,8 s. |
| `--estilo dinamico` | Silencios de más de 0,5 s, para piezas cortas. |
| `--sin-cortes` | No recorta nada; solo marcadores, subtítulos e informe. |
| `--modelo medium` | Transcripción más precisa (más lenta). |
| `--idioma en` | Entrevistas en inglés. |
| `--max-caracteres 25` | Subtítulos cortos para vídeo vertical. |
| `--transcripcion carpeta/transcripcion.json` | Reutiliza la transcripción y prueba otro estilo sin esperar. |

Se crea la carpeta `Entrevista Ana_resolve/` con todo lo necesario.

### Paso 2 — Montar en Resolve

1. Crea un proyecto nuevo y ejecuta **Workspace > Scripts > YOV_1_Preparar_Proyecto**
   para crear las carpetas del canal.
2. **File > Import > Timeline…** → `corte_bruto.fcpxml`. Si Resolve pregunta,
   deja marcado que importe los clips al Media Pool.
3. En el Media Pool, clic derecho sobre el timeline importado >
   **Timelines > Import > Timeline Markers from EDL…** → `marcadores.edl`.
4. Importa `subtitulos.srt` en el Media Pool y arrástralo al timeline
   (crea una pista de subtítulos).

### Paso 3 — Editar con los marcadores

| Color | Significa | Qué hacer |
|---|---|---|
| 🟡 Amarillo | Muletilla («eh», «o sea», «en plan»…) | Recorta solo si rompe la idea. Algunas muletillas son parte de cómo habla una persona. |
| 🟤 Crema | Palabra repetida («que que») | Normalmente se puede cortar. |
| 🟣 Morado | Candidato a Short / Reel | Escúchalo y decide si se queda. |
| 🔵 Azul | Capítulo (los pones tú) | Título del capítulo en el nombre del marcador. |

Usa **Shift + flecha arriba/abajo** para saltar de marcador en marcador.

Cuando acabes de revisar: **Workspace > Scripts > YOV_4_Limpiar_Marcadores_Revision**
borra los amarillos y crema y deja los azules y morados.

### Paso 4 — Shorts y Reels

**Workspace > Scripts > YOV_2_Crear_Shorts** crea un timeline vertical
1080×1920 por cada marcador morado, en la carpeta *08 Shorts y Reels*, con el
plano ya ampliado. Te queda:

- Encuadrar a quien habla (Inspector > Transform > Position X).
- Subtítulos grandes en la zona central (las interfaces de YouTube e
  Instagram tapan la parte inferior y la derecha).
- El gancho escrito en pantalla desde el primer segundo.
- Cerrar con una invitación a ver la entrevista completa.

`informe.md` explica por qué se propuso cada fragmento. La puntuación es
una heurística: premia ganchos («nadie te cuenta…», «el error…»), preguntas,
temas del canal (trauma, dinero, autoestima, liderazgo…) y ritmo de habla. Te
ahorra escuchar la hora entera para encontrarlos, pero el criterio final es el
tuyo.

### Paso 5 — Capítulos para YouTube y Spotify

Pon marcadores **azules** al inicio de cada bloque y escribe el título en el
nombre. Después ejecuta **Workspace > Scripts > YOV_3_Exportar_Capitulos_YouTube**:
genera el texto en tu Escritorio, listo para la descripción. El script comprueba
las reglas de YouTube: empieza en 0:00, al menos 3 capítulos y 10 s mínimo por
capítulo.

---

## 3. Criterios de edición con tu sello

Los criterios salen del tipo de contenido (conversaciones profundas sobre
psicología, emociones y finanzas) y de lo que buscas transmitir: cercanía y
verdad.

1. **Respeta las pausas con peso.** Después de una pregunta difícil, el
   silencio del invitado *es* contenido. Por eso el estilo por defecto es
   `natural`. Quita los silencios técnicos, no los emocionales.
2. **Arranca con la frase más potente (cold open).** Los 15–30 s de antes de
   la intro son los que deciden si alguien se queda. Usa el mejor candidato
   morado como apertura y después entra con tu presentación.
3. **Cortes J y L en vez de cortes secos.** Que se oiga la respuesta antes
   de ver al invitado (o tu reacción mientras habla). Da sensación de
   conversación real.
4. **Tu reacción también cuenta.** En una entrevista de desarrollo personal,
   tu cara escuchando genera confianza. Guarda planos tuyos asintiendo para
   tapar cortes.
5. **B-roll con moderación.** Úsalo para ilustrar un dato o un ejemplo
   concreto, no para tapar. El protagonista es la conversación.
6. **Color cálido y coherente.** Guarda tu corrección como *Still* en la
   Galería de la página Color y aplícala a todos los episodios. La identidad
   visual estable ayuda a que te reconozcan en la miniatura y en el feed.
7. **Rótulos fijos de marca.** Mismo tipo de letra, posición y animación
   para el nombre del invitado y para las frases destacadas. Guárdalos en
   *05 Marca* o como plantilla de Fusion Title.

---

## 4. Audio y exportación

### Volumen de referencia

| Plataforma | Objetivo de sonoridad | Pico real |
|---|---|---|
| Spotify (vídeo y audio) | −14 LUFS integrados | ≤ −1 dBTP |
| Apple Podcasts | −16 LUFS | ≤ −1 dBTP |
| YouTube | Normaliza el volumen al reproducir; −14 LUFS es el valor de referencia habitual | ≤ −1 dBTP |

Spotify documenta el −14 LUFS y el −1 dBTP en su página oficial de
normalización. YouTube no publica una cifra oficial, por eso se trabaja con
−14 LUFS, que es la referencia del sector. En Resolve: página **Fairlight** >
*Loudness* en los medidores, o clic derecho en el clip > **Normalize Audio
Levels**.

### Exportar (página Deliver)

- **YouTube:** preset *YouTube 1080p* (o 4K si grabas en 4K). YouTube recomienda
  H.264, audio AAC estéreo a 48 kHz y unos 8 Mbps en 1080p a 24–30 fps.
- **Spotify (video podcast):** el mismo máster de YouTube sirve. Para la versión
  solo audio, exporta *Audio Only* en WAV o MP3 de 320 kbps.
- **Shorts/Reels:** 1080×1920, H.264. Los candidatos duran 25–60 s, un rango
  que vale a la vez para YouTube Shorts, Reels y TikTok.

---

## 5. Límites conocidos

- Whisper a veces se salta sonidos como «eh» o «mmm», así que habrá muletillas
  sin marcar. El corte de silencios se basa en el audio, no en la
  transcripción, y es fiable.
- Si el umbral de silencio no encaja con tu sala (mucho ruido de fondo), prueba
  `--estilo equilibrado` o ajusta `umbral_db` en `ESTILOS` dentro de
  `preparar_entrevista.py`.
- `YOV_2_Crear_Shorts` asume que los clips no tienen cambios de velocidad. En
  versiones antiguas de Resolve (anteriores a la 18.5) solo copia la pista V1
  con su audio.
- La transcripción integrada y el aislamiento de voz de Resolve son de la versión
  Studio. Este kit cubre la transcripción con Whisper. Para limpiar ruido en la
  versión gratuita, usa el filtro *Noise Reduction* de Fairlight con moderación.
