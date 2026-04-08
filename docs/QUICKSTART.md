# Quickstart

## 1. Clona il repository

```bash
git clone https://github.com/BrianCortinovis/EventGEn.git
cd EventGEn
```

## 2. Crea un ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Prova il motore con Val Seriana

```bash
python3 run.py list-areas
python3 run.py generate-config --query "Val Seriana"
```

## 4. Esegui la pipeline sulla configurazione generata

```bash
python3 run.py analyze --project generated/val-seriana/project.yaml --sources generated/val-seriana/sources.yaml --candidates generated/val-seriana/sources_candidates.yaml --max-sources 4
```

Oppure in un solo passaggio:

```bash
python3 run.py bootstrap --query "Val Seriana" --max-sources 4
```

## 5. Apri l'output

- `events.html`
- `output/events.html`

## 6. Usa un provider IA solo se ti serve

```bash
python3 run.py bootstrap --query "Val Seriana" --provider=openai --max-sources 4
```

Se il provider non è configurato, il sistema continua in fallback euristico.
