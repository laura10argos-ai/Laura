/* ==========================================================
   CONFIGURACIÓN — edita aquí tus enlaces y datos de contacto.
   Todo lo que esté como "#" o vacío es un hueco por rellenar.
   ========================================================== */
window.SITE_CONFIG = {
  name: "Laura Díez Argos",
  email: "",                      // p. ej. "hola@lauradiezargos.com"
  youtube: "#",                   // URL del canal Your Own Voice
  instagram: "#",                 // URL de tu perfil personal de Instagram
  spotify: "#",                   // URL del podcast en Spotify
  linkedin: "#",                  // opcional
  // Para que el formulario envíe emails sin abrir el cliente de correo,
  // crea un formulario gratuito en https://formspree.io y pega aquí la URL.
  formEndpoint: "",               // p. ej. "https://formspree.io/f/xxxxxxx"
  // Embeds (opcionales). Pega el ID del vídeo / episodio destacado.
  youtubeFeaturedId: "",          // p. ej. "dQw4w9WgXcQ"
  spotifyShowId: "",              // ID del show (lo que va tras /show/ en la URL)

  // Newsletter: endpoint de tu herramienta (Formspree, Mailchimp, Brevo, Substack…)
  newsletterEndpoint: "",

  // EPISODIOS DESTACADOS (portada y página del podcast).
  // Pon el ID del vídeo de YouTube y la miniatura se carga sola.
  // Los títulos van en los dos idiomas.
  episodes: [
    { youtubeId: "", tag: { es: "Psicología", en: "Psychology" },
      title: { es: "Título del episodio 1", en: "Episode 1 title" },
      guest: { es: "con [nombre del invitado]", en: "with [guest name]" } },
    { youtubeId: "", tag: { es: "Finanzas", en: "Finance" },
      title: { es: "Título del episodio 2", en: "Episode 2 title" },
      guest: { es: "con [nombre del invitado]", en: "with [guest name]" } },
    { youtubeId: "", tag: { es: "Liderazgo", en: "Leadership" },
      title: { es: "Título del episodio 3", en: "Episode 3 title" },
      guest: { es: "con [nombre del invitado]", en: "with [guest name]" } }
  ]
};
