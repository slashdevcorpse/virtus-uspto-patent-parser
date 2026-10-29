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

1. `Build a wheel and an sdist with uv build`: `pyproject.toml` (upstream has no packaging). Patch 5 replaces
   its backend and layout.
2. `Add a smoke test that parses a small XML v4 fixture`: `tests/test_smoke.py` and
   `tests/fixtures/ipg_two_grants.xml` (two synthetic grants, hand-written, no publisher data).
3. `Add the release workflow of the virtus fork`: `.github/workflows/virtus-release.yml`.
4. `Add VIRTUS.md`: this file.
5. `Move the code into the uspto_patent_parser package`: `git mv` of `uspto.py` to
   `uspto_patent_parser/__init__.py` and of `parsers/` to `uspto_patent_parser/parsers/`; the three imports of the
   parsers become relative (decision D-122: a top-level `parsers` package collides in site-packages). The
   `uv_build` backend builds the wheel from the package; the sdist keeps `tests/` and leaves out `documentation/`
   (a 49 MB PDF).
6. `Add an APS TXT fixture to the smoke test`: `tests/fixtures/aps_two_grants.txt` (two synthetic grants,
   hand-written).
7. `Update VIRTUS.md for the uspto_patent_parser package`: this file.

Apart from the moves and the relative imports of patch 5, no patch changes the upstream code.

## Library use

```python
import uspto_patent_parser

grants = uspto_patent_parser.read_and_parse_file_from_disk("ipg200107.xml", ["INVT", "ABST", "CLMS"], "xml4")
```

`uspto_patent_parser` has the functions that `from uspto import *` gives upstream (the upstream README). The
parsers are `uspto_patent_parser.parsers.parse_txt_file`, `parse_xml_v2_file` and `parse_xml_v4_file`. The
functions that download from `bulkdata.uspto.gov` (`read_and_parse_yearly_data`, `download_yearly_data`,
`read_and_parse_from_url` and the `read_data_from_url_*` functions) make their own `requests` calls with no pacing
and no User-Agent. The Virtus ETL does not call them; it downloads with its own paced client and gives the files or
the XML text to the parse functions.

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
2. Merge `master` into `virtus` (never rebase `virtus`). Git follows the renames of patch 5 for changes to
   existing files. Move a new upstream file into `uspto_patent_parser/` with `git mv` and make its imports of
   `parsers` relative.
3. If upstream added a dependency, add it to `dependencies` in `pyproject.toml`.
4. Run the smoke test against the built wheel, as the release workflow does:
   `uv build --out-dir dist`, then in `tests/`:
   `uv run --isolated --no-project --with ../dist/<wheel> --with pytest pytest --import-mode=importlib .`
5. Update "Base" in this file. If upstream starts to publish a version, set the version to
   `<upstream version>+virtus.1`.
6. Do a release.
