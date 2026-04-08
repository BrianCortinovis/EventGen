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

1. duplica `sources.yaml`;
2. compila le sorgenti nel formato compatibile;
3. aggiorna `known_municipalities` e `theme` in `project.yaml`;
4. esegui di nuovo `python3 run.py`.
