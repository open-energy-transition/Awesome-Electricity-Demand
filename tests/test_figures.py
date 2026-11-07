"""Tests of the computations and drawing of the figures."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

import figures
import registry
from conftest import entity, source, write_source

if TYPE_CHECKING:
    from pathlib import Path


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
    assert list(years) == [5, 60]
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


def test_years_by_entity(data_dir: Path) -> None:
    """Count the years of each country and subdivision of any source."""
    years = figures.years_by_entity(registry.load(data_dir))
    assert years == {
        "DZA": 10,
        "JPN": 3,
        "JPN-Kantō": registry.current_year() - 2016 + 1,
    }


@pytest.mark.parametrize(
    ("years", "expected"),
    [(1, 0), (4, 0), (5, 1), (9, 1), (10, 2), (19, 2), (20, 3), (60, 3)],
)
def test_year_class(years: int, expected: int) -> None:
    """Put a number of years in the classes of the map."""
    assert figures.year_class(years) == expected


def test_ramp_spreads_its_own_steps() -> None:
    """Pick the steps of a ramp from its strongest one."""
    colours = ("#000001", "#000002", "#000003", "#000004", "#000005")
    assert figures.ramp(colours, 1) == ["#000001"]
    assert figures.ramp(colours, 2) == ["#000001", "#000005"]
    assert figures.ramp(colours, 3) == ["#000001", "#000003", "#000005"]
    assert figures.ramp(colours, 5) == list(colours)


def test_ramp_interpolates_beyond_its_length() -> None:
    """Interpolate the steps when more are needed than the ramp has."""
    steps = figures.ramp(("#000000", "#ffffff"), 3)
    assert steps[0] == "#000000"
    assert steps[2] == "#ffffff"
    assert steps[1] not in steps[::2]


def test_robinson_projection() -> None:
    """Project the equator, the poles and the edges of the map."""
    x, y = figures.robinson(
        np.array([0.0, 180.0, 0.0, -180.0]), np.array([0.0, 0.0, 90.0, -90.0])
    )
    assert x == pytest.approx([0, 0.8487 * np.pi, 0, -0.8487 * 0.5322 * np.pi])
    assert y == pytest.approx([0, 0, 1.3523, -1.3523])


def test_outline_path_keeps_the_holes(data_dir: Path) -> None:
    """Join the rings of a shape, its hole included, in one path."""
    shapes = registry.load_shapes(data_dir)
    path = figures.outline_path(shapes["DZA"])
    assert len(path.to_polygons()) == 2


def test_plot_all(data_dir: Path, tmp_path: Path) -> None:
    """Draw each figure in a light and a dark version."""
    directory = tmp_path / "figures"
    figures.plot_all(
        registry.load(data_dir), registry.load_shapes(data_dir), directory
    )
    assert sorted(p.name for p in directory.iterdir()) == [
        f"{name}_{theme}.png"
        for name in ("coverage_by_continent", "map", "years_by_continent")
        for theme in ("dark", "light")
    ]


def test_map_leaves_out_entities_without_a_shape(
    data_dir: Path, tmp_path: Path
) -> None:
    """Draw the map without the entities that have no outline."""
    shapes = registry.load_shapes(data_dir)
    del shapes["JPN-Kantō"]
    path = tmp_path / "map.png"
    figures.plot_map(registry.load(data_dir), shapes, figures.THEMES[0], path)
    assert path.stat().st_size > 0
