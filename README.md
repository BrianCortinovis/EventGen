# EventGen

Motore locale per generare configurazioni territoriali, analizzare eventi pubblici da fonti web e social discovery-only e produrre output pronti per un futuro sito o portale.

[Repository GitHub](https://github.com/BrianCortinovis/EventGen) | [Quickstart](docs/QUICKSTART.md) | [Configurazione](docs/CONFIGURATION.md) | [Formato sources.yaml](docs/SOURCES_FORMAT.md) | [Motore aree](docs/ENGINE.md)

## Obiettivo

Questo repository contiene il core terminale di EventGen. Il progetto è pensato per restare generico e riutilizzabile: i territori reali e i file area usati in produzione restano locali e non vengono pubblicati nel repo.

## Stato attuale

Al momento il repository contiene:

- `run.py` con subcomandi per aree, generazione config e analisi;
- cartella `catalog/areas/` pronta a ricevere file area locali non versionati;
- configurazione via `project.yaml` e `sources.yaml`;
- parsing, analisi, deduplica e rendering HTML;
- provider IA via CLI con euristiche usate solo come supporto;
- una skill Codex nativa in `skills/eventgencodex/`.

## Direzione del progetto

I prossimi blocchi di sviluppo previsti qui dentro sono:

1. migliorare il motore di selezione area o territorio;
2. arricchire il generatore di `sources.yaml` compatibile;
3. integrare discovery automatica da mappa, comune, provincia o raggio;
4. collegare questi output a un sito o portale eventi.

## Cosa fa

- esegue una pipeline manuale con `python3 run.py`;
- usa configurazione esterna, quindi non è legato a una sola area;
- supporta HTML statico, WordPress/PHP, listing eventi e pagine evento;
- può usare un browser headless per pagine dinamiche quando serve;
- usa i social solo per discovery, mai come conferma forte;
- deduplica eventi simili e assegna un livello di affidabilità;
- importa solo eventi ancora attivi alla data di esecuzione;
- arricchisce la scheda evento con testo esteso, foto, flyer e link YouTube;
- genera `events.html`, `events.json` ed export portal-ready con SEO, ricerca e tracking.

## Struttura

```text
run.py
project.yaml
sources.yaml
sources_candidates.yaml
event_pipeline/
docs/
output/
```

## Avvio rapido

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run.py list-areas
python3 run.py generate-config --query "Nome Zona"
python3 run.py analyze --project generated/nome-zona/project.yaml --sources generated/nome-zona/sources.yaml --candidates generated/nome-zona/sources_candidates.yaml --provider=claude
```

Bootstrap completo:

```bash
python3 run.py bootstrap --query "Nome Zona" --provider=openai
python3 run.py bootstrap --query "Nome Zona" --provider=claude
python3 run.py bootstrap --query "Nome Zona" --provider=gemini
```

`--max-sources` esiste ancora, ma solo per test rapidi: il flusso normale deve processare tutte le fonti attive.

## Versione Codex nativa

Nel repository è inclusa anche una skill per Codex:

- `skills/eventgencodex/`

Quando installata in Codex, si usa come:

```text
Usa $EventGenCodex per generare la configurazione di una zona e lanciare il bootstrap.
```

## Motore iniziale

Comandi gia disponibili:

- `python3 run.py list-areas`
- `python3 run.py resolve-area --query "Nome Zona"`
- `python3 run.py generate-config --query "Nome Zona"`
- `python3 run.py bootstrap --query "Nome Zona" --provider=claude`
- `python3 run.py analyze ...`

Il catalogo repository resta vuoto di default. I file area reali possono stare in `catalog/areas/` sul tuo ambiente locale oppure in una cartella esterna passata via `--catalog`.

## Tipi di eventi coperti

Il motore e pensato per coprire praticamente tutto il perimetro eventi pubblici:

- sagre, feste, mercatini, fiere;
- mostre, cinema, cultura, tradizioni;
- concerti, live, spettacoli;
- serate in bar, pub, enoteche e locali;
- nightlife, dj set, discoteche, bowling, karaoke e intrattenimento indoor;
- parate, cerimonie, manifestazioni ufficiali;
- eventi sportivi pubblici e outdoor.

L'obiettivo e distinguere gli eventi reali con data da semplici pagine promozionali o istituzionali.

## Export per portali

Oltre all'HTML e al JSON standard, la pipeline produce anche:

- `output/portal_events.json`
- `output/portal_events.ndjson`
- `output/seo_index.json`
- `output/search_index.ndjson`
- `output/site_import.json`

Questi file sono preparati per futuri aggiornamenti di siti o portali web, con campi utili per:

- SEO editoriale;
- Open Graph e Twitter cards;
- import analytics e tracking GA4;
- ricerca interna;
- import verso CMS o portali eventi;
- schede evento con testo, media, sorgenti e metadata.

## Configurazione

- `project.yaml`: area, categorie, parole chiave, output;
- `sources.yaml`: fonti attive;
- `sources_candidates.yaml`: fonti scoperte ma non validate.

Il repository è completamente generico e non contiene più territori pubblici di esempio. Il file `sources.yaml` deve seguire il formato compatibile documentato in [docs/SOURCES_FORMAT.md](docs/SOURCES_FORMAT.md).

Nel setup locale dell'autore, il prompt usato per generare file fonti compatibili è mantenuto anche in:

`/Users/brian/Desktop/Fonti_Generation/PROMPT_generate_compatible_sources.md`

## Affidabilità fonti

- `alta`: comuni, proloco, musei, siti ufficiali;
- `media`: portali e aggregatori;
- `bassa`: social.

Gli eventi trovati solo via social restano non confermati.

## Provider IA

La pipeline richiede un provider IA via CLI:

- `openai` tramite Codex CLI
- `claude` tramite Claude Code CLI
- `gemini` tramite Gemini CLI, se installato

Le euristiche locali restano attive per parsing, date, filtri e supporto al prompt, ma non sostituiscono il provider IA.

## Rendering browser opzionale

Per fonti con JavaScript è possibile impostare `requires_browser: true` in `sources.yaml`.

```bash
pip install playwright
python -m playwright install
```

## Roadmap pubblica

Per rendere il progetto più facile da usare da altri, vedi [docs/PUBLIC_PROJECT.md](docs/PUBLIC_PROJECT.md).
