# Configurazione

## `project.yaml`

Definisce il dominio del progetto:

- nome e descrizione;
- area o tema di riferimento;
- timezone;
- categorie;
- parole chiave di inclusione;
- parole chiave di esclusione;
- comuni noti;
- output HTML.

## `catalog/areas/*.yaml`

Definisce una zona riutilizzabile per il motore EventGen.

Campi principali:

- `slug`
- `name`
- `aliases`
- `area_type`
- `region`
- `province`
- `country`
- `center`
- `radius_km`
- `municipalities`
- `search_labels`
- `source_seeds`

## `sources.yaml`

Contiene le fonti attive e deve seguire il formato compatibile descritto in [SOURCES_FORMAT.md](SOURCES_FORMAT.md).

Campi principali per ogni sorgente:

- `id`
- `name`
- `url`
- `type`
- `subtype`
- `area`
- `municipality`
- `categories_hint`
- `priority`
- `trust_level`
- `parsing_profile`
- `notes`

Campi opzionali:

- `requires_browser`
- `discovery_only`
- `active`

## `sources_candidates.yaml`

Serve per salvare nuove fonti suggerite dal sistema, ma non ancora approvate.

Il progetto non deve attivarle automaticamente.

## Tipi di fonte supportati

- `portale`
- `comune`
- `proloco`
- `museo`
- `social`
- `aggregatore`

## Uso pratico

Per adattarlo a un territorio o a un tema:

1. aggiungi o modifica un file in `catalog/areas/`;
2. genera la configurazione con `python3 run.py generate-config --query "<area>"`;
3. controlla il `sources.yaml` generato;
4. lancia l'analisi con `python3 run.py analyze ...`.
