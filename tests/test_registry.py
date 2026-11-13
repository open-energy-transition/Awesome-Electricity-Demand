"""Tests of the loading and validation of the data files."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

import registry
from conftest import entity, source, write_shapes, write_source

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


def test_series_take_the_fields_of_their_source(data_dir: Path) -> None:
    """Give each series the name, licence and access of its source."""
    japan = registry.load(data_dir)[-1]
    by_source = {s.source_id: s for s in japan.series}
    assert by_source["entsoe"].name == "ENTSO-E"
    assert by_source["entsoe"].licence.category == "restricted"
    assert by_source["entsoe"].url == "https://example.org/a|b(c)"
    assert by_source["tepco"].url == "https://example.org/data"
    assert by_source["tepco"].access == "on-request"


def test_series_are_marked_from_the_demandcast_file(
    data_dir: Path,
) -> None:
    """Mark the series that the DemandCast file lists."""
    marked = {
        (s.source_id, s.entity.label)
        for c in registry.load(data_dir)
        for s in c.series
        if s.demandcast
    }
    assert marked == {("sonelgaz", "DZA"), ("tepco", "JPN-Kantō")}
    assert registry.load_demandcast(data_dir) == marked


def test_series_are_not_marked_without_the_file(data_dir: Path) -> None:
    """Mark no series if there is no DemandCast file."""
    (data_dir / "demandcast.yaml").unlink()
    assert not any(
        s.demandcast for c in registry.load(data_dir) for s in c.series
    )


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("sources:\n  other:\n  - DZA\n", "other is not a data source"),
        (
            "sources:\n  tepco:\n  - JPN-Kansai\n",
            "tepco has no entity JPN-Kansai",
        ),
        ("sources:\n  tepco:\n  - japan\n", "should match pattern"),
    ],
)
def test_invalid_demandcast_file_is_rejected(
    data_dir: Path, content: str, message: str
) -> None:
    """Reject marks of sources or entities that the list lacks."""
    (data_dir / "demandcast.yaml").write_text(content, encoding="utf-8")
    with pytest.raises(registry.RegistryError, match=message):
        registry.load(data_dir)


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
    ("category", "name"),
    [
        ("open", "CC BY 4.0"),
        ("open", "CC BY"),
        ("open", "CC BY-SA 4.0"),
        ("open", "CC BY 3.0 AU"),
        ("open", "CC BY 3.0 IGO"),
        ("open", "CC0 1.0"),
        ("open", "PDM 1.0"),
        ("open", "ODbL 1.0"),
        ("open", "Any use with attribution"),
        ("open", "Any use"),
        ("non-commercial", "CC BY-NC 4.0"),
        ("non-commercial", "CC BY-NC-SA 2.5 DK"),
        ("non-commercial", "Non-commercial use with attribution"),
        ("non-commercial", "Personal or academic use"),
        ("restricted", "CC BY-ND 4.0"),
        ("restricted", "CC BY-NC-ND 3.0 IGO"),
        ("restricted", "Personal use"),
        ("restricted", "Any use with attribution, no redistribution"),
        ("restricted", "Any use with attribution, no derivatives"),
        ("restricted", "Non-commercial use with attribution, no derivatives"),
        ("restricted", "Use with authorisation"),
        ("restricted", "No terms found"),
    ],
)
def test_licence_names_of_each_category(category: str, name: str) -> None:
    """Accept the words of the terms of use of each category."""
    licence = registry.Licence.model_validate(
        {"name": name, "url": "https://x.org", "category": category}
    )
    assert licence.name == name


@pytest.mark.parametrize(
    ("category", "name"),
    [
        ("open", "Open data"),
        ("open", "CC-BY 4.0"),
        ("open", "CC BY-NC 4.0"),
        ("open", "CC BY-ND 4.0"),
        ("open", "CC BY 3.0 Australia"),
        ("non-commercial", "CC BY 4.0"),
        ("non-commercial", "CC BY-NC-ND 4.0"),
        ("restricted", "All rights reserved"),
        ("restricted", "Use with authorization"),
        (
            "non-commercial",
            "Non-commercial use with attribution, no derivatives",
        ),
        ("restricted", "Any use"),
    ],
)
def test_other_licence_names_are_rejected(
    data_dir: Path, category: str, name: str
) -> None:
    """Reject terms that are not in the words of their category."""
    licence = {"name": name, "url": "https://x.org", "category": category}
    write_source(data_dir, "sonelgaz", source([entity()], licence=licence))
    with pytest.raises(registry.RegistryError, match="is not a name of"):
        registry.load(data_dir)


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


def test_every_problem_is_reported(data_dir: Path) -> None:
    """Report the problems of every file at once."""
    write_source(data_dir, "sonelgaz", source([entity(resolution=7)]))
    write_source(data_dir, "other", source([entity(country_code="XYZ")]))
    with pytest.raises(registry.RegistryError) as error:
        registry.load(data_dir)
    assert len(str(error.value).splitlines()) == 2


def test_repository_shapes_are_valid() -> None:
    """Load the shapes of the repository, one for every country."""
    shapes = registry.load_shapes()
    assert {c.code for c in registry.load()} <= set(shapes)


def test_load_shapes(data_dir: Path) -> None:
    """Load each shape as a list of polygons, by label."""
    shapes = registry.load_shapes(data_dir)
    assert list(shapes) == ["DZA", "EGY", "AGO", "JPN", "JPN-Kantō"]
    assert len(shapes["DZA"]) == 1
    assert [len(ring) for ring in shapes["DZA"][0]] == [5, 5]
    assert shapes["EGY"][0][0][1] == (19.0, 0.0)


def test_load_multipolygon_shapes(data_dir: Path) -> None:
    """Load each polygon of a multipolygon."""
    ring = [[0, 0], [1, 0], [1, 1], [0, 0]]
    (data_dir / "shapes.geojson").write_text(
        '{"type": "FeatureCollection", "features": [{"type": "Feature", '
        '"properties": {"label": "DZA"}, "geometry": {"type": '
        f'"MultiPolygon", "coordinates": [[{ring}], [{ring}]]}}}}]}}',
        encoding="utf-8",
    )
    assert len(registry.load_shapes(data_dir)["DZA"]) == 2


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (None, "No such file"),
        ("{}", "type: Field required"),
        (
            (
                '{"type": "FeatureCollection", "features": [{"type": '
                '"Feature", "properties": {"label": "dza"}, "geometry": '
                '{"type": "Polygon", "coordinates": []}}]}'
            ),
            "label: String should match pattern",
        ),
        (
            (
                '{"type": "FeatureCollection", "features": [{"type": '
                '"Feature", "properties": {"label": "DZA"}, "geometry": '
                '{"type": "Point", "coordinates": [0, 0]}}]}'
            ),
            "does not match any of the expected tags",
        ),
    ],
)
def test_invalid_shapes_are_rejected(
    data_dir: Path, content: str | None, message: str
) -> None:
    """Reject a shapes file that is missing or not valid GeoJSON."""
    path = data_dir / "shapes.geojson"
    if content is None:
        path.unlink()
    else:
        path.write_text(content, encoding="utf-8")
    with pytest.raises(registry.RegistryError, match=message):
        registry.load_shapes(data_dir)


def test_duplicate_shape_is_rejected(data_dir: Path) -> None:
    """Reject a shapes file with two shapes of an entity."""
    write_shapes(data_dir, ["DZA", "DZA"])
    with pytest.raises(registry.RegistryError, match="duplicate shape DZA"):
        registry.load_shapes(data_dir)
