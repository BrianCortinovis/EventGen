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
python3 run.py resolve-area --query "Val Seriana"
```

### Generare la configurazione

```bash
python3 run.py generate-config --query "Val Seriana"
```

Output generato di default:

- `generated/val-seriana/area.yaml`
- `generated/val-seriana/project.yaml`
- `generated/val-seriana/sources.yaml`
- `generated/val-seriana/sources_candidates.yaml`

### Bootstrap completo

```bash
python3 run.py bootstrap --query "Val Seriana" --max-sources 4
```

Questo comando:

1. risolve l'area;
2. genera la configurazione;
3. lancia subito la pipeline di analisi.

## Caso di test attuale

Il motore include una prima area reale:

- `Val Seriana`

Serve come test del flusso end-to-end e come modello per aggiungere nuove aree.
