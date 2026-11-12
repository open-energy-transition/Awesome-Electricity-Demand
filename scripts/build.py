"""Generate the README list, the map data and the figures from the data.

The data files are read and validated by `registry`. The README has
blocks between ``<!-- <name>:start -->`` and ``<!-- <name>:end -->``
that are replaced with the summary and the tables of data sources. The
site for GitHub Pages is the interactive map of ``site/``, with the
outlines that it draws, the list as CSV and JSON, and the figures.

Usage::

    python scripts/build.py readme      # validate, update README.md
    python scripts/build.py check       # fail if README.md is stale
    python scripts/build.py site DIR    # build the site into DIR
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

import registry
from registry import (
    CONTINENTS,
    ROOT,
    Country,
    Polygon,
    RegistryError,
    Series,
)

README = ROOT / "README.md"
STATIC_DIR = ROOT / "site"
CSV_FIELDS = (
    "country_code",
    "country_name",
    "continent",
    "subdivision_code",
    "subdivision_name",
    "source_id",
    "source_name",
    "url",
    "start",
    "end",
    "resolution_minutes",
    "access",
    "licence_name",
    "licence_url",
    "licence_category",
    "note",
    "demandcast",
)

logger = logging.getLogger(__name__)


def slug(text: str) -> str:
    """Return the anchor that GitHub gives to a Markdown heading.

    Parameters
    ----------
    text : str
        Text of the heading.

    Returns
    -------
    str
        Lower-case text without punctuation, with dashes for spaces.
    """
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def cell(text: str) -> str:
    """Escape text for a cell of a Markdown table.

    Parameters
    ----------
    text : str
        Text of the cell.

    Returns
    -------
    str
        The text with its pipes escaped.
    """
    return text.replace("|", "\\|")


def link(label: str, url: str) -> str:
    """Return a Markdown link that can be put in a table cell.

    Parameters
    ----------
    label : str
        Text of the link.
    url : str
        Target of the link.

    Returns
    -------
    str
        The link, as ``[label](url)``.

    Notes
    -----
    A pipe would end the cell and a parenthesis could end the link, so
    both are percent-encoded in the URL, which keeps it equivalent.
    """
    for character, code in (("|", "%7C"), ("(", "%28"), (")", "%29")):
        url = url.replace(character, code)
    return f"[{cell(label)}]({url})"


def sort_key(series: Series) -> tuple[bool, str, int, str]:
    """Order the series of a country: national first, then by region.

    Parameters
    ----------
    series : Series
        A time series.

    Returns
    -------
    tuple
        Whether the series is for a subdivision, the name of the
        subdivision, the first year and the name of the source.
    """
    entity = series.entity
    return (
        entity.subdivision_name is not None,
        entity.subdivision_name or "",
        entity.start,
        series.name,
    )


def readme_summary(countries: list[Country]) -> str:
    """Write the number of series, sources and countries.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.

    Returns
    -------
    str
        Markdown with the totals and links to the continents.
    """
    covered = [c for c in countries if c.series]
    series = [s for c in covered for s in c.series]
    sources = {s.source_id for s in series}
    lines = [
        (
            f"The list has **{len(series)} time series** from "
            f"**{len(sources)} data sources** for "
            f"**{len(covered)} countries** and their subdivisions in:"
        ),
        "",
    ]
    for continent in CONTINENTS:
        n = sum(1 for c in covered if c.continent == continent)
        lines.append(f"- [{continent}](#{slug(continent)}) ({n} countries)")
    return "\n".join(lines)


LICENCE_MARKS = {"open": "🟢", "non-commercial": "🟡", "restricted": "🔴"}
LEGEND = (
    "🟢 open · 🟡 non-commercial · 🔴 restricted "
    "[terms](CONTRIBUTING.md#terms-of-use) · 🔒 access on "
    "request · ✅ retrieved by "
    "[DemandCast](https://github.com/open-energy-transition/demandcast)"
)


def group_series(series: tuple[Series, ...]) -> list[list[Series]]:
    """Group the series of a country that differ only by subdivision.

    Parameters
    ----------
    series : tuple of Series
        The time series of a country.

    Returns
    -------
    list of list of Series
        The groups, national first, then by subdivision and first year,
        each a row of the README.

    Notes
    -----
    A group joins the series of the subdivisions of one source with the
    same years, resolution and note, such as the 13 regions of the EIA,
    and never joins the national series with those of subdivisions.
    """
    groups: dict[tuple[object, ...], list[Series]] = {}
    for item in sorted(series, key=sort_key):
        entity = item.entity
        key = (
            item.source_id,
            entity.subdivision_code is None,
            entity.start,
            entity.end,
            entity.resolution,
            entity.note,
        )
        groups.setdefault(key, []).append(item)
    return list(groups.values())


def group_url(group: list[Series]) -> str:
    """Return the page to link for a group of series.

    Parameters
    ----------
    group : list of Series
        Series of one source that differ only by subdivision.

    Returns
    -------
    str
        The page of the series if they share one, otherwise the page of
        their source.
    """
    urls = {item.url for item in group}
    return urls.pop() if len(urls) == 1 else group[0].source_url


def area_cell(group: list[Series]) -> str:
    """Return the Area cell of a group of series.

    Parameters
    ----------
    group : list of Series
        Series of one source that differ only by subdivision.

    Returns
    -------
    str
        "National", the name of the subdivision, or the number of the
        subdivisions with their names folded under it.
    """
    names = [
        cell(item.entity.subdivision_name)
        for item in group
        if item.entity.subdivision_name is not None
    ]
    if not names:
        return "National"
    if len(names) == 1:
        return names[0]
    return (
        f"<details><summary>{len(names)} subdivisions</summary>"
        f"{', '.join(names)}</details>"
    )


def source_cell(group: list[Series]) -> str:
    """Return the Source cell of a group of series.

    Parameters
    ----------
    group : list of Series
        Series of one source that differ only by subdivision.

    Returns
    -------
    str
        The name of the source linked to its page, and its note in
        small text below.
    """
    first = group[0]
    text = link(first.name, group_url(group))
    if first.entity.note:
        text += f"<br><sub>{cell(first.entity.note)}</sub>"
    return text


def terms_cell(series: Series) -> str:
    """Return the Terms cell of a series.

    Parameters
    ----------
    series : Series
        A time series.

    Returns
    -------
    str
        The mark of the category of the licence, its name linked to its
        page, and a lock if the data is given only on request.
    """
    licence = series.licence
    text = (
        f"{LICENCE_MARKS[licence.category]} {link(licence.name, licence.url)}"
    )
    if series.access == "on-request":
        text += " 🔒"
    return text


def demandcast_cell(group: list[Series]) -> str:
    """Return the DemandCast cell of a group of series.

    Parameters
    ----------
    group : list of Series
        Series of one source that differ only by subdivision.

    Returns
    -------
    str
        A check mark if DemandCast retrieves every series of the group,
        with the number of them if it retrieves only some, or nothing.
    """
    retrieved = sum(item.demandcast for item in group)
    if retrieved == 0:
        return ""
    if retrieved == len(group):
        return "✅"
    return f"✅ {retrieved}/{len(group)}"


def resolution_label(minutes: int) -> str:
    """Return the time step of a series as shown in the README.

    Parameters
    ----------
    minutes : int
        Time step in minutes.

    Returns
    -------
    str
        "hourly", or the number of minutes.
    """
    return "hourly" if minutes == 60 else f"{minutes} min"


def readme_sources(countries: list[Country]) -> str:
    """Write a folded table of the data sources of each continent.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.

    Returns
    -------
    str
        Markdown with a legend, then for each continent a heading and a
        table, folded under the number of its countries and series, with
        a row for each group of series.
    """
    blocks = [f"<sub>{LEGEND}</sub>"]
    for continent in CONTINENTS:
        members = [
            c for c in countries if c.continent == continent and c.series
        ]
        n_series = sum(len(c.series) for c in members)
        rows = [
            f"### {continent}",
            "",
            (
                f"<details open><summary>{len(members)} countries · "
                f"{n_series} time series</summary>"
            ),
            "",
            (
                "| Country | Area | Source | Years | Resolution | Terms "
                "| DemandCast |"
            ),
            "| --- | --- | --- | --- | --- | --- | :-: |",
        ]
        for country in members:
            for i, group in enumerate(group_series(country.series)):
                first = group[0]
                cells = [
                    f"**{cell(country.name)}**" if i == 0 else "",
                    area_cell(group),
                    source_cell(group),
                    first.period,
                    resolution_label(first.entity.resolution),
                    terms_cell(first),
                    demandcast_cell(group),
                ]
                rows.append("| " + " | ".join(cells) + " |")
        rows += ["", "</details>"]
        blocks.append("\n".join(rows))
    return "\n\n".join(blocks)


BLOCKS: dict[str, Callable[[list[Country]], str]] = {
    "summary": readme_summary,
    "sources": readme_sources,
}


def render_readme(text: str, countries: list[Country]) -> str:
    """Replace the generated blocks of the README.

    Parameters
    ----------
    text : str
        Content of the README.
    countries : list of Country
        Every country of the list.

    Returns
    -------
    str
        The README with each block replaced by its generated content.

    Raises
    ------
    ValueError
        If the README lacks one of the blocks of `BLOCKS`.
    """
    for name, render in BLOCKS.items():
        pattern = re.compile(
            rf"(<!-- {name}:start[^>]*-->)\n.*?(<!-- {name}:end -->)",
            flags=re.DOTALL,
        )
        match = pattern.search(text)
        if match is None:
            raise ValueError(f"the README has no {name} block")
        block = f"{match[1]}\n{render(countries)}\n{match[2]}"
        text = text[: match.start()] + block + text[match.end() :]
    return text


def records(
    countries: list[Country],
) -> list[dict[str, str | int | bool | None]]:
    """Return one flat record per time series.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.

    Returns
    -------
    list of dict
        The values of `CSV_FIELDS` for each time series.
    """
    return [
        {
            "country_code": country.code,
            "country_name": country.name,
            "continent": country.continent,
            "subdivision_code": series.entity.subdivision_code,
            "subdivision_name": series.entity.subdivision_name,
            "source_id": series.source_id,
            "source_name": series.name,
            "url": series.url,
            "start": series.entity.start,
            "end": series.entity.end,
            "resolution_minutes": series.entity.resolution,
            "access": series.access,
            "licence_name": series.licence.name,
            "licence_url": series.licence.url,
            "licence_category": series.licence.category,
            "note": series.entity.note,
            "demandcast": series.demandcast,
        }
        for country in countries
        for series in sorted(country.series, key=sort_key)
    ]


def build_site(
    countries: list[Country],
    shapes: dict[str, list[Polygon]],
    site_dir: Path,
) -> None:
    """Build the site for GitHub Pages.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    shapes : dict
        The outlines of the countries and subdivisions, by label, for
        the interactive map and the map of the figures.
    site_dir : Path
        Folder of the site, created if needed.

    Notes
    -----
    The site is the content of ``site/``, with ``sources.csv`` and
    ``sources.json``, which list every time series, ``map.geojson``,
    the outlines that the interactive map draws with their years of
    data, and the figures. The map shows the data sources of a country
    or subdivision from ``sources.json``.
    """
    import figures  # noqa: PLC0415 - Matplotlib is only needed here.

    shutil.copytree(STATIC_DIR, site_dir, dirs_exist_ok=True)
    rows = records(countries)
    with (site_dir / "sources.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    country_fields = {"country_code", "country_name", "continent"}
    data = {
        "countries": {
            country.code: {
                "name": country.name,
                "continent": country.continent,
                "years": country.years,
                "series": [
                    {k: v for k, v in r.items() if k not in country_fields}
                    for r in rows
                    if r["country_code"] == country.code
                ],
            }
            for country in countries
        }
    }
    (site_dir / "sources.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    (site_dir / "map.geojson").write_text(
        json.dumps(
            figures.map_features(countries, shapes), separators=(",", ":")
        ),
        encoding="utf-8",
    )
    figures.plot_all(countries, shapes, site_dir / "figures")
    logger.info("Site built in %s", site_dir)


def main(argv: list[str] | None = None) -> int:
    """Run the command given on the command line.

    Parameters
    ----------
    argv : list of str, optional
        Arguments of the command, by default those of the process.

    Returns
    -------
    int
        0 on success, 1 if the data is invalid or the README is stale.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("readme", help="validate and update README.md")
    commands.add_parser("check", help="fail if README.md is out of date")
    site = commands.add_parser("site", help="build the GitHub Pages site")
    site.add_argument("directory", type=Path)
    args = parser.parse_args(argv)

    try:
        countries = registry.load()
        shapes = registry.load_shapes()
    except RegistryError as e:
        logger.error("The data files have errors:\n%s", e)  # noqa: TRY400
        return 1

    if args.command == "site":
        build_site(countries, shapes, args.directory)
        return 0

    current = README.read_text(encoding="utf-8")
    updated = render_readme(current, countries)
    if updated == current:
        logger.info("The data is valid and README.md is up to date.")
        return 0
    if args.command == "check":
        logger.error(
            "README.md is out of date: run `uv run scripts/build.py "
            "readme` and commit the result."
        )
        return 1
    README.write_text(updated, encoding="utf-8")
    logger.info("README.md updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
