# AGENTS.md

Instructions for AI coding agents working on Awesome Electricity Demand. Human contributors should read [CONTRIBUTING.md](CONTRIBUTING.md).

## Project

A curated list of hourly and sub-hourly electricity demand data, by country and subdivision. The list is kept as data files, from which a Python script generates the tables of README.md, an interactive map, the list as CSV and JSON, and figures of its coverage. It is a Python 3.12+ project managed with [uv](https://docs.astral.sh/uv/). Its sister project, [DemandCast](https://github.com/open-energy-transition/demandcast), downloads the data of many of these sources.

## Layout

- `data/sources/<id>.yaml`: one data source each, with its terms of use and its entities (countries and subdivisions, with their years and resolution), named after the YAML file of the source in DemandCast when there is one. `data/countries.csv`: every country considered, with its continent, population and land area. Their format is described once, in [CONTRIBUTING.md](CONTRIBUTING.md#adding-or-changing-a-data-source).
- `data/demandcast.yaml`: the countries and subdivisions of each source whose series DemandCast retrieves, which the README marks with ✅. Write it with `scripts/demandcast_sync.py --update-marks`, never by hand.
- `data/shapes.geojson`: the outlines of the countries and subdivisions for the interactive map and the map of the figures. Write it with `scripts/shapes.py`, which runs in the environment of DemandCast (see CONTRIBUTING.md), never by hand.
- `scripts/registry.py`: the pydantic models that load and validate the data files, and flatten them into one `Series` per entity of a source. `scripts/build.py`: generates the blocks of README.md and builds the site. `scripts/figures.py`: the figures of the site, each in a light and a dark version. `scripts/shapes.py`: writes `data/shapes.geojson` with the code of DemandCast. `scripts/check_links.py`: checks the links of the data files. `scripts/demandcast_sync.py`: compares the sources with those of DemandCast; `data/demandcast_differences.yaml` lists the deliberate differences, each with a reason.
- `site/`: the static files of the site, the interactive map (`index.html`, `map.js`, `map.css`), which draws `map.geojson` and lists the data sources from `sources.json`, both written next to it by `scripts/build.py site`.
- `tests/`: the pytest suite, with a small data folder in `conftest.py`.
- `.github/workflows/`: `ci.yml` runs the hooks, the tests and mypy, and checks README.md; `pages.yml` builds and deploys the site from `main`, and monthly; `demandcast-sync.yml` compares with DemandCast and keeps the `demandcast-sync` issue, and `demandcast-sync-comment.yml` comments on pull requests that change the divergences; `link-check.yml` checks the links every week, keeping the `link-check` issue, and the links that pull requests add.

## Commands

```bash
uv run scripts/build.py readme       # validate the data and update README.md
uv run scripts/build.py check        # fail if the data is invalid or README.md is stale
uv run scripts/build.py site _site   # build the site
uv run scripts/check_links.py --output link-check   # check the links (network)
uv run pytest                        # run the tests
uv run mypy                          # check the types
uvx pre-commit run --all-files       # lint, format and check everything
```

Run the tests, mypy and the pre-commit hooks before you finish: CI runs them all.

## Conventions

- Ruff formatting and linting, with lines of at most 79 characters (72 for docstrings and comments), NumPy-style docstrings and type hints, checked by mypy. Import datetime and Matplotlib as `dt` and `plt`.
- Docstrings follow PEP 257 and numpydoc. Each file starts with a descriptive, concise, clear and simple docstring (or comment, for files that are not Python) that states what the module does and the data behind it. The docstring of each function, class and test states what it does, with the reasons and data facts that apply only to it in a Notes section. Inline comments are only for lines a reader would otherwise misread, never to explain ordinary behaviour or to repeat a docstring. Comments, docstrings and documentation describe the current code, with no history of changes and no comparisons with other code: those belong in commit messages and pull requests.
- Never edit the generated blocks of README.md: change the data files and run `uv run scripts/build.py readme`.
- Keep the data files free of comments. Name a source after its YAML file in DemandCast, and give non-standard subdivisions, those without an ISO 3166-2 code, a commonly accepted and recognizable code and name, the same in both repositories.
- Do not change a URL, a licence or the years of a source without a source for the change, and say in the pull request where the information comes from.
- Every source of DemandCast must be in the list: add a source here before its retriever in DemandCast. Differences from DemandCast never fail CI; resolve them in either repository, or accept them with a reason in `data/demandcast_differences.yaml`.
- Tests must not use the network, and write files to `tmp_path`.
- Change dependencies in `pyproject.toml` and run `uv lock`; never edit `uv.lock` by hand.

## Pull requests

- Titles follow [Conventional Commits](https://www.conventionalcommits.org/), e.g. `feat(data): add Malaysia`.
- Every commit needs a DCO `Signed-off-by` line from the human contributor. Do not add it on their behalf unless they explicitly ask you to.
- Keep pull requests focused, and say in the description which AI tools were used and for what.
- The ruleset of `main` requires the checks `CI result`, `Conventional Commits title`, `DCO sign-off` and `dependency-review`, the CodeQL results, and a review by the code owners.
