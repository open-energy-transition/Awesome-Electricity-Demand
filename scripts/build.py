"""Generate the README list, the map data and the figures from the data.

The data files are read and validated by `registry`. The README has
blocks between ``<!-- <name>:start -->`` and ``<!-- <name>:end -->``
that are replaced with the summary, the tables of data sources and the
countries searched without success. The site for GitHub Pages is the
map of ``demand-data-map/``, the list as CSV and JSON, and the figures.

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
from registry import CONTINENTS, ROOT, Country, RegistryError, Series

README = ROOT / "README.md"
MAP_DIR = ROOT / "demand-data-map"
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


def notes(series: Series) -> str:
    """Return the text of the Notes column for a series.

    Parameters
    ----------
    series : Series
        A time series.

    Returns
    -------
    str
        Whether access is on request, and the note of the series.
    """
    parts = []
    if series.access == "on-request":
        parts.append("Access on request")
    if series.entity.note:
        parts.append(series.entity.note)
    return cell(". ".join(parts))


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


def readme_sources(countries: list[Country]) -> str:
    """Write a table of the data sources of each continent.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.

    Returns
    -------
    str
        Markdown with one heading and one table per continent.
    """
    blocks = []
    for continent in CONTINENTS:
        rows = [
            f"### {continent}",
            "",
            (
                "| Country | Subdivision | Source | Period | Resolution "
                "| Licence | Notes |"
            ),
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for country in countries:
            if country.continent != continent:
                continue
            for i, series in enumerate(sorted(country.series, key=sort_key)):
                cells = [
                    f"**{cell(country.name)}**" if i == 0 else "",
                    cell(series.entity.subdivision_name or ""),
                    link(series.name, series.url),
                    series.period,
                    f"{series.entity.resolution} min",
                    link(series.licence.name, series.licence.url),
                    notes(series),
                ]
                rows.append("| " + " | ".join(cells) + " |")
        blocks.append("\n".join(rows))
    return "\n\n".join(blocks)


def readme_searched(countries: list[Country]) -> str:
    """Write the countries searched without finding data, by continent.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.

    Returns
    -------
    str
        Markdown list with one item per continent.
    """
    lines = []
    for continent in CONTINENTS:
        names = [
            c.name
            for c in countries
            if c.continent == continent and c.searched and not c.series
        ]
        if names:
            lines.append(f"- **{continent}:** {', '.join(names)}")
    return "\n".join(lines) or "None yet."


BLOCKS: dict[str, Callable[[list[Country]], str]] = {
    "summary": readme_summary,
    "searched": readme_searched,
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


def records(countries: list[Country]) -> list[dict[str, str | int | None]]:
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
        }
        for country in countries
        for series in sorted(country.series, key=sort_key)
    ]


def build_site(countries: list[Country], site_dir: Path) -> None:
    """Build the site for GitHub Pages.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    site_dir : Path
        Folder of the site, created if needed.

    Notes
    -----
    ``sources.json`` has every country, with whether it has been
    searched and the number of years with data, which the map colours.
    """
    import figures  # noqa: PLC0415 - Matplotlib is only needed here.

    shutil.copytree(
        MAP_DIR,
        site_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("README.md"),
    )
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
                "searched": country.searched,
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
    figures.plot_all(countries, site_dir / "figures")
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
    except RegistryError as e:
        logger.error("The data files have errors:\n%s", e)  # noqa: TRY400
        return 1

    if args.command == "site":
        build_site(countries, args.directory)
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
