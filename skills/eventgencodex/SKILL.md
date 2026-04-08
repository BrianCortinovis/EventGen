---
name: EventGenCodex
description: Use EventGen as a native Codex workflow to resolve an area, generate compatible project and sources files, and run the local event analysis pipeline. Trigger this skill when the user wants to work on EventGen, generate configs for a territory, expand the area catalog, or run the terminal engine from inside Codex.
metadata:
  short-description: Native workflow for EventGen
---

# EventGenCodex

Use this skill when working with the repository-local EventGen engine.

Prefer this skill for:

- generating `project.yaml` and `sources.yaml` from a named area;
- extending local `catalog/areas/*.yaml`;
- running the EventGen terminal engine from Codex;
- testing real territories from local area files;
- iterating on the future desktop-app motor before the UX exists.

## Repository shape

The important pieces are:

- `run.py`
- `eventgen_engine/`
- `catalog/areas/`
- `event_pipeline/`
- `generated/` for local generated configs and outputs

## Main commands

List areas:

```bash
python3 run.py list-areas
```

Resolve an area:

```bash
python3 run.py resolve-area --query "Nome Zona"
```

Generate config:

```bash
python3 run.py generate-config --query "Nome Zona"
```

Bootstrap generate + analyze:

```bash
python3 run.py bootstrap --query "Nome Zona" --provider=claude
```

Run analyze on existing generated files:

```bash
python3 run.py analyze --project generated/nome-zona/project.yaml --sources generated/nome-zona/sources.yaml --candidates generated/nome-zona/sources_candidates.yaml --provider=claude
```

## Working rules

- Keep EventGen separate from the earlier analyzer repo.
- Treat the terminal engine as the source of truth for now.
- Do not hardcode a single territory in the core engine.
- Use real seed sources when adding a new area.
- Keep social sources discovery-only.
- Cover all public event types in scope, including nightlife, bar, discoteche, bowling, live music and entertainment.
- Import only events that are still active on the execution date; exclude already ended events.
- Use all active sources by default; use `--max-sources` only for quick tests.
- Use a CLI provider (`openai`, `claude`, `gemini`) for real runs. Heuristics support the extraction but do not replace the model.
- Prefer improving the area motor and generation flow before building the desktop UX.

## Validation

After edits:

- run `python3 -m py_compile run.py event_pipeline/*.py eventgen_engine/*.py`
- run at least one local area flow
- verify that generated files appear under `generated/<area-slug>/`
- verify that `events.html` is produced when analysis succeeds

## References

Read [references/commands.md](references/commands.md) when you need the command flow or area-file structure.
