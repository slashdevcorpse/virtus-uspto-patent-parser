# virtus-uspto-patent-parser

This repo is the Virtus fork of the upstream project. Virtus uses it as a Python wheel in the USPTO stage of the
corpus ETL: it parses the patent grant full text of the USPTO bulk data (APS TXT 1976-2001, XML v2 2002-2004,
XML v4 2005 and later).

- Upstream: https://github.com/TamerKhraisha/uspto-patent-data-parser (licence MIT).
- Base: upstream `master` at `3d3e0868760dfa97c9b13a45c3520202b322cbff` (2020-09-07; upstream has no version and
  no tags).

## Branches

- `master` is equal to upstream `master`. Only a fast-forward from upstream moves it.
- `virtus` holds our patches as separate commits on top of an upstream commit.

## Patches

One line for each commit on `virtus` that is not in upstream:

1. `Build a wheel and an sdist with uv build`: `pyproject.toml` with the hatchling backend (upstream has no
   packaging; `uv_build` cannot package the single-file module `uspto.py`). The wheel holds the upstream layout
   unchanged: the top-level module `uspto` and the top-level package `parsers`. The sdist leaves out
   `documentation/` (a 49 MB PDF).
2. `Add a smoke test that parses a small XML v4 fixture`: `tests/test_smoke.py` and
   `tests/fixtures/ipg_two_grants.xml` (two synthetic grants, hand-written, no publisher data).
3. `Add the release workflow of the virtus fork`: `.github/workflows/virtus-release.yml`.
4. `Add VIRTUS.md`: this file.

No patch changes the upstream code. The upstream files are where upstream has them, so a sync merge does not
conflict with a patch.

## Library use

```python
import uspto

grants = uspto.read_and_parse_file_from_disk("ipg200107.xml", ["INVT", "ABST", "CLMS"], "xml4")
```

The import names are the upstream ones: `uspto` and `parsers`. The functions that download from
`bulkdata.uspto.gov` (`read_and_parse_yearly_data`, `download_yearly_data`, `read_and_parse_from_url` and the
`read_data_from_url_*` functions) make their own `requests` calls with no pacing and no User-Agent. The Virtus ETL
does not call them; it downloads with its own paced client and gives the files or the XML text to the parse
functions.

## Release

1. Increase `<n>` in the `pyproject.toml` version `<upstream version>+virtus.<n>`. Upstream has no version, so
   `<upstream version>` is `0.0.0`.
2. Tag the `virtus` commit `v<upstream version>+virtus.<n>` and push the tag.
3. The workflow `virtus-release` checks that the tag equals the version, builds the wheel and the sdist with
   `uv build`, runs the smoke test against the wheel, and publishes both with one `SHA256SUMS` as the release
   assets of the tag.
4. In `virtus`, run `tools/pins/bump.py virtus-uspto-patent-parser <tag>`.

## Sync with upstream

1. Fast-forward `master` to upstream `master`:
   `git fetch upstream && git push origin upstream/master:master`.
2. Merge `master` into `virtus` (never rebase `virtus`). Solve the conflicts in the patch commits.
3. If upstream added a module or a package, add it to `only-include` in `pyproject.toml`. If upstream added a
   dependency, add it to `dependencies`.
4. Run the smoke test against the built wheel, as the release workflow does:
   `uv build --out-dir dist`, then in `tests/`:
   `uv run --isolated --no-project --with ../dist/<wheel> --with pytest pytest --import-mode=importlib .`
5. Update "Base" in this file. If upstream starts to publish a version, set the version to
   `<upstream version>+virtus.1`.
6. Do a release.
