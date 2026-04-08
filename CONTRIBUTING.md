# Contributing

Grazie per l'interesse nel progetto.

## Come contribuire

1. Apri una issue o descrivi il problema che vuoi risolvere.
2. Mantieni le modifiche piccole e leggibili.
3. Evita di introdurre architetture complesse, scheduler automatici o dipendenze pesanti senza motivo forte.
4. Mantieni la pipeline lineare: fetch, parsing, analisi, deduplica, rendering.
5. Non trattare i social come fonti di conferma.

## Cosa valutiamo con priorità

- correttezza dei dati;
- riduzione dei falsi positivi;
- miglioramento della configurabilità;
- documentazione chiara per nuove aree geografiche e nuovi temi;
- test leggeri e verifiche ripetibili.

## Prima di aprire una pull request

Esegui almeno:

```bash
python3 -m py_compile run.py event_pipeline/*.py
python3 run.py --max-sources 1
```

Se il progetto viene adattato a una nuova area:

- aggiungi o aggiorna esempi di configurazione;
- documenta le fonti usate;
- segnala limiti noti e possibili falsi positivi.
