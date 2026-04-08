# Motore Aree e Generazione Config

EventGen ora include un primo motore operativo per:

- risolvere un'area da query testuale;
- generare un `project.yaml` area-specifico;
- generare un `sources.yaml` compatibile;
- arricchire gli eventi con testo descrittivo, immagini, flyer e link YouTube;
- lanciare la pipeline sulla configurazione generata.

## Catalogo aree

Le aree catalogate stanno in:

`catalog/areas/`

Ogni file area contiene:

- slug e nome;
- alias;
- regione, provincia, paese;
- centro e raggio indicativo;
- comuni noti;
- etichette di ricerca;
- seed sources iniziali.

## Comandi principali

### Elencare le aree disponibili

```bash
python3 run.py list-areas
```

### Risolvere una zona

```bash
python3 run.py resolve-area --query "Nome Zona"
```

### Generare la configurazione

```bash
python3 run.py generate-config --query "Nome Zona"
```

Output generato di default:

- `generated/nome-zona/area.yaml`
- `generated/nome-zona/project.yaml`
- `generated/nome-zona/sources.yaml`
- `generated/nome-zona/sources_candidates.yaml`

### Bootstrap completo

```bash
python3 run.py bootstrap --query "Nome Zona" --provider=claude
```

Questo comando:

1. risolve l'area;
2. genera la configurazione;
3. lancia subito la pipeline di analisi.

## Note repository

Il repository pubblico non include aree reali versionate. I file area stanno di norma in `catalog/areas/` solo nel tuo ambiente locale oppure in una cartella esterna passata via `--catalog`.
