"""Tests of the loading and validation of the data files."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

import registry
from conftest import entity, source, write_source

if TYPE_CHECKING:
    from pathlib import Path


def test_repository_data_is_valid() -> None:
    """Load the data files of the repository without errors."""
    countries = registry.load()
    assert any(c.series for c in countries)


def test_load_groups_entities_by_country(data_dir: Path) -> None:
    """Order the countries and give each the series of every source."""
    countries = registry.load(data_dir)
    assert [c.code for c in countries] == ["DZA", "AGO", "EGY", "JPN"]
    algeria, japan = countries[0], countries[-1]
    assert sorted(s.source_id for s in algeria.series) == [
        "entsoe",
        "sonelgaz",
    ]
    assert {s.source_id for s in japan.series} == {"entsoe", "tepco"}
    assert not countries[1].searched


def test_series_take_the_fields_of_their_source(data_dir: Path) -> None:
    """Give each series the name, licence and access of its source."""
    japan = registry.load(data_dir)[-1]
    by_source = {s.source_id: s for s in japan.series}
    assert by_source["entsoe"].name == "ENTSO-E"
    assert by_source["entsoe"].licence.category == "restricted"
    assert by_source["entsoe"].url == "https://example.org/a|b(c)"
    assert by_source["tepco"].url == "https://example.org/data"
    assert by_source["tepco"].access == "on-request"


def test_years_counts_each_year_once(data_dir: Path) -> None:
    """Count the years covered by overlapping series once."""
    write_source(
        data_dir,
        "sonelgaz",
        source([entity(start=2010, end=2015), entity(start=2014, end=2016)]),
    )
    algeria = registry.load(data_dir)[0]
    assert algeria.years == 7


def test_present_counts_until_the_current_year(data_dir: Path) -> None:
    """Count "present" as the current year."""
    write_source(
        data_dir, "sonelgaz", source([entity(start=2020, end="present")])
    )
    algeria = registry.load(data_dir)[0]
    series = next(s for s in algeria.series if s.source_id == "sonelgaz")
    assert series.end_year == registry.current_year()
    assert series.period == "2020-present"


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
        ({"country_code": "dz"}, "should match pattern"),
    ],
)
def test_invalid_entity_is_rejected(
    data_dir: Path, changes: dict[str, Any], message: str
) -> None:
    """Reject an entity with an invalid field, naming its file."""
    write_source(data_dir, "sonelgaz", source([entity(**changes)]))
    with pytest.raises(registry.RegistryError, match=message) as error:
        registry.load(data_dir)
    assert "sources/sonelgaz.yaml: entities.0" in str(error.value)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"access": "paid"}, "'public' or 'on-request'"),
        (
            {"licence": {"name": "x", "url": "https://x.org", "category": ""}},
            "'open', 'non-commercial' or 'restricted'",
        ),
        ({"provider": "x"}, "Extra inputs are not permitted"),
    ],
)
def test_invalid_source_is_rejected(
    data_dir: Path, changes: dict[str, Any], message: str
) -> None:
    """Reject a source with an invalid field."""
    write_source(data_dir, "sonelgaz", source([entity()], **changes))
    with pytest.raises(registry.RegistryError, match=message):
        registry.load(data_dir)


def test_source_without_entities_is_rejected(data_dir: Path) -> None:
    """Reject a source with no entities."""
    write_source(data_dir, "sonelgaz", source([]))
    with pytest.raises(registry.RegistryError, match="at least 1 item"):
        registry.load(data_dir)


def test_duplicate_entity_is_rejected(data_dir: Path) -> None:
    """Reject an entity listed twice in a source."""
    write_source(data_dir, "sonelgaz", source([entity(), entity()]))
    with pytest.raises(registry.RegistryError, match="duplicate entity"):
        registry.load(data_dir)


def test_entity_with_the_url_of_its_source_is_rejected(
    data_dir: Path,
) -> None:
    """Reject an entity URL that repeats the URL of its source."""
    write_source(
        data_dir,
        "sonelgaz",
        source([entity(url="https://example.org/data")]),
    )
    with pytest.raises(registry.RegistryError, match="leave it out"):
        registry.load(data_dir)


def test_subdivision_with_two_names_is_rejected(data_dir: Path) -> None:
    """Reject a subdivision code named differently in two sources."""
    write_source(
        data_dir,
        "kansaitd",
        source(
            [
                entity(
                    country_code="JPN",
                    subdivision_code="Kantō",
                    subdivision_name="Kanto",
                )
            ]
        ),
    )
    with pytest.raises(registry.RegistryError, match="Kanto"):
        registry.load(data_dir)


def test_unknown_country_is_rejected(data_dir: Path) -> None:
    """Reject an entity whose country is not in the countries file."""
    write_source(data_dir, "sonelgaz", source([entity(country_code="XYZ")]))
    with pytest.raises(registry.RegistryError, match="XYZ is not a country"):
        registry.load(data_dir)


def test_invalid_file_name_is_rejected(data_dir: Path) -> None:
    """Reject a data file whose name is not a source identifier."""
    write_source(data_dir, "ENTSO-E", source([entity()]))
    with pytest.raises(registry.RegistryError, match="lower-case letters"):
        registry.load(data_dir)


def test_country_with_data_must_be_searched(data_dir: Path) -> None:
    """Reject a country with data that is marked as not searched."""
    write_source(data_dir, "sonelgaz", source([entity(country_code="AGO")]))
    with pytest.raises(registry.RegistryError, match="searched must be yes"):
        registry.load(data_dir)


def test_every_problem_is_reported(data_dir: Path) -> None:
    """Report the problems of every file at once."""
    write_source(data_dir, "sonelgaz", source([entity(resolution=7)]))
    write_source(data_dir, "other", source([entity(country_code="XYZ")]))
    with pytest.raises(registry.RegistryError) as error:
        registry.load(data_dir)
    assert len(str(error.value).splitlines()) == 2
