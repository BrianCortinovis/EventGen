---
name: EventGenCodex
description: Use EventGen as a native Codex workflow to resolve an area, generate compatible project and sources files, and run the local event analysis pipeline. Trigger this skill when the user wants to work on EventGen, generate configs for a territory like Val Seriana, expand the area catalog, or run the terminal engine from inside Codex.
metadata:
  short-description: Native workflow for EventGen
---

# EventGenCodex

Use this skill when working with the repository-local EventGen engine.

Prefer this skill for:

- generating `project.yaml` and `sources.yaml` from a named area;
- extending `catalog/areas/*.yaml`;
- running the EventGen terminal engine from Codex;
- testing real territories such as `Val Seriana`;
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
python3 run.py resolve-area --query "Val Seriana"
```

Generate config:

```bash
python3 run.py generate-config --query "Val Seriana"
```

Bootstrap generate + analyze:

```bash
python3 run.py bootstrap --query "Val Seriana" --max-sources 4
```

Run analyze on existing generated files:

```bash
python3 run.py analyze --project generated/val-seriana/project.yaml --sources generated/val-seriana/sources.yaml --candidates generated/val-seriana/sources_candidates.yaml --max-sources 4
```

## Working rules

- Keep EventGen separate from the earlier analyzer repo.
- Treat the terminal engine as the source of truth for now.
- Do not hardcode a single territory in the core engine.
- Use real seed sources when adding a new area.
- Keep social sources discovery-only.
- Prefer improving the area motor and generation flow before building the desktop UX.

## Validation

After edits:

- run `python3 -m py_compile run.py event_pipeline/*.py eventgen_engine/*.py`
- run at least one area flow such as `Val Seriana`
- verify that generated files appear under `generated/<area-slug>/`
- verify that `events.html` is produced when analysis succeeds

## References

Read [references/commands.md](references/commands.md) when you need the command flow or area-file structure.
