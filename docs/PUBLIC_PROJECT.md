# Come renderlo davvero pubblico e usabile da altri

Il progetto è già pubblicabile come repository open source, ma per essere davvero usabile da altri servono alcune scelte di prodotto e manutenzione.

## Già pronto

- esecuzione locale semplice;
- configurazione esterna;
- licenza MIT;
- documentazione base;
- landing page statica per GitHub Pages;
- workflow GitHub per CI e Pages.

## Per renderlo adottabile da altri

### 1. Stabilizzare l'onboarding

- mantenere il quickstart corto e testato;
- fornire una specifica chiara per generare `sources.yaml` in modo coerente;
- evitare istruzioni implicite o passaggi manuali nascosti.

### 2. Rendere chiari i limiti

- spiegare che i social sono solo discovery;
- documentare i casi tipici di falsi positivi;
- chiarire che alcuni siti dinamici richiedono Playwright.

### 3. Migliorare la qualità del parsing

- aggiungere casi di test su HTML reali;
- mantenere parser semplici e leggibili;
- evitare overfitting su un solo territorio.

### 4. Rendere il progetto estendibile

- aggiungere template YAML per nuovi domini;
- documentare come aggiungere nuovi parser;
- mantenere la logica base separata dalla configurazione locale.

### 5. Costruire fiducia pubblica

- mostrare esempi reali di output;
- pubblicare una roadmap corta;
- aggiungere issue template e discussioni se il progetto cresce.

## Buon assetto open source minimo

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `docs/`
- `sources_candidates.yaml`
- esempio configurazioni

## Prossimi miglioramenti consigliati

1. aggiungere test automatici su parser e deduplica;
2. aggiungere un file `pyproject.toml` per packaging leggero;
3. creare una cartella `examples/` con più territori;
4. pubblicare una demo HTML aggiornata via GitHub Pages;
5. aggiungere una modalità `--sources path.yaml` ben documentata per casi multipli.
