# Quickstart

## 1. Clona il repository

```bash
git clone https://github.com/BrianCortinovis/event-source-analyzer.git
cd event-source-analyzer
```

## 2. Crea un ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Adatta la configurazione

- modifica `project.yaml`;
- genera o compila `sources.yaml` nel formato compatibile descritto in `docs/SOURCES_FORMAT.md`;
- lascia `sources_candidates.yaml` per le fonti da validare.

## 4. Esegui la pipeline

```bash
python3 run.py
```

## 5. Apri l'output

- `events.html`
- `output/events.html`

## 6. Usa un provider IA solo se ti serve

```bash
python3 run.py --provider=openai
```

Se il provider non è configurato, il sistema continua in fallback euristico.
