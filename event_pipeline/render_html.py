import json
from datetime import datetime

from event_pipeline.models import ProjectConfig


def render_events_html(project: ProjectConfig, events):
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    events_payload = json.dumps([event.to_dict() for event in events], ensure_ascii=False)
    categories = json.dumps(sorted({event.category for event in events if event.category}), ensure_ascii=False)
    municipalities = json.dumps(sorted({event.municipality for event in events if event.municipality}), ensure_ascii=False)
    sources = json.dumps(sorted({event.source for event in events if event.source}), ensure_ascii=False)
    reliabilities = json.dumps(sorted({event.reliability for event in events if event.reliability}), ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="{project.language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{project.name}</title>
  <style>
    :root {{
      --bg: #0b0f14;
      --bg-elev: #11161d;
      --bg-panel: #151b23;
      --bg-panel-2: #1a2230;
      --line: #283243;
      --line-soft: #202938;
      --text: #e7edf6;
      --muted: #91a0b5;
      --accent: #57a6ff;
      --accent-soft: rgba(87, 166, 255, 0.12);
      --success: #7ee787;
      --warn: #ffb86b;
      --danger: #ff7b72;
      --shadow: 0 18px 60px rgba(0, 0, 0, 0.32);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; }}
    body {{
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(87, 166, 255, 0.1), transparent 28rem),
        radial-gradient(circle at top right, rgba(126, 231, 135, 0.06), transparent 22rem),
        linear-gradient(180deg, #0a0d12 0%, #0c1118 100%);
    }}
    .app {{
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto auto 1fr;
    }}
    .topbar {{
      border-bottom: 1px solid var(--line);
      background: rgba(10, 14, 20, 0.92);
      backdrop-filter: blur(14px);
      position: sticky;
      top: 0;
      z-index: 5;
    }}
    .topbar-inner {{
      max-width: 1560px;
      margin: 0 auto;
      padding: 18px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}
    .title-block {{
      min-width: 0;
    }}
    .eyebrow {{
      color: var(--accent);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      margin-bottom: 6px;
    }}
    .title-block h1 {{
      margin: 0;
      font-size: clamp(1.25rem, 2.6vw, 2.1rem);
      font-weight: 650;
      letter-spacing: -0.02em;
    }}
    .title-block p {{
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 0.96rem;
    }}
    .top-stats {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .stat {{
      border: 1px solid var(--line);
      background: var(--bg-panel);
      padding: 10px 12px;
      min-width: 132px;
    }}
    .stat-label {{
      display: block;
      color: var(--muted);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 4px;
    }}
    .stat-value {{
      font-size: 0.98rem;
      font-weight: 600;
    }}
    .toolbar {{
      border-bottom: 1px solid var(--line);
      background: rgba(14, 18, 25, 0.92);
    }}
    .toolbar-inner {{
      max-width: 1560px;
      margin: 0 auto;
      padding: 18px 24px;
      display: grid;
      grid-template-columns: 1.2fr repeat(6, minmax(140px, 1fr));
      gap: 10px;
    }}
    .field {{
      display: grid;
      gap: 6px;
    }}
    .field label {{
      color: var(--muted);
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .field input,
    .field select {{
      width: 100%;
      border: 1px solid var(--line);
      background: var(--bg-panel);
      color: var(--text);
      padding: 11px 12px;
      outline: none;
      appearance: none;
    }}
    .field input:focus,
    .field select:focus {{
      border-color: var(--accent);
      box-shadow: inset 0 0 0 1px var(--accent);
    }}
    .workspace {{
      max-width: 1560px;
      width: 100%;
      margin: 0 auto;
      padding: 20px 24px 28px;
      display: grid;
      grid-template-columns: 420px minmax(0, 1fr);
      gap: 16px;
      min-height: 0;
    }}
    .panel {{
      min-height: 0;
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(20, 26, 35, 0.96), rgba(16, 21, 29, 0.96));
      box-shadow: var(--shadow);
    }}
    .panel-header {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--line-soft);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }}
    .panel-title {{
      font-size: 0.92rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .panel-meta {{
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .list-panel {{
      display: grid;
      grid-template-rows: auto 1fr;
      min-height: 72vh;
    }}
    .list-scroll {{
      overflow: auto;
      min-height: 0;
    }}
    .event-row {{
      width: 100%;
      text-align: left;
      border: 0;
      border-bottom: 1px solid var(--line-soft);
      background: transparent;
      color: inherit;
      padding: 14px 16px;
      cursor: pointer;
      display: grid;
      gap: 8px;
    }}
    .event-row:hover {{
      background: rgba(255, 255, 255, 0.025);
    }}
    .event-row.active {{
      background: linear-gradient(90deg, var(--accent-soft), transparent 78%);
      box-shadow: inset 2px 0 0 var(--accent);
    }}
    .row-top {{
      display: flex;
      justify-content: space-between;
      align-items: start;
      gap: 12px;
    }}
    .row-title {{
      font-size: 0.98rem;
      line-height: 1.35;
      font-weight: 600;
    }}
    .row-date {{
      flex-shrink: 0;
      color: var(--accent);
      font-size: 0.84rem;
      font-weight: 600;
    }}
    .row-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 0.84rem;
    }}
    .row-summary {{
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.45;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--line);
      background: var(--bg-panel-2);
      color: var(--text);
      padding: 3px 8px;
      font-size: 0.78rem;
      white-space: nowrap;
    }}
    .badge.reliability-alta {{ border-color: rgba(126, 231, 135, 0.35); color: var(--success); }}
    .badge.reliability-media {{ border-color: rgba(255, 184, 107, 0.35); color: var(--warn); }}
    .badge.reliability-bassa {{ border-color: rgba(255, 123, 114, 0.35); color: var(--danger); }}
    .detail-panel {{
      display: grid;
      grid-template-rows: auto 1fr;
      min-height: 72vh;
    }}
    .detail-scroll {{
      overflow: auto;
      min-height: 0;
    }}
    .detail-empty {{
      height: 100%;
      display: grid;
      place-items: center;
      color: var(--muted);
      padding: 32px;
      text-align: center;
    }}
    .detail-body {{
      padding: 18px 18px 28px;
      display: grid;
      gap: 18px;
    }}
    .detail-title {{
      margin: 0;
      font-size: clamp(1.4rem, 2vw, 2rem);
      line-height: 1.08;
      letter-spacing: -0.02em;
    }}
    .detail-head {{
      display: grid;
      gap: 12px;
    }}
    .detail-badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .detail-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .info-block {{
      border: 1px solid var(--line-soft);
      background: rgba(255, 255, 255, 0.02);
      padding: 12px 13px;
    }}
    .info-label {{
      display: block;
      color: var(--muted);
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 5px;
    }}
    .info-value {{
      font-size: 0.95rem;
      line-height: 1.45;
    }}
    .hero-image {{
      width: 100%;
      max-height: 460px;
      object-fit: cover;
      border: 1px solid var(--line);
      background: #0f141b;
    }}
    .section {{
      display: grid;
      gap: 10px;
    }}
    .section h2 {{
      margin: 0;
      font-size: 0.84rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .description {{
      white-space: pre-line;
      line-height: 1.65;
      color: #d9e1ec;
      font-size: 0.98rem;
    }}
    .gallery {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 10px;
    }}
    .gallery a {{
      border: 1px solid var(--line);
      background: var(--bg-panel);
      display: block;
      overflow: hidden;
    }}
    .gallery img {{
      width: 100%;
      height: 140px;
      object-fit: cover;
      display: block;
    }}
    .asset-list {{
      display: grid;
      gap: 8px;
    }}
    .asset-link {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 11px 12px;
      border: 1px solid var(--line);
      background: var(--bg-panel);
      color: var(--text);
      text-decoration: none;
    }}
    .asset-link span:last-child {{
      color: var(--accent);
      white-space: nowrap;
    }}
    .detail-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .action-link {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      color: var(--text);
      border: 1px solid var(--line);
      background: var(--bg-panel);
      padding: 11px 13px;
    }}
    .action-link.primary {{
      border-color: rgba(87, 166, 255, 0.35);
      background: var(--accent-soft);
      color: #dcecff;
    }}
    .mono {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.85rem;
    }}
    @media (max-width: 1180px) {{
      .toolbar-inner {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}
      .workspace {{
        grid-template-columns: 360px minmax(0, 1fr);
      }}
    }}
    @media (max-width: 900px) {{
      .topbar-inner {{
        flex-direction: column;
        align-items: start;
      }}
      .top-stats {{
        justify-content: start;
      }}
      .toolbar-inner {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .workspace {{
        grid-template-columns: 1fr;
      }}
      .list-panel,
      .detail-panel {{
        min-height: auto;
      }}
      .detail-grid {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 640px) {{
      .toolbar-inner {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="title-block">
          <div class="eyebrow">Event Workspace</div>
          <h1>{project.name}</h1>
          <p>{project.description}</p>
        </div>
        <div class="top-stats">
          <div class="stat">
            <span class="stat-label">Area</span>
            <span class="stat-value">{project.area_label}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Generato</span>
            <span class="stat-value">{generated_at}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Totale Record</span>
            <span class="stat-value" id="total-stat">{len(events)}</span>
          </div>
        </div>
      </div>
    </header>

    <section class="toolbar">
      <div class="toolbar-inner">
        <div class="field">
          <label for="q">Ricerca</label>
          <input id="q" type="search" placeholder="Titolo, luogo, descrizione, tag">
        </div>
        <div class="field">
          <label for="date">Data da</label>
          <input id="date" type="date">
        </div>
        <div class="field">
          <label for="municipality">Comune</label>
          <select id="municipality"></select>
        </div>
        <div class="field">
          <label for="category">Categoria</label>
          <select id="category"></select>
        </div>
        <div class="field">
          <label for="source">Fonte</label>
          <select id="source"></select>
        </div>
        <div class="field">
          <label for="reliability">Affidabilità</label>
          <select id="reliability"></select>
        </div>
        <div class="field">
          <label for="sort">Ordina per</label>
          <select id="sort">
            <option value="date_asc">Data crescente</option>
            <option value="date_desc">Data decrescente</option>
            <option value="municipality">Comune</option>
            <option value="category">Categoria</option>
            <option value="title">Titolo</option>
          </select>
        </div>
      </div>
    </section>

    <main class="workspace">
      <section class="panel list-panel">
        <div class="panel-header">
          <div class="panel-title">Elenco Eventi</div>
          <div class="panel-meta" id="summary"></div>
        </div>
        <div class="list-scroll" id="event-list"></div>
      </section>

      <section class="panel detail-panel">
        <div class="panel-header">
          <div class="panel-title">Scheda Evento</div>
          <div class="panel-meta mono" id="detail-meta"></div>
        </div>
        <div class="detail-scroll" id="event-detail"></div>
      </section>
    </main>
  </div>

  <script>
    const events = {events_payload};
    const categories = {categories};
    const municipalities = {municipalities};
    const sources = {sources};
    const reliabilities = {reliabilities};

    const state = {{
      filtered: [],
      selectedId: null,
    }};

    const el = {{
      q: document.getElementById("q"),
      date: document.getElementById("date"),
      municipality: document.getElementById("municipality"),
      category: document.getElementById("category"),
      source: document.getElementById("source"),
      reliability: document.getElementById("reliability"),
      sort: document.getElementById("sort"),
      list: document.getElementById("event-list"),
      detail: document.getElementById("event-detail"),
      summary: document.getElementById("summary"),
      detailMeta: document.getElementById("detail-meta"),
      totalStat: document.getElementById("total-stat"),
    }};

    function fillSelect(node, options, label) {{
      node.innerHTML = "";
      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = `Tutti: ${{label}}`;
      node.appendChild(defaultOption);
      options.forEach((item) => {{
        const option = document.createElement("option");
        option.value = item;
        option.textContent = item;
        node.appendChild(option);
      }});
    }}

    function formatDate(startDate, endDate) {{
      if (!startDate) return "Data non disponibile";
      if (endDate) return `${{startDate}} -> ${{endDate}}`;
      return startDate;
    }}

    function reliabilityClass(value) {{
      return `reliability-${{(value || "").toLowerCase()}}`;
    }}

    function reliabilityLabel(value, status) {{
      return status === "non confermato" ? `${{value}} / non confermato` : value;
    }}

    function matchesFilters(event) {{
      const q = el.q.value.trim().toLowerCase();
      const minDate = el.date.value;
      if (q) {{
        const haystack = [
          event.title,
          event.short_description,
          event.full_description,
          event.municipality,
          event.venue,
          event.category,
          event.source,
          ...(event.tags || [])
        ].join(" ").toLowerCase();
        if (!haystack.includes(q)) return false;
      }}
      if (minDate && (!event.start_date || event.start_date < minDate)) return false;
      if (el.municipality.value && event.municipality !== el.municipality.value) return false;
      if (el.category.value && event.category !== el.category.value) return false;
      if (el.source.value && event.source !== el.source.value) return false;
      if (el.reliability.value && event.reliability !== el.reliability.value) return false;
      return true;
    }}

    function sortEvents(items) {{
      const mode = el.sort.value;
      return [...items].sort((a, b) => {{
        if (mode === "date_desc") return (b.start_date || "").localeCompare(a.start_date || "");
        if (mode === "municipality") return (a.municipality || "").localeCompare(b.municipality || "");
        if (mode === "category") return (a.category || "").localeCompare(b.category || "");
        if (mode === "title") return (a.title || "").localeCompare(b.title || "");
        return (a.start_date || "").localeCompare(b.start_date || "");
      }});
    }}

    function updateState() {{
      state.filtered = sortEvents(events.filter(matchesFilters));
      if (!state.filtered.length) {{
        state.selectedId = null;
        return;
      }}
      const stillVisible = state.filtered.some((event) => event.id === state.selectedId);
      if (!stillVisible) {{
        state.selectedId = state.filtered[0].id;
      }}
    }}

    function renderList() {{
      el.summary.textContent = `${{state.filtered.length}} / ${{events.length}}`;
      el.totalStat.textContent = String(events.length);
      if (!state.filtered.length) {{
        el.list.innerHTML = '<div class="detail-empty">Nessun evento corrisponde ai filtri correnti.</div>';
        return;
      }}

      el.list.innerHTML = state.filtered.map((event) => {{
        const active = event.id === state.selectedId ? "active" : "";
        const summary = escapeHtml((event.short_description || "").slice(0, 180));
        return `
          <button class="event-row ${{active}}" data-event-id="${{escapeAttr(event.id)}}">
            <div class="row-top">
              <div class="row-title">${{escapeHtml(event.title)}}</div>
              <div class="row-date">${{escapeHtml(event.start_date || "-")}}</div>
            </div>
            <div class="row-meta">
              <span>${{escapeHtml(event.municipality || "Comune n/d")}}</span>
              <span>${{escapeHtml(event.category || "Categoria n/d")}}</span>
              <span>${{escapeHtml(event.source || "Fonte n/d")}}</span>
            </div>
            <div class="row-meta">
              <span class="badge ${{reliabilityClass(event.reliability)}}">${{escapeHtml(reliabilityLabel(event.reliability, event.confirmation_status))}}</span>
              <span class="badge">${{escapeHtml((event.gallery_images || []).length + " foto")}}</span>
              <span class="badge">${{escapeHtml((event.flyer_urls || []).length + " flyer")}}</span>
            </div>
            <div class="row-summary">${{summary}}</div>
          </button>
        `;
      }}).join("");

      el.list.querySelectorAll(".event-row").forEach((node) => {{
        node.addEventListener("click", () => {{
          state.selectedId = node.dataset.eventId;
          render();
        }});
      }});
    }}

    function renderDetail() {{
      const event = state.filtered.find((item) => item.id === state.selectedId);
      if (!event) {{
        el.detailMeta.textContent = "";
        el.detail.innerHTML = '<div class="detail-empty">Seleziona un evento dall\\'elenco per aprire la scheda completa.</div>';
        return;
      }}

      el.detailMeta.textContent = event.id || "";

      const badges = [
        `<span class="badge">${{escapeHtml(event.category || "Cultura")}}</span>`,
        `<span class="badge ${{reliabilityClass(event.reliability)}}">${{escapeHtml(reliabilityLabel(event.reliability, event.confirmation_status))}}</span>`,
        ...(event.tags || []).map((tag) => `<span class="badge">${{escapeHtml(tag)}}</span>`)
      ].join("");

      const cover = event.image_url
        ? `<img class="hero-image" src="${{escapeAttr(event.image_url)}}" alt="${{escapeAttr(event.title)}}" loading="lazy">`
        : "";

      const gallery = (event.gallery_images || []).length
        ? `<div class="section"><h2>Immagini e flyer</h2><div class="gallery">${{(event.gallery_images || []).slice(0, 12).map((url) => `
            <a href="${{escapeAttr(url)}}" target="_blank" rel="noreferrer">
              <img src="${{escapeAttr(url)}}" alt="${{escapeAttr(event.title)}}" loading="lazy">
            </a>
          `).join("")}}</div></div>`
        : "";

      const flyers = (event.flyer_urls || []).length
        ? `<div class="section"><h2>Flyer e materiali</h2><div class="asset-list">${{(event.flyer_urls || []).map((url, index) => `
            <a class="asset-link" href="${{escapeAttr(url)}}" target="_blank" rel="noreferrer">
              <span>Asset ${{index + 1}}</span>
              <span>Apri</span>
            </a>
          `).join("")}}</div></div>`
        : "";

      const youtube = (event.youtube_urls || []).length
        ? `<div class="section"><h2>Link YouTube</h2><div class="asset-list">${{(event.youtube_urls || []).map((url, index) => `
            <a class="asset-link" href="${{escapeAttr(url)}}" target="_blank" rel="noreferrer">
              <span>YouTube ${{index + 1}}</span>
              <span>Apri</span>
            </a>
          `).join("")}}</div></div>`
        : "";

      const secondarySources = (event.secondary_sources || []).length
        ? escapeHtml(event.secondary_sources.join(", "))
        : "-";

      el.detail.innerHTML = `
        <div class="detail-body">
          <div class="detail-head">
            <div class="detail-badges">${{badges}}</div>
            <h1 class="detail-title">${{escapeHtml(event.title)}}</h1>
            <div class="detail-actions">
              <a class="action-link primary" href="${{escapeAttr(event.source_url)}}" target="_blank" rel="noreferrer">Apri fonte originale</a>
              ${{event.image_url ? `<a class="action-link" href="${{escapeAttr(event.image_url)}}" target="_blank" rel="noreferrer">Apri immagine principale</a>` : ""}}
            </div>
          </div>

          ${{cover}}

          <div class="detail-grid">
            <div class="info-block"><span class="info-label">Data</span><div class="info-value">${{escapeHtml(formatDate(event.start_date, event.end_date))}}</div></div>
            <div class="info-block"><span class="info-label">Ora</span><div class="info-value">${{escapeHtml(event.time_text || "-")}}</div></div>
            <div class="info-block"><span class="info-label">Comune</span><div class="info-value">${{escapeHtml(event.municipality || "-")}}</div></div>
            <div class="info-block"><span class="info-label">Luogo</span><div class="info-value">${{escapeHtml(event.venue || "-")}}</div></div>
            <div class="info-block"><span class="info-label">Organizzatore</span><div class="info-value">${{escapeHtml(event.organizer || "-")}}</div></div>
            <div class="info-block"><span class="info-label">Fonte primaria</span><div class="info-value">${{escapeHtml(event.source || "-")}}</div></div>
            <div class="info-block"><span class="info-label">Fonti secondarie</span><div class="info-value">${{secondarySources}}</div></div>
            <div class="info-block"><span class="info-label">Asset trovati</span><div class="info-value">${{escapeHtml(`${{(event.gallery_images || []).length}} foto · ${{(event.flyer_urls || []).length}} flyer · ${{(event.youtube_urls || []).length}} link YouTube`)}}</div></div>
          </div>

          <div class="section">
            <h2>Descrizione breve</h2>
            <div class="description">${{escapeHtml(event.short_description || "")}}</div>
          </div>

          <div class="section">
            <h2>Scheda estesa</h2>
            <div class="description">${{escapeHtml(event.full_description || event.short_description || "")}}</div>
          </div>

          ${{gallery}}
          ${{flyers}}
          ${{youtube}}
        </div>
      `;
    }}

    function render() {{
      updateState();
      renderList();
      renderDetail();
    }}

    function escapeHtml(value) {{
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }}

    function escapeAttr(value) {{
      return escapeHtml(value);
    }}

    fillSelect(el.category, categories, "categorie");
    fillSelect(el.municipality, municipalities, "comuni");
    fillSelect(el.source, sources, "fonti");
    fillSelect(el.reliability, reliabilities, "livelli");

    [el.q, el.date, el.municipality, el.category, el.source, el.reliability, el.sort]
      .forEach((node) => node.addEventListener("input", render));
    [el.municipality, el.category, el.source, el.reliability, el.sort]
      .forEach((node) => node.addEventListener("change", render));

    render();
  </script>
</body>
</html>
"""
