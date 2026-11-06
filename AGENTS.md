# AGENTS.md

Instructions for AI coding agents working on Awesome Electricity Demand. Human contributors should read [CONTRIBUTING.md](CONTRIBUTING.md).

## Project

A curated list of hourly and sub-hourly electricity demand data, by country and subdivision. The list is kept as data files, from which a Python script generates the tables of README.md, an interactive map, the list as CSV and JSON, and figures of its coverage. It is a Python 3.12+ project managed with [uv](https://docs.astral.sh/uv/). Its sister project, [DemandCast](https://github.com/open-energy-transition/demandcast), downloads the data of many of these sources.

## Layout

- `data/sources/<ISO3>.yaml`: the data sources of each country. `data/countries.csv`: every country considered, with its continent, population, land area and whether it has been searched. Their format is described once, in [CONTRIBUTING.md](CONTRIBUTING.md#adding-or-changing-a-data-source).
- `scripts/registry.py`: the pydantic models that load and validate the data files. `scripts/build.py`: generates the blocks of README.md and builds the site. `scripts/figures.py`: the figures of the site.
- `demand-data-map/`: the map, which reads `sources.json` from the built site.
- `tests/`: the pytest suite, with a small data folder in `conftest.py`.
- `.github/workflows/`: `ci.yml` runs the hooks, the tests and mypy, and checks README.md; `pages.yml` builds and deploys the site from `main`, and monthly.

## Commands

```bash
uv run scripts/build.py readme       # validate the data and update README.md
uv run scripts/build.py check        # fail if the data is invalid or README.md is stale
uv run scripts/build.py site _site   # build the site
uv run pytest                        # run the tests
uv run mypy                          # check the types
uvx pre-commit run --all-files       # lint, format and check everything
```

Run the tests, mypy and the pre-commit hooks before you finish: CI runs them all.

## Conventions

- Ruff formatting and linting, with lines of at most 79 characters (72 for docstrings and comments), NumPy-style docstrings and type hints, checked by mypy. Import datetime and Matplotlib as `dt` and `plt`.
- Docstrings follow PEP 257 and numpydoc. Each file starts with a descriptive, concise, clear and simple docstring (or comment, for files that are not Python) that states what the module does and the data behind it. The docstring of each function, class and test states what it does, with the reasons and data facts that apply only to it in a Notes section. Inline comments are only for lines a reader would otherwise misread, never to explain ordinary behaviour or to repeat a docstring. Comments, docstrings and documentation describe the current code, with no history of changes and no comparisons with other code: those belong in commit messages and pull requests.
- Never edit the generated blocks of README.md: change the data files and run `uv run scripts/build.py readme`.
- Keep the data files free of comments. Use the subdivision codes of DemandCast for grid regions without an ISO 3166-2 code.
- Do not change a URL, a licence or the years of a source without a source for the change, and say in the pull request where the information comes from.
- Tests must not use the network, and write files to `tmp_path`.
- Change dependencies in `pyproject.toml` and run `uv lock`; never edit `uv.lock` by hand.

## Pull requests

- Titles follow [Conventional Commits](https://www.conventionalcommits.org/), e.g. `feat(data): add Malaysia`.
- Keep pull requests focused, and say in the description which AI tools were used and for what.
