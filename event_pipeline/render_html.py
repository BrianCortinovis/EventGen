import json
from datetime import datetime

from event_pipeline.models import EventRecord, ProjectConfig


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
      --bg: #f5f0e8;
      --panel: #fffaf3;
      --border: #d8c8b3;
      --text: #2f2419;
      --muted: #7a6856;
      --accent: #a04c2f;
      --accent-soft: #f0d8cb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, #fff6df 0, transparent 28rem),
        linear-gradient(180deg, #f7f2ea 0%, #efe5d7 100%);
    }}
    .shell {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .hero {{
      padding: 28px;
      border: 1px solid var(--border);
      background: rgba(255, 250, 243, 0.92);
      border-radius: 18px;
      box-shadow: 0 12px 30px rgba(80, 47, 20, 0.08);
    }}
    .hero h1 {{
      margin: 0 0 10px;
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
      max-width: 56rem;
      line-height: 1.5;
    }}
    .meta {{
      margin-top: 12px;
      font-size: 0.95rem;
      color: var(--muted);
    }}
    .controls {{
      margin-top: 22px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
    }}
    .controls label {{
      display: block;
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 4px;
    }}
    .controls input,
    .controls select {{
      width: 100%;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: white;
      color: var(--text);
    }}
    .summary {{
      margin: 18px 0 12px;
      font-size: 0.95rem;
      color: var(--muted);
    }}
    .event-list {{
      display: grid;
      gap: 14px;
    }}
    .event-card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 18px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 260px;
      gap: 16px;
    }}
    .event-cover {{
      width: 100%;
      aspect-ratio: 16 / 9;
      object-fit: cover;
      border-radius: 12px;
      border: 1px solid var(--border);
      margin-top: 12px;
      background: #f0e5d5;
    }}
    .event-main h2 {{
      margin: 0 0 8px;
      font-size: 1.35rem;
    }}
    .event-main p {{
      margin: 10px 0 0;
      line-height: 1.5;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }}
    .chip {{
      border-radius: 999px;
      padding: 4px 10px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.82rem;
    }}
    .event-side {{
      min-width: 220px;
      text-align: right;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .event-side a {{
      color: var(--accent);
      text-decoration: none;
    }}
    .asset-links {{
      display: grid;
      gap: 6px;
      margin-top: 10px;
    }}
    .asset-links a {{
      font-size: 0.9rem;
    }}
    details {{
      margin-top: 14px;
    }}
    summary {{
      cursor: pointer;
      color: var(--accent);
      font-size: 0.92rem;
    }}
    .full-description {{
      margin-top: 10px;
      white-space: pre-line;
      color: var(--muted);
      line-height: 1.55;
    }}
    .empty {{
      padding: 28px;
      text-align: center;
      color: var(--muted);
      border: 1px dashed var(--border);
      border-radius: 16px;
      background: rgba(255, 250, 243, 0.8);
    }}
    @media (max-width: 720px) {{
      .event-card {{
        grid-template-columns: 1fr;
      }}
      .event-side {{
        text-align: left;
        min-width: 0;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <h1>{project.name}</h1>
      <p>{project.description}</p>
      <div class="meta">Area esempio configurata: {project.area_label}. Generato il {generated_at}.</div>
      <div class="controls">
        <div>
          <label for="q">Ricerca testuale</label>
          <input id="q" type="search" placeholder="Titolo, luogo, descrizione">
        </div>
        <div>
          <label for="date">Data da</label>
          <input id="date" type="date">
        </div>
        <div>
          <label for="municipality">Comune</label>
          <select id="municipality"></select>
        </div>
        <div>
          <label for="category">Categoria</label>
          <select id="category"></select>
        </div>
        <div>
          <label for="source">Fonte</label>
          <select id="source"></select>
        </div>
        <div>
          <label for="reliability">Affidabilità</label>
          <select id="reliability"></select>
        </div>
        <div>
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
    <div class="summary" id="summary"></div>
    <section class="event-list" id="event-list"></section>
  </div>

  <script>
    const events = {events_payload};
    const categories = {categories};
    const municipalities = {municipalities};
    const sources = {sources};
    const reliabilities = {reliabilities};

    const el = {{
      q: document.getElementById("q"),
      date: document.getElementById("date"),
      municipality: document.getElementById("municipality"),
      category: document.getElementById("category"),
      source: document.getElementById("source"),
      reliability: document.getElementById("reliability"),
      sort: document.getElementById("sort"),
      list: document.getElementById("event-list"),
      summary: document.getElementById("summary"),
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

    fillSelect(el.category, categories, "categorie");
    fillSelect(el.municipality, municipalities, "comuni");
    fillSelect(el.source, sources, "fonti");
    fillSelect(el.reliability, reliabilities, "livelli");

    function formatDate(startDate, endDate) {{
      if (!startDate) return "Data non disponibile";
      if (endDate) return `${{startDate}} - ${{endDate}}`;
      return startDate;
    }}

    function matchesFilters(event) {{
      const q = el.q.value.trim().toLowerCase();
      const minDate = el.date.value;
      if (q) {{
        const haystack = [
          event.title,
          event.short_description,
          event.municipality,
          event.venue,
          event.category,
          event.source
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

    function reliabilityLabel(value, status) {{
      return status === "non confermato" ? `${{value}} / non confermato` : value;
    }}

    function render() {{
      const filtered = sortEvents(events.filter(matchesFilters));
      el.summary.textContent = `${{filtered.length}} eventi mostrati su ${{events.length}} raccolti`;

      if (!filtered.length) {{
        el.list.innerHTML = '<div class="empty">Nessun evento corrisponde ai filtri correnti.</div>';
        return;
      }}

      el.list.innerHTML = filtered.map((event) => {{
        const tags = (event.tags || []).map((tag) => `<span class="chip">${{escapeHtml(tag)}}</span>`).join("");
        const secondary = (event.secondary_sources || []).length
          ? `<div>Fonti secondarie: ${{escapeHtml(event.secondary_sources.join(", "))}}</div>`
          : "";
        const cover = event.image_url
          ? `<img class="event-cover" src="${{escapeAttr(event.image_url)}}" alt="${{escapeAttr(event.title)}}" loading="lazy">`
          : "";
        const assets = [
          (event.flyer_urls || []).slice(0, 3).map((url, index) => `<a href="${{escapeAttr(url)}}" target="_blank" rel="noreferrer">Flyer ${{index + 1}}</a>`),
          (event.youtube_urls || []).slice(0, 2).map((url, index) => `<a href="${{escapeAttr(url)}}" target="_blank" rel="noreferrer">YouTube ${{index + 1}}</a>`)
        ].flat().join("");
        const detailSection = event.full_description && event.full_description !== event.short_description
          ? `<details><summary>Apri scheda estesa</summary><div class="full-description">${{escapeHtml(event.full_description)}}</div></details>`
          : "";
        const mediaSummary = [
          (event.gallery_images || []).length ? `${{event.gallery_images.length}} foto` : "",
          (event.flyer_urls || []).length ? `${{event.flyer_urls.length}} flyer` : "",
          (event.youtube_urls || []).length ? `${{event.youtube_urls.length}} link video` : ""
        ].filter(Boolean).join(" · ");
        return `
          <article class="event-card">
            <div class="event-main">
              <h2>${{escapeHtml(event.title)}}</h2>
              <div class="chips">
                <span class="chip">${{escapeHtml(event.category || "Cultura")}}</span>
                <span class="chip">${{escapeHtml(reliabilityLabel(event.reliability, event.confirmation_status))}}</span>
                ${{tags}}
              </div>
              <p>${{escapeHtml(event.short_description || "")}}</p>
              ${{cover}}
              ${{detailSection}}
            </div>
            <aside class="event-side">
              <div><strong>Data:</strong> ${{escapeHtml(formatDate(event.start_date, event.end_date))}}</div>
              <div><strong>Comune:</strong> ${{escapeHtml(event.municipality || "-")}}</div>
              <div><strong>Luogo:</strong> ${{escapeHtml(event.venue || "-")}}</div>
              <div><strong>Fonte:</strong> ${{escapeHtml(event.source || "-")}}</div>
              <div><strong>Ora:</strong> ${{escapeHtml(event.time_text || "-")}}</div>
              <div><strong>Asset:</strong> ${{escapeHtml(mediaSummary || "-")}}</div>
              ${{secondary}}
              <div class="asset-links">${{assets}}</div>
              <div style="margin-top:8px;"><a href="${{escapeAttr(event.source_url)}}" target="_blank" rel="noreferrer">Apri fonte originale</a></div>
            </aside>
          </article>
        `;
      }}).join("");
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

    [el.q, el.date, el.municipality, el.category, el.source, el.reliability, el.sort]
      .forEach((node) => node.addEventListener("input", render));
    [el.municipality, el.category, el.source, el.reliability, el.sort]
      .forEach((node) => node.addEventListener("change", render));

    render();
  </script>
</body>
</html>
"""
