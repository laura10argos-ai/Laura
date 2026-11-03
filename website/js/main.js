/* ==========================================================
   Lógica común: cabecera, pie, cambio de idioma, menú móvil,
   enlaces a redes, embeds y formulario de contacto.
   ========================================================== */
(function () {
  const C = window.SITE_CONFIG;
  const T = window.I18N;

  const ICONS = {
    youtube: '<svg viewBox="0 0 24 24"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z"/></svg>',
    instagram: '<svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 3.9 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 1 0 0 12.4 6.2 6.2 0 0 0 0-12.4zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.8a1.4 1.4 0 1 0 0 2.9 1.4 1.4 0 0 0 0-2.9z"/></svg>',
    spotify: '<svg viewBox="0 0 24 24"><path d="M12 0a12 12 0 1 0 0 24 12 12 0 0 0 0-24zm5.5 17.3a.7.7 0 0 1-1 .3c-2.8-1.7-6.4-2.1-10.5-1.2a.7.7 0 1 1-.3-1.5c4.5-1 8.4-.6 11.5 1.4.3.2.4.7.3 1zm1.5-3.3a.9.9 0 0 1-1.3.3c-3.2-2-8.2-2.6-12-1.4a.9.9 0 1 1-.6-1.8c4.4-1.3 9.8-.7 13.5 1.6.5.3.6.9.4 1.3zm.1-3.4C15.3 8.3 8.9 8.1 5.2 9.2a1.1 1.1 0 1 1-.7-2.1c4.3-1.3 11.3-1 15.7 1.6a1.1 1.1 0 0 1-1.1 1.9z"/></svg>'
  };
  window.SITE_ICONS = ICONS;

  const NAV = [
    { href: "negocios.html", key: "nav.business" },
    { href: "empleados.html", key: "nav.employees" },
    { href: "your-own-voice.html", key: "nav.yov" },
    { href: "contacto.html", key: "nav.contact" }
  ];
  const current = location.pathname.split("/").pop() || "index.html";

  /* ---------- Idioma ---------- */
  function getLang() {
    const url = new URLSearchParams(location.search).get("lang");
    if (url === "es" || url === "en") return url;
    try {
      const saved = localStorage.getItem("lang");
      if (saved === "es" || saved === "en") return saved;
    } catch (e) {}
    return (navigator.language || "es").toLowerCase().startsWith("es") ? "es" : "en";
  }

  function applyLang(lang) {
    const dict = T[lang];
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const v = dict[el.dataset.i18n];
      if (v !== undefined) el.innerHTML = v;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const v = dict[el.dataset.i18nPlaceholder];
      if (v !== undefined) el.placeholder = v;
    });
    document.querySelectorAll(".lang-switch button").forEach(b =>
      b.classList.toggle("on", b.dataset.lang === lang));
    const titleKey = document.body.dataset.titleKey;
    if (titleKey && dict[titleKey]) {
      const plain = dict[titleKey].replace(/<[^>]+>/g, "");
      document.title = (titleKey === "home.title" ? C.name : plain + " · " + C.name);
    }
    try { localStorage.setItem("lang", lang); } catch (e) {}
    window.CURRENT_LANG = lang;
  }

  /* ---------- Cabecera y pie ---------- */
  function socialLinks() {
    return ["youtube", "instagram", "spotify"].map(k =>
      `<a href="${C[k]}" target="_blank" rel="noopener" aria-label="${k}">${ICONS[k]}</a>`).join("");
  }

  function renderHeader() {
    const links = NAV.map(n =>
      `<li><a href="${n.href}" data-i18n="${n.key}" class="${current === n.href ? "active" : ""}"></a></li>`).join("");
    document.getElementById("site-header").outerHTML = `
      <header class="site-header">
        <div class="container nav">
          <a class="brand" href="index.html">Laura <span>Díez Argos</span></a>
          <ul class="nav-links" id="nav-links">${links}</ul>
          <div class="nav-right">
            <div class="lang-switch" role="group" aria-label="Language">
              <button data-lang="es">ES</button><button data-lang="en">EN</button>
            </div>
            <button class="menu-toggle" aria-label="Menu" id="menu-toggle"><span></span><span></span><span></span></button>
          </div>
        </div>
      </header>`;
  }

  function renderFooter() {
    const links = NAV.map(n => `<li><a href="${n.href}" data-i18n="${n.key}"></a></li>`).join("");
    document.getElementById("site-footer").outerHTML = `
      <footer class="site-footer">
        <div class="container">
          <div class="footer-grid">
            <div style="max-width:320px">
              <a class="brand" href="index.html">Laura <span>Díez Argos</span></a>
              <p style="margin-top:12px" data-i18n="footer.tagline"></p>
            </div>
            <div><strong data-i18n="footer.explore"></strong><ul class="footer-links" style="margin-top:12px">${links}</ul></div>
            <div><strong data-i18n="footer.follow"></strong><div class="socials" style="margin-top:12px">${socialLinks()}</div></div>
          </div>
          <div class="copy">© ${new Date().getFullYear()} ${C.name}. <span data-i18n="footer.rights"></span></div>
        </div>
      </footer>`;
  }

  /* ---------- Contenido dinámico ---------- */
  function fillDynamic() {
    document.querySelectorAll("[data-link]").forEach(a => {
      a.href = C[a.dataset.link] || "#";
      if (a.href.startsWith("http")) { a.target = "_blank"; a.rel = "noopener"; }
    });
    document.querySelectorAll("[data-icon]").forEach(el => { el.innerHTML = ICONS[el.dataset.icon]; });

    const yt = document.getElementById("yt-embed");
    if (yt && C.youtubeFeaturedId) {
      yt.innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${C.youtubeFeaturedId}" title="YouTube" allowfullscreen loading="lazy"></iframe>`;
    }
    const sp = document.getElementById("sp-embed");
    if (sp && C.spotifyShowId) {
      sp.innerHTML = `<iframe src="https://open.spotify.com/embed/show/${C.spotifyShowId}" title="Spotify" loading="lazy" allow="encrypted-media"></iframe>`;
    }
  }

  function setupForm() {
    const form = document.getElementById("contact-form");
    if (!form) return;
    const status = document.getElementById("form-status");
    form.addEventListener("submit", async e => {
      e.preventDefault();
      const d = T[window.CURRENT_LANG];
      const data = new FormData(form);
      if (C.formEndpoint) {
        try {
          const r = await fetch(C.formEndpoint, { method: "POST", body: data, headers: { Accept: "application/json" } });
          if (!r.ok) throw new Error();
          form.reset();
          status.textContent = d["contact.sent"];
        } catch (err) { status.textContent = d["contact.error"]; }
      } else if (C.email) {
        const subject = encodeURIComponent(`[Web] ${data.get("type")} — ${data.get("name")}`);
        const body = encodeURIComponent(`${data.get("message")}\n\n${data.get("name")} · ${data.get("email")}`);
        location.href = `mailto:${C.email}?subject=${subject}&body=${body}`;
      } else {
        status.textContent = d["contact.error"];
      }
    });
  }

  /* ---------- Inicio ---------- */
  renderHeader();
  renderFooter();
  fillDynamic();
  applyLang(getLang());
  setupForm();

  document.querySelectorAll(".lang-switch button").forEach(b =>
    b.addEventListener("click", () => applyLang(b.dataset.lang)));
  const toggle = document.getElementById("menu-toggle");
  toggle.addEventListener("click", () => document.getElementById("nav-links").classList.toggle("open"));
})();
