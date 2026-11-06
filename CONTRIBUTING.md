# Contributing

Thank you for helping to improve the list! You can contribute in two ways:

- [Open an issue](https://github.com/open-energy-transition/Awesome-Electricity-Demand/issues) to suggest a data source, report a broken link or ask a question.
- Open a pull request that adds or changes a data source, as described below.

## How the list is kept

The list is kept in the [`data/`](data/) folder, and everything else is generated from it:

- `data/sources/<id>.yaml` has one data source, such as `entsoe.yaml` for the ENTSO-E Transparency Platform: its name, page and terms of use, and the countries and subdivisions (the entities) that it has data for, with their years and resolution. A source that [DemandCast](https://github.com/open-energy-transition/demandcast) retrieves has the identifier of its YAML file in DemandCast's `retrievals/electricity_demand_data_sources/` folder; a new one gets a short identifier in lower case, such as the acronym of the provider, or `<first author>_et_al` for the dataset of a paper.
- `data/countries.csv` has every country that the list considers, with its name, continent, population in millions and land area in km² (estimates for 2025), and whether it has been searched for data (`yes` or `no`).

From these files, `scripts/build.py` generates:

- the summary, the tables of data sources and the countries searched without success in [README.md](README.md), between the `<!-- ...:start -->` and `<!-- ...:end -->` markers: do not edit them by hand;
- the [map](https://open-energy-transition.github.io/Awesome-Electricity-Demand/), the list as CSV and JSON, and the figures, which the Pages workflow publishes from `main`.

## Adding or changing a data source

1. Fork the repository and create a branch.
2. Add the countries or subdivisions to the file of the source, or create the file of a new source. Keep the file free of comments; a remark for readers goes in `note`.
3. Set `searched` to `yes` for the country in `data/countries.csv`, if it is not already.
4. Update README.md and check the data with:

   ```bash
   uv run scripts/build.py readme
   ```

   This needs [uv](https://docs.astral.sh/uv/getting-started/installation/). If you cannot run it, say so in the pull request, and a maintainer will update README.md.

5. Open a pull request, with a link to where the licence or terms of use are stated.

For example, `data/sources/cenace.yaml` starts with:

```yaml
name: CENACE
url: https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx
access: public
licence:
  name: All rights reserved
  url: https://www.gob.mx/terminos
  category: restricted
entities:
  - country_code: MEX
    subdivision_code: BCA
    subdivision_name: Baja California
    start: 2016
    end: present
    resolution: 60
```

The fields of a source are:

| Field              | Required | Meaning                                                                          |
| ------------------ | -------- | -------------------------------------------------------------------------------- |
| `name`             | yes      | Name of the source, as shown in the list.                                        |
| `url`              | yes      | Where to download or request the data.                                           |
| `access`           | no       | `public` (the default), or `on-request` if a request or registration is needed. |
| `licence.name`     | yes      | Short description of the terms of use, as shown in the list.                     |
| `licence.url`      | yes      | Page with the full terms.                                                        |
| `licence.category` | yes      | `open`, `non-commercial` or `restricted` (see below).                            |
| `entities`         | yes      | The countries and subdivisions with data, with the fields below.                 |

The fields of an entity are:

| Field                                  | Required | Meaning                                                                          |
| -------------------------------------- | -------- | -------------------------------------------------------------------------------- |
| `country_code`                         | yes      | [ISO 3166-1 alpha-3 code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) of the country, such as `DEU`; Kosovo uses `XKX`. |
| `subdivision_code`, `subdivision_name` | no       | The subdivision or grid region covered, for data of only part of the country.   |
| `start`                                | yes      | First year with data.                                                            |
| `end`                                  | yes      | Last year with data, or `present` if the data is still updated.                  |
| `resolution`                           | yes      | Time step in minutes, such as 5, 15, 30 or 60.                                   |
| `url`                                  | no       | Page of the data of this entity, if it is not the `url` of the source.          |
| `note`                                 | no       | Remark shown in the list, such as "Generation, proxy for demand".                |

- `subdivision_code` is the [ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2) code without the country prefix (`NSW` for New South Wales). For grid regions without one, use the code that DemandCast uses (`CAL` for the California region of the EIA), so that the two lists can be compared.
- `licence.category` sorts the terms:
  - `open`: any use, possibly with attribution (CC-BY, CC0, open data licences);
  - `non-commercial`: only non-commercial use (CC BY-NC, non-commercial reproduction);
  - `restricted`: personal use, all rights reserved, or use only with an authorisation.
- Only hourly or sub-hourly data belongs to the list, so `resolution` must divide 60 minutes.
- If the data of an entity changes resolution over time, list each period as a separate entity.

The checks reject unknown fields and countries, years in the wrong order or in the future, entities listed twice, entity URLs that repeat the URL of their source, and subdivision codes with two names, and list every problem at once.

## Keeping the list in sync with DemandCast

Every data source that [DemandCast](https://github.com/open-energy-transition/demandcast) retrieves should be in this list, with the identifier of its YAML file in DemandCast, and with the same countries, subdivisions, years and terms of use. The list can have more: its sources that DemandCast does not retrieve yet are the backlog of DemandCast. So add a source here first, then its retriever in DemandCast.

`scripts/demandcast_sync.py` compares the two repositories, and never fails because they differ:

- On pull requests that change `data/`, it adds warnings to the changed files, and a comment and the `demandcast-sync` label when the pull request adds or resolves differences. Merge it if the change is genuine.
- On `main`, after each change of `data/` and every month, it keeps the [`demandcast-sync` issue](https://github.com/open-energy-transition/Awesome-Electricity-Demand/issues?q=label%3Ademandcast-sync) open with the divergences, until one of the repositories changes.

It reports as divergences:

- a source of DemandCast that the list does not have, and an entity (country or subdivision) of DemandCast that its source in the list does not have;
- a subdivision named differently;
- years of DemandCast outside those of the list, and data that only one of them says is still updated (a last day of DemandCast in the current year agrees with `present`; a first day in December counts in the next year, and a last day in January in the year before, since many series start or end with a few days in UTC);
- data that DemandCast redistributes and the list calls `restricted`, or that DemandCast does not redistribute and the list calls `open`.

It also notes the sources that DemandCast does not retrieve yet, the different pages of terms, and the years of the list that DemandCast does not have: a retriever may use only part of a series, but these years are worth checking.

A divergence that is deliberate, such as a retriever that takes only some years of a source, goes in `data/demandcast_differences.yaml`, with the check, the entity if any, and a reason:

```yaml
differences:
  - source: aeso
    check: years
    entity: CAN-AB
    reason: Why the two repositories differ, with a link to the evidence.
```

It is then reported as accepted, and noted when it is no longer found, so that it can be removed. To compare with a copy of DemandCast:

```bash
uv run scripts/demandcast_sync.py --demandcast ../demandcast/demandcast/retrievals/electricity_demand_data_sources --output sync
```

## Checking the links

`scripts/check_links.py` requests every link of the data files: the page and the terms of each source, and the pages of its entities. A link is:

- **ok** if it answers;
- **broken** if it answers with a client error, such as 404;
- **unreachable** if its server fails, times out or cannot be reached;
- **blocked** if the website refuses automated requests (401, 403 or 429), which says nothing about the page;
- **unverifiable** if only a browser can check it: its website answers a missing page with the same page, as applications that render their pages in the browser do, or its certificate can only be verified by a browser.

Every week, the check of all the links keeps the [`link-check` issue](https://github.com/open-energy-transition/Awesome-Electricity-Demand/issues?q=label%3Alink-check) open with the links that are broken or unreachable in two checks in a row, and lists the others for review. On pull requests that change `data/sources/`, it checks the links that they add, and reports those that fail as warnings. A failing link never fails CI. To check the links locally:

```bash
uv run scripts/check_links.py --output link-check
```

## Changing the scripts

The scripts in `scripts/` use Python 3.12+ and [uv](https://docs.astral.sh/uv/). Run the checks before you open a pull request: CI runs them all.

```bash
uv run pytest                              # run the tests
uv run mypy                                # check the types
uv run scripts/build.py site _site         # build the site into _site/
uvx pre-commit install                     # run the hooks before each commit
uvx pre-commit run --all-files             # run them on the whole repository
```

To see the map, serve the built site, for example with `python -m http.server --directory _site`, and open <http://localhost:8000>.

Follow the existing style:

- [Ruff](https://docs.astral.sh/ruff/) formatting and linting, with lines of at most 79 characters (72 for docstrings and comments), and type hints, checked by mypy. Import datetime and Matplotlib as `dt` and `plt`.
- Write docstrings following [PEP 257](https://peps.python.org/pep-0257/) and [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html). Start each file with a descriptive, concise, clear and simple docstring (or comment, for files that are not Python) that states what the module does and the data behind it. The docstring of each function, class and test states what it does, with the reasons and data facts that apply only to it in a Notes section. Add inline comments only for lines a reader would otherwise misread, never to explain ordinary behaviour or to repeat a docstring. Comments, docstrings and documentation describe the current code, with no history of changes and no comparisons with other code: those belong in commit messages and pull requests.
- Tests must not use the network, and write files to `tmp_path`.
- Change dependencies in `pyproject.toml` and run `uv lock`; never edit `uv.lock` by hand.

## Commits and pull requests

### Sign off your commits (DCO)

Every commit must be signed off to certify that you have the right to submit it under the project's license, as described in the [Developer Certificate of Origin](https://developercertificate.org/). Add `-s` when committing:

```bash
git commit -s -m "feat(data): add Malaysia"
```

This appends `Signed-off-by: Your Name <your@email>` to the commit message, using your git name and email. If you forgot, sign off all the commits of your branch and update your pull request:

```bash
git rebase --signoff origin/main
git push --force-with-lease
```

When you commit on GitHub's website, GitHub signs off your commits for you.

### Pull request titles

Pull requests are squash-merged, and their title becomes the commit message on `main`. Titles must follow [Conventional Commits](https://www.conventionalcommits.org/): `type(optional scope): description`, for example:

- `feat(data): add Malaysia`
- `fix(data): update the ENTSO-E links`
- `fix(map): show every source of a country`

Common types are `feat`, `fix`, `docs`, `test`, `refactor`, `build`, `ci` and `chore`.

### Review

A maintainer reviews every pull request. Before it is merged, all CI checks must pass and every review conversation must be resolved. Please keep pull requests focused: several small ones are easier to review than a large one.

### AI-assisted contributions

You may use AI tools to help with your contribution, provided that you say so in the pull request description (which tool, and for what), that you have reviewed and checked every change, and that you are responsible for the contribution: your DCO sign-off certifies that you have the right to submit it.
