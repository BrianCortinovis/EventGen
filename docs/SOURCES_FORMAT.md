# Formato compatibile di `sources.yaml`

Questo progetto si aspetta un file `sources.yaml` compatibile con la struttura seguente.

```yaml
version: 1
project: <slug progetto>
region: <regione>
country: <codice paese>
notes: <nota generale>
defaults:
  enabled: true
  fetch_mode: auto
  output_language: it
  confidence_policy:
    official: high
    aggregator: medium
    social: low
  social_policy:
    discovery_only: true
    requires_confirmation: true
sources:
  - id: <slug_univoco>
    name: <nome leggibile>
    type: <portal|institution|aggregator|proloco|comune|museum|local_portal|cultural_portal|attraction|social>
    subtype: <sottotipo leggibile>
    active: true
    discovery_only: <true|false>
    url: <url assoluto>
    area: <area o territorio>
    municipality: <comune o null>
    categories_hint: [lista, di, categorie]
    priority: <1-10>
    trust_level: <high|medium|low>
    parsing_profile: <auto|social>
    notes: <nota>
```

## Regole

1. Includi solo fonti rilevanti per eventi pubblici.
2. Escludi siti di news generiche, cronaca e contenuti editoriali.
3. I social devono essere sempre `type: social` e `discovery_only: true`.
4. Le fonti ufficiali o primarie devono avere `trust_level: high`.
5. Usa `priority` alta per le fonti core e bassa per il discovery.
6. Non inventare URL.
7. Se non sei sicuro del comune, usa `municipality: null`.

## Prompt di generazione

Nel setup locale dell'autore, il prompt usato per produrre file compatibili è mantenuto anche in:

`/Users/brian/Desktop/Fonti_Generation/PROMPT_generate_compatible_sources.md`

Se usi solo il repository pubblico, questa pagina è già la specifica necessaria per creare `sources.yaml`.
