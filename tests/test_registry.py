"""Tests of the loading and validation of the data files."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

import registry
from conftest import source, write_sources

if TYPE_CHECKING:
    from pathlib import Path


def test_repository_data_is_valid() -> None:
    """Load the data files of the repository without errors."""
    countries = registry.load()
    assert any(c.sources for c in countries)


def test_load_orders_countries_and_reads_sources(data_dir: Path) -> None:
    """Order the countries by continent and name, with their sources."""
    countries = registry.load(data_dir)
    assert [c.code for c in countries] == ["DZA", "AGO", "EGY", "JPN"]
    assert len(countries[-1].sources) == 2
    assert countries[0].searched
    assert not countries[1].searched


def test_years_counts_each_year_once(data_dir: Path) -> None:
    """Count the years covered by overlapping sources once."""
    write_sources(
        data_dir,
        "DZA",
        [source(start=2010, end=2015), source(start=2014, end=2016)],
    )
    algeria = registry.load(data_dir)[0]
    assert algeria.years == 7


def test_present_counts_until_the_current_year(data_dir: Path) -> None:
    """Count "present" as the current year."""
    write_sources(data_dir, "DZA", [source(start=2020, end="present")])
    algeria = registry.load(data_dir)[0]
    assert algeria.years == registry.current_year() - 2020 + 1
    assert algeria.sources[0].period == "2020-present"


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"colour": "red"}, "Extra inputs are not permitted"),
        ({"start": 2020, "end": 2019}, "is before start"),
        ({"end": 9999}, "use 'present'"),
        ({"resolution": 7}, "divides 60"),
        ({"resolution": 1440}, "divides 60"),
        ({"url": "example.org"}, "should match pattern"),
        ({"subdivision_code": "BA"}, "must be given together"),
        ({"access": "paid"}, "'public' or 'on-request'"),
        (
            {"licence": {"name": "x", "url": "https://x.org", "category": ""}},
            "'open', 'non-commercial' or 'restricted'",
        ),
    ],
)
def test_invalid_source_is_rejected(
    data_dir: Path, changes: dict[str, Any], message: str
) -> None:
    """Reject a data source with an invalid field, naming its file."""
    write_sources(data_dir, "DZA", [source(**changes)])
    with pytest.raises(registry.RegistryError, match=message) as error:
        registry.load(data_dir)
    assert "sources/DZA.yaml" in str(error.value)


def test_subdivision_with_two_names_is_rejected(data_dir: Path) -> None:
    """Reject a subdivision code given two different names."""
    write_sources(
        data_dir,
        "DZA",
        [
            source(subdivision_code="A", subdivision_name="One"),
            source(subdivision_code="A", subdivision_name="Two", start=2011),
        ],
    )
    with pytest.raises(registry.RegistryError, match="has two names"):
        registry.load(data_dir)


def test_duplicate_source_is_rejected(data_dir: Path) -> None:
    """Reject a data source listed twice."""
    write_sources(data_dir, "DZA", [source(), source()])
    with pytest.raises(registry.RegistryError, match="duplicate source"):
        registry.load(data_dir)


def test_unknown_country_file_is_rejected(data_dir: Path) -> None:
    """Reject a data file whose name is not in the countries file."""
    write_sources(data_dir, "XYZ", [source()])
    with pytest.raises(registry.RegistryError, match="XYZ is not a country"):
        registry.load(data_dir)


def test_country_with_data_must_be_searched(data_dir: Path) -> None:
    """Reject a country with data sources but marked as not searched."""
    write_sources(data_dir, "AGO", [source()])
    with pytest.raises(registry.RegistryError, match="searched must be yes"):
        registry.load(data_dir)


def test_every_problem_is_reported(data_dir: Path) -> None:
    """Report the problems of every file at once."""
    write_sources(data_dir, "DZA", [source(resolution=7)])
    write_sources(data_dir, "XYZ", [source()])
    with pytest.raises(registry.RegistryError) as error:
        registry.load(data_dir)
    assert len(str(error.value).splitlines()) == 2
