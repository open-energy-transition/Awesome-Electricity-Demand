# Contributing

Thank you for helping to improve the list! You can contribute in two ways:

- [Open an issue](https://github.com/open-energy-transition/Awesome-Electricity-Demand/issues) to suggest a data source, report a broken link or ask a question.
- Open a pull request that adds or changes a data source, as described below.

## How the list is kept

The list is kept in the [`data/`](data/) folder, and everything else is generated from it:

- `data/sources/<id>.yaml` has one data source, such as `entsoe.yaml` for the ENTSO-E Transparency Platform: its name, page and terms of use, and the countries and subdivisions (the entities) that it has data for, with their years and resolution. A source that [DemandCast](https://github.com/open-energy-transition/demandcast) retrieves has the identifier of its YAML file in DemandCast's `retrievals/electricity_demand_data_sources/` folder; a new one gets a short identifier in lower case, such as the acronym of the provider, or `<first author>_et_al` for the dataset of a paper.
- `data/country_totals.csv` has every country that the list considers, with its name, continent, and its population in millions and land area in km² (estimates for 2025).
- `data/demandcast.yaml` lists, for each source, the countries and subdivisions whose series [DemandCast](https://github.com/open-energy-transition/demandcast) retrieves, which the list marks with ✅. It is written by a command (see below), not by hand.
- `data/shapes.geojson` has the outlines of every country and of each subdivision of the list, for the interactive map and the map of the figures, and for each country with subdivisions, the shares of its people and of its land inside their outlines, for the figure of the coverage. It is written by a command (see below), not by hand.

From these files, `scripts/build.py` generates:

- the summary and the tables of data sources (one per continent, folded, with a row for the subdivisions of a source that share their years and resolution, the category of their terms as 🟢 open, 🟡 non-commercial or 🔴 restricted, 🔒 for access on request, and ✅ for the series that DemandCast retrieves) in [README.md](README.md), between the `<!-- ...:start -->` and `<!-- ...:end -->` markers: do not edit them by hand;
- the [site](https://open-energy-transition.github.io/Awesome-Electricity-Demand/), which the Pages workflow publishes from `main` and every month: the interactive map of `site/`, which draws the outlines of `map.geojson`, coloured by their years of data, and lists the data sources of a country or subdivision from `sources.json`; the list as CSV and JSON; and the figures, in a light and a dark version that the README shows according to the reader's theme. To see the site locally, build and serve it:

  ```bash
  uv run scripts/build.py site _site
  python -m http.server --directory _site
  ```

## Adding or changing a data source

1. Fork the repository and create a branch.
2. Add the countries or subdivisions to the file of the source, or create the file of a new source. Keep the file free of comments; a remark for readers goes in `note`. Write its terms of use as [described below](#terms-of-use).
3. Update README.md and check the data with:

   ```bash
   uv run scripts/build.py readme
   ```

   This needs [uv](https://docs.astral.sh/uv/getting-started/installation/). If you cannot run it, say so in the pull request, and a maintainer will update README.md.

4. Open a pull request, with a link to where the terms of use are stated and the sentences of the terms that decide their category, in their language and translated if needed.

For example, `data/sources/cenace.yaml` starts with:

```yaml
name: CENACE
url: https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx
access: public
licence:
  name: Personal use
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
| `licence.name`     | yes      | What the terms allow, in the words of the list (see below).                      |
| `licence.url`      | yes      | Page where the source states its terms, or the record of a dataset with its licence. |
| `licence.category` | yes      | `open`, `non-commercial` or `restricted` (see below).                            |
| `entities`         | yes      | The countries and subdivisions with data, with the fields below.                 |

The fields of an entity are:

| Field                                  | Required | Meaning                                                                          |
| -------------------------------------- | -------- | -------------------------------------------------------------------------------- |
| `country_code`                         | yes      | [ISO 3166-1 alpha-3 code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) of the country, such as `DEU`; Kosovo uses `XKX`. |
| `subdivision_code`, `subdivision_name` | no       | The subdivision covered, for data of only part of the country (see below).      |
| `start`                                | yes      | First year with data.                                                            |
| `end`                                  | yes      | Last year with data, or `present` if the data is still updated.                  |
| `resolution`                           | yes      | Time step in minutes, such as 5, 15, 30 or 60.                                   |
| `url`                                  | no       | Page of the data of this entity, if it is not the `url` of the source.          |
| `note`                                 | no       | Remark shown in the list, such as "Generation, proxy for demand".                |

- An entity is a country or a subdivision of a country. A subdivision is either standard, with an [ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2) code, such as a state or a province, or non-standard, such as the area of a grid or of a bidding zone.
- `subdivision_code` is the ISO 3166-2 code of a standard subdivision, without the country prefix (`NSW` for New South Wales). A non-standard subdivision takes a code and a name that are commonly accepted and recognizable, such as those of its operator (`CAL` and California for the region of the EIA, `QLD1` and Queensland region of the NEM, `SIN` and National Interconnected System for Colombia). DemandCast uses the same code, so that the two lists can be compared.
- An entity is the area whose demand its data measures, so that neither the list nor its map claims more:
  - A country covers all of it. Data of only part of a country, even of most of it, belongs to the subdivision it covers, standard or non-standard.
  - An entity can still include an area left out of the data if that area has less than 1% of the demand of the country (or of its population, when the demand is not known) and less than 1% of its land, or if it is too scattered to draw on a map of the world, such as isolated villages or small islands. The note names the area when it is known, such as "Without the isolated systems of the Amazon".
  - When a source publishes data for several subdivisions and for their total, list the subdivisions, with a note that says the source also publishes their total. List the total only for the years or the resolution that the subdivisions do not have, or when it covers more than them.
  - When the area of the data changes over time beyond these limits, as when an isolated system joins the grid, list each period as a separate entity, with its own subdivision. A smaller change goes in the note.
- Only hourly or sub-hourly data belongs to the list, so `resolution` must divide 60 minutes.
- If the data of an entity changes resolution over time, list each period as a separate entity.

The checks reject unknown fields and countries, years in the wrong order or in the future, entities listed twice, entity URLs that repeat the URL of their source, subdivision codes with two names, and terms of use not written in the words of their category (see below), and list every problem at once.

### Terms of use

Read the terms where the source states them: its terms of use, legal notice or copyright page, or the record of a dataset on Zenodo, Mendeley Data or an open data portal, whose licence takes precedence over the terms of the website. `licence.url` links to that page, and the pull request quotes the sentences that decide the category.

`licence.category` sorts the terms, and `licence.name` says what they allow, in one of these words:

| Category         | Terms                                                                      | `licence.name`                                                                                                                         |
| ---------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `open`           | Any use, including commercial use and redistribution of modified data, possibly with attribution | `CC BY 4.0`, `CC BY-SA 4.0`, `CC0 1.0`, `PDM 1.0`, `ODbL 1.0`, `ODC-By 1.0` or `PDDL 1.0`, else `Any use with attribution` or `Any use` |
| `non-commercial` | Only non-commercial use, of modified data too | `CC BY-NC 4.0` or `CC BY-NC-SA 4.0`, else `Non-commercial use with attribution`, `Non-commercial use`, `Personal or academic use with attribution` or `Personal or academic use` |
| `restricted`     | Personal use, no redistribution, no modified data, or no use without permission | `CC BY-ND 4.0` or `CC BY-NC-ND 4.0`, else `Personal use`, `Any use with attribution, no redistribution`, `Any use with attribution, no derivatives`, `Non-commercial use with attribution, no derivatives`, `Use with authorisation` (also for a bare "all rights reserved") or `No terms found` |

- A Creative Commons or Open Data Commons licence keeps its short name, with its version when the source states it: a version before 4.0 can be ported to a country, such as `CC BY 3.0 AU`, or be the IGO version, such as `CC BY 3.0 IGO`. A licence without derivatives (ND) is restricted, since modified data cannot be shared. Other licences, such as national open data licences, are written as what they allow.
- "with attribution" is added when the terms require citing the source, not when they only ask for it.
- `Use with authorisation` is for terms that grant no use, or no reuse, without permission, including a bare "all rights reserved". `No terms found` is for a source with no terms and no copyright notice at all.
- When the data of a source is collected from others, whose terms also apply, say so in `note`.

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

The ✅ marks of the list come from `data/demandcast.yaml`. When DemandCast retrieves a new source or subdivision, or stops retrieving one, the comparison reports the marks that no longer match as divergences. To update them, write the file from a copy of DemandCast and update the README:

```bash
uv run scripts/demandcast_sync.py --demandcast ../demandcast/demandcast/retrievals/electricity_demand_data_sources --output sync --update-marks
uv run scripts/build.py readme
```

The comparison also reports the countries and subdivisions without an outline in `data/shapes.geojson`, which the maps leave out, and the outlines of subdivisions that the list no longer has, which the shares of their country still count. A new or removed subdivision needs the file written again: write the file with the code of DemandCast, which finds the shapes of standard subdivisions in Natural Earth and those of non-standard subdivisions in its own shapes, from the `demandcast` folder of a copy of DemandCast, in its environment:

```bash
PYTHONPATH=. uv run --locked python ../../Awesome-Electricity-Demand/scripts/shapes.py
```

The command also computes the shares of each country with subdivisions: its people inside their outlines from the density of population of [SEDAC](https://doi.org/10.7927/H49C6VHW) in 2020, which DemandCast downloads into its data folder (about 400 MB) if it is not there, and its land from geodesic areas. It lists the subdivisions that still have no shape. A non-standard subdivision needs a shape in DemandCast first: an entry in its `demandcast/shapes/composites.yaml`, as a union of standard subdivisions of Natural Earth, with a polygon for the part of any of them outside it, drawn by hand along the borders of their districts, or a shapefile made by a script in the same folder.

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
