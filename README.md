# EventGEn

Base di partenza per costruire un'app desktop completa che generi aree, scopra fonti compatibili e analizzi eventi pubblici da fonti web e social.

[Quickstart](docs/QUICKSTART.md) | [Configurazione](docs/CONFIGURATION.md) | [Formato sources.yaml](docs/SOURCES_FORMAT.md)

## Obiettivo

Questo repository nasce come evoluzione del motore locale già costruito: da qui vogliamo arrivare a un'app desktop integrata che permetta di selezionare una zona, generare un file fonti compatibile, analizzare le fonti e produrre un output eventi usabile anche da utenti non tecnici.

## Stato attuale

Al momento il repository contiene ancora il motore locale lineare:

- `run.py` per eseguire la pipeline;
- configurazione via `project.yaml` e `sources.yaml`;
- parsing, analisi, deduplica e rendering HTML;
- supporto a provider IA opzionali con fallback euristico.

## Direzione del progetto

I prossimi blocchi di sviluppo previsti qui dentro sono:

1. motore di selezione area o territorio;
2. generatore di `sources.yaml` compatibile;
3. integrazione tra generatore fonti e source analyzer;
4. successiva UX desktop con avvio da icona.

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
python3 run.py
```

Con provider IA opzionale:

```bash
python3 run.py --provider=openai
python3 run.py --provider=claude
python3 run.py --provider=gemini
```

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
