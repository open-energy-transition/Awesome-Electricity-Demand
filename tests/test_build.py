"""Tests of the generation of the README, the site and the figures."""

from __future__ import annotations

import csv
import json
from typing import TYPE_CHECKING

import pytest

import build
import figures
import registry
from conftest import entity, source, write_source

if TYPE_CHECKING:
    from pathlib import Path

TEMPLATE = """\
# Title

<!-- summary:start: generated -->
old
<!-- summary:end -->

<!-- searched:start -->
<!-- searched:end -->

<!-- sources:start -->
old
lines
<!-- sources:end -->
"""


def test_repository_readme_is_up_to_date() -> None:
    """Match the README of the repository with its data files."""
    text = build.README.read_text(encoding="utf-8")
    assert build.render_readme(text, registry.load()) == text


def test_render_readme_replaces_each_block(data_dir: Path) -> None:
    """Replace the content of each block and keep the text around it."""
    text = build.render_readme(TEMPLATE, registry.load(data_dir))
    assert text.startswith("# Title\n\n<!-- summary:start: generated -->\n")
    assert "old" not in text
    assert (
        "**4 time series** from **3 data sources** for **2 countries**" in text
    )
    assert "- [North America](#north-america) (0 countries)" in text
    assert "- **Africa:** Egypt\n<!-- searched:end -->" in text
    assert build.render_readme(text, registry.load(data_dir)) == text


def test_tables_list_national_sources_first(data_dir: Path) -> None:
    """Write the country name once, before its national series."""
    text = build.readme_sources(registry.load(data_dir))
    japan = text.split("### Asia")[1].splitlines()
    rows = [line for line in japan if "ENTSO-E" in line or "TEPCO" in line]
    assert rows == [
        (
            "| **Japan** | National | "
            "[ENTSO-E](https://example.org/a%7Cb%28c%29)"
            "<br><sub>Generation, proxy for demand</sub> | 2015-2017 | "
            "hourly | 🔴 [Personal use](https://example.org/terms) |  |"
        ),
        (
            "|  | Kantō | [TEPCO](https://example.org/data) | 2016-present | "
            "5 min | 🟢 [CC-BY 4.0](https://example.org/licence) 🔒 | ✅ |"
        ),
    ]


def test_tables_are_folded_by_continent(data_dir: Path) -> None:
    """Fold each continent under its numbers, below the legend."""
    text = build.readme_sources(registry.load(data_dir))
    assert text.startswith(f"<sub>{build.LEGEND}</sub>")
    assert (
        "### Africa\n\n<details open><summary>1 countries · 2 time "
        "series</summary>"
    ) in text
    assert "| Resolution | Terms | DemandCast |" in text
    assert text.count("</details>") == len(registry.CONTINENTS)


def test_subdivisions_share_a_row(data_dir: Path) -> None:
    """Join the subdivisions of a source with the same years."""
    write_source(
        data_dir,
        "cenace",
        source(
            [
                entity(
                    subdivision_code=code,
                    subdivision_name=name,
                    url=f"https://example.org/{code}",
                )
                for code, name in (("A", "Alger"), ("B", "Batna"))
            ]
            + [entity(subdivision_code="C", subdivision_name="Constantine")],
            name="CENACE",
        ),
    )
    (data_dir / "demandcast.yaml").write_text(
        "sources:\n  cenace:\n  - DZA-A\n  - DZA-B\n", encoding="utf-8"
    )
    text = build.readme_sources(registry.load(data_dir))
    rows = [line for line in text.splitlines() if "CENACE" in line]
    assert rows == [
        (
            "|  | <details><summary>3 subdivisions</summary>Alger, Batna, "
            "Constantine</details> | [CENACE](https://example.org/data) | "
            "2010-2019 | hourly | 🟢 [CC-BY 4.0](https://example.org/licence)"
            " | ✅ 2/3 |"
        )
    ]


def test_group_url_is_shared_or_of_the_source(data_dir: Path) -> None:
    """Link the shared page of a group, or the page of its source."""
    japan = registry.load(data_dir)[-1]
    groups = build.group_series(japan.series)
    assert [build.group_url(g) for g in groups] == [
        "https://example.org/a|b(c)",
        "https://example.org/data",
    ]
    mixed = [groups[0][0], groups[0][0].model_copy(update={"url": "x"})]
    assert build.group_url(mixed) == groups[0][0].source_url


def test_link_encodes_pipes_and_parentheses() -> None:
    """Percent-encode the characters that would break a table cell."""
    assert build.link("a|b", "https://x.org/a|b(c)") == (
        r"[a\|b](https://x.org/a%7Cb%28c%29)"
    )


def test_render_readme_needs_every_block(data_dir: Path) -> None:
    """Raise an error if the README lacks a block."""
    with pytest.raises(ValueError, match="no sources block"):
        build.render_readme(
            TEMPLATE.replace("sources:", "other:"), registry.load(data_dir)
        )


def test_coverage_by_continent(data_dir: Path) -> None:
    """Compute the shares of countries, population and land covered."""
    shares = figures.coverage_by_continent(registry.load(data_dir))
    assert shares["countries"][0] == pytest.approx(100 / 3)
    assert shares["population"][0] == pytest.approx(20)
    assert shares["land"][0] == pytest.approx(20)
    assert shares["countries"][1] == pytest.approx(100)


def test_years_by_resolution(data_dir: Path) -> None:
    """Count the years of each country and resolution once."""
    years = figures.years_by_resolution(registry.load(data_dir))
    assert years[60][:2] == [10, 3]
    assert years[5][1] == registry.current_year() - 2016 + 1


def test_years_of_subdivisions_count_once(data_dir: Path) -> None:
    """Count the years of a country once for all its subdivisions."""
    (data_dir / "demandcast.yaml").unlink()
    write_source(
        data_dir,
        "sonelgaz",
        source(
            [
                entity(subdivision_code="A", subdivision_name="A", end=2011),
                entity(subdivision_code="B", subdivision_name="B", end=2012),
            ]
        ),
    )
    write_source(data_dir, "entsoe", source([entity(start=2011, end=2011)]))
    years = figures.years_by_resolution(registry.load(data_dir))
    assert years[60][0] == 3


def test_build_site(data_dir: Path, tmp_path: Path) -> None:
    """Write the map, the CSV and JSON lists and the figures."""
    site = tmp_path / "site"
    build.build_site(registry.load(data_dir), site)
    assert (site / "index.html").exists()
    assert (site / "figures" / "coverage_by_continent.png").exists()
    with (site / "sources.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [r["source_name"] for r in rows] == [
        "Sonelgaz",
        "ENTSO-E",
        "ENTSO-E",
        "TEPCO",
    ]
    assert rows[0]["source_id"] == "sonelgaz"
    assert [r["demandcast"] for r in rows] == [
        "True",
        "False",
        "False",
        "True",
    ]
    data = json.loads((site / "sources.json").read_text(encoding="utf-8"))
    assert data["countries"]["EGY"] == {
        "name": "Egypt",
        "continent": "Africa",
        "searched": True,
        "years": 0,
        "series": [],
    }
    assert data["countries"]["JPN"]["series"][1]["subdivision_code"] == (
        "Kantō"
    )
