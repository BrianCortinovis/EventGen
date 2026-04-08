# EventGEn

Base di partenza per costruire un'app desktop completa che generi aree, generi file fonti compatibili e analizzi eventi pubblici da fonti web e social.

[Repository GitHub](https://github.com/BrianCortinovis/EventGEn) | [Quickstart](docs/QUICKSTART.md) | [Configurazione](docs/CONFIGURATION.md) | [Formato sources.yaml](docs/SOURCES_FORMAT.md) | [Motore aree](docs/ENGINE.md)

## Obiettivo

Questo repository nasce come evoluzione del motore locale già costruito: da qui vogliamo arrivare a un'app desktop integrata che permetta di selezionare una zona, generare un file fonti compatibile, analizzare le fonti e produrre un output eventi usabile anche da utenti non tecnici.

## Stato attuale

Al momento il repository contiene:

- `run.py` con subcomandi per aree, generazione config e analisi;
- catalogo aree locale in `catalog/areas/`;
- configurazione via `project.yaml` e `sources.yaml`;
- parsing, analisi, deduplica e rendering HTML;
- supporto a provider IA opzionali con fallback euristico;
- una skill Codex nativa in `skills/eventgen-native/`.

## Direzione del progetto

I prossimi blocchi di sviluppo previsti qui dentro sono:

1. migliorare il motore di selezione area o territorio;
2. arricchire il generatore di `sources.yaml` compatibile;
3. integrare discovery automatica da mappa, comune, provincia o raggio;
4. aggiungere la UX desktop con avvio da icona.

## Cosa fa

- esegue una pipeline manuale con `python3 run.py`;
- usa configurazione esterna, quindi non è legato a una sola area;
- supporta HTML statico, WordPress/PHP, listing eventi e pagine evento;
- può usare un browser headless per pagine dinamiche quando serve;
- usa i social solo per discovery, mai come conferma forte;
- deduplica eventi simili e assegna un livello di affidabilità;
- genera `events.html` e `output/events.html`.

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
python3 run.py generate-config --query "Val Seriana"
python3 run.py analyze --project generated/val-seriana/project.yaml --sources generated/val-seriana/sources.yaml --candidates generated/val-seriana/sources_candidates.yaml --max-sources 4
```

Con provider IA opzionale:

```bash
python3 run.py bootstrap --query "Val Seriana" --provider=openai --max-sources 4
python3 run.py bootstrap --query "Val Seriana" --provider=claude --max-sources 4
python3 run.py bootstrap --query "Val Seriana" --provider=gemini --max-sources 4
```

## Versione Codex nativa

Nel repository è inclusa anche una skill per Codex:

- `skills/eventgen-native/`

Quando installata in Codex, si usa come:

```text
Usa $eventgen-native per generare la configurazione di Val Seriana e lanciare il bootstrap.
```

## Motore iniziale

Comandi gia disponibili:

- `python3 run.py list-areas`
- `python3 run.py resolve-area --query "Val Seriana"`
- `python3 run.py generate-config --query "Val Seriana"`
- `python3 run.py bootstrap --query "Val Seriana" --max-sources 4`
- `python3 run.py analyze ...`

Il caso `Val Seriana` e incluso come area reale di test nel catalogo locale.

## Configurazione

- `project.yaml`: area, categorie, parole chiave, output;
- `sources.yaml`: fonti attive;
- `sources_candidates.yaml`: fonti scoperte ma non validate.

Il repository è ora completamente generico e non contiene riferimenti a territori specifici. Il file `sources.yaml` deve seguire il formato compatibile documentato in [docs/SOURCES_FORMAT.md](docs/SOURCES_FORMAT.md).

Nel setup locale dell'autore, il prompt usato per generare file fonti compatibili è mantenuto anche in:

`/Users/brian/Desktop/Fonti_Generation/PROMPT_generate_compatible_sources.md`

## Affidabilità fonti

- `alta`: comuni, proloco, musei, siti ufficiali;
- `media`: portali e aggregatori;
- `bassa`: social.

Gli eventi trovati solo via social restano non confermati.

## Provider IA

La pipeline funziona anche senza IA. Se il provider scelto non è disponibile, il sistema usa il fallback euristico.

Variabili ambiente attese:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

SDK opzionali:

```bash
pip install openai anthropic google-generativeai
```

## Rendering browser opzionale

Per fonti con JavaScript è possibile impostare `requires_browser: true` in `sources.yaml`.

```bash
pip install playwright
python -m playwright install
```

## Roadmap pubblica

Per rendere il progetto più facile da usare da altri, vedi [docs/PUBLIC_PROJECT.md](docs/PUBLIC_PROJECT.md).
