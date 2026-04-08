# Quickstart

## 1. Clona il repository

```bash
git clone https://github.com/BrianCortinovis/EventGen.git
cd EventGen
```

## 2. Crea un ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Prepara un file area locale

```bash
python3 run.py list-areas
python3 run.py generate-config --query "Nome Zona"
```

Il repository non include aree reali di esempio. Puoi tenere i tuoi file in `catalog/areas/` localmente oppure usare `--catalog /percorso/alla/tua/cartella-aree`.

## 4. Esegui la pipeline sulla configurazione generata

```bash
python3 run.py analyze --project generated/nome-zona/project.yaml --sources generated/nome-zona/sources.yaml --candidates generated/nome-zona/sources_candidates.yaml --provider=claude
```

Oppure in un solo passaggio:

```bash
python3 run.py bootstrap --query "Nome Zona" --provider=claude
```

## 5. Apri l'output

- `events.html`
- `output/events.html`

## 6. Scegli un provider IA via CLI

```bash
python3 run.py bootstrap --query "Nome Zona" --provider=openai
python3 run.py bootstrap --query "Nome Zona" --provider=claude
python3 run.py bootstrap --query "Nome Zona" --provider=gemini
```

La pipeline usa sempre un provider IA CLI. Le euristiche locali servono da supporto, non da sostituto.

`--max-sources` va usato solo per test rapidi. Nel flusso normale è meglio processare tutte le fonti attive.
