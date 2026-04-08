# Contributing

Grazie per l'interesse nel progetto.

## Come contribuire

1. Apri una issue o descrivi il problema che vuoi risolvere.
2. Mantieni le modifiche piccole e leggibili.
3. Evita di introdurre architetture complesse, scheduler automatici o dipendenze pesanti senza motivo forte.
4. Mantieni la pipeline lineare: fetch, parsing, analisi, deduplica, rendering.
5. Non trattare i social come fonti di conferma.
6. Considera in perimetro anche nightlife, bar, discoteche, bowling, concerti e intrattenimento pubblico, purché siano veri eventi con data.

## Cosa valutiamo con priorità

- correttezza dei dati;
- riduzione dei falsi positivi;
- miglioramento della configurabilità;
- qualità dei metadata per export sito, SEO e analytics;
- documentazione chiara per nuove aree geografiche e nuovi temi;
- test leggeri e verifiche ripetibili.

## Prima di aprire una pull request

Esegui almeno:

```bash
python3 -m py_compile run.py event_pipeline/*.py eventgen_engine/*.py
```

Se stai facendo una run reale, usa un provider IA CLI e processa tutte le fonti attive. `--max-sources` è ammesso solo per test rapidi.

Se il progetto viene adattato a una nuova area:

- aggiungi o aggiorna esempi di configurazione;
- documenta le fonti usate;
- segnala limiti noti e possibili falsi positivi.
