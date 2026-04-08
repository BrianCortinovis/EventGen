# EventGen Commands and Area Files

## Area catalog files

Each area file in `catalog/areas/` should define:

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
- `notes`
- `source_seeds`

`source_seeds` should already follow the compatible `sources.yaml` item shape.

## Generation flow

1. Resolve the area from a user query.
2. Load the repo template `project.yaml`.
3. Generate:
   - `area.yaml`
   - `project.yaml`
   - `sources.yaml`
   - `sources_candidates.yaml`
4. Optionally run `analyze`.

## Good first test

Use:

```bash
python3 run.py bootstrap --query "Nome Zona" --provider=claude
```

This is the standard end-to-end validation of the current EventGen motor. Use `--max-sources` only for quick local tests, not for real production-oriented runs.
