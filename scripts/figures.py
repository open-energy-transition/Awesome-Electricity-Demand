"""Draw the figures of the coverage of the list.

The figures are computed from the countries and time series loaded by
`registry`: the share of the countries, population and land area of
each continent that have data, and the years of data of each continent
by time resolution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from registry import CONTINENTS, Country

if TYPE_CHECKING:
    from pathlib import Path

YEAR_COLOURS = (
    "#ff8b94",
    "#ffaaa5",
    "#ffd3b6",
    "#dcedc1",
    "#a8e6cf",
    "#bde0fe",
    "#cdb4db",
)


def percent(part: float, whole: float) -> float:
    """Return a part of a whole as a percentage.

    Parameters
    ----------
    part : float
        The part.
    whole : float
        The whole, which can be 0.

    Returns
    -------
    float
        The percentage, or 0 if the whole is 0.
    """
    return 100 * part / whole if whole else 0.0


def coverage_by_continent(
    countries: list[Country],
) -> dict[str, list[float]]:
    """Compute the share of each continent that has data.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.

    Returns
    -------
    dict
        The percentages of countries, population and land area with
        data, under "countries", "population" and "land", in the order
        of `CONTINENTS`.

    Notes
    -----
    A country counts as covered if it has any time series, even one
    for only some of its subdivisions.
    """
    shares: dict[str, list[float]] = {
        "countries": [],
        "population": [],
        "land": [],
    }
    for continent in CONTINENTS:
        members = [c for c in countries if c.continent == continent]
        covered = [c for c in members if c.series]
        shares["countries"].append(percent(len(covered), len(members)))
        shares["population"].append(
            percent(
                sum(c.population_millions for c in covered),
                sum(c.population_millions for c in members),
            )
        )
        shares["land"].append(
            percent(
                sum(c.land_area_km2 for c in covered),
                sum(c.land_area_km2 for c in members),
            )
        )
    return shares


def years_by_resolution(countries: list[Country]) -> dict[int, list[int]]:
    """Count the years of data of each continent by time resolution.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.

    Returns
    -------
    dict
        For each resolution in minutes, the years of data of each
        continent, in the order of `CONTINENTS`.

    Notes
    -----
    A year counts once for each country and resolution, however many
    sources or subdivisions of the country have data for it at that
    resolution.
    """
    resolutions = sorted(
        {s.entity.resolution for c in countries for s in c.series}
    )
    years = {r: [0] * len(CONTINENTS) for r in resolutions}
    for country in countries:
        i = CONTINENTS.index(country.continent)
        covered: dict[int, set[int]] = {}
        for series in country.series:
            covered.setdefault(series.entity.resolution, set()).update(
                range(series.entity.start, series.end_year + 1)
            )
        for resolution, years_covered in covered.items():
            years[resolution][i] += len(years_covered)
    return years


def plot_coverage(countries: list[Country], path: Path) -> None:
    """Draw the share of each continent that has data.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    path : Path
        PNG file to write.
    """
    shares = coverage_by_continent(countries)
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(CONTINENTS))
    width = 0.25
    series = (
        ("Countries", "countries", "#fbb4ae", -width),
        ("Population", "population", "#b3cde3", 0.0),
        ("Land", "land", "#ccebc5", width),
    )
    for label, key, colour, offset in series:
        bars = ax.bar(
            [p + offset for p in x],
            shares[key],
            width,
            label=label,
            color=colour,
        )
        ax.bar_label(
            bars, fmt="%.1f%%", fontsize=8, fontweight="bold", padding=2
        )
    ax.set_xticks(list(x), CONTINENTS, rotation=45, fontsize=11)
    ax.set_ylabel("Coverage (%)", fontsize=12, fontweight="bold")
    ax.set_ylim(0, 105)
    ax.set_title(
        "Country, Population, and Land Coverage by Continent",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_years(countries: list[Country], path: Path) -> None:
    """Draw the years of data of each continent by time resolution.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    path : Path
        PNG file to write.
    """
    years = years_by_resolution(countries)
    fig, ax = plt.subplots(figsize=(10, 7))
    x = range(len(CONTINENTS))
    bottoms = [0] * len(CONTINENTS)
    for i, (resolution, values) in enumerate(years.items()):
        ax.bar(
            x,
            values,
            0.4,
            bottom=bottoms,
            color=YEAR_COLOURS[i % len(YEAR_COLOURS)],
            label=f"{resolution}-min",
        )
        bottoms = [b + v for b, v in zip(bottoms, values, strict=True)]
    ax.set_xticks(list(x), CONTINENTS, rotation=45, fontsize=11)
    ax.set_ylabel(
        "Total Number of Years Available", fontsize=12, fontweight="bold"
    )
    ax.set_title(
        "Electricity Demand Data by Continent and Frequency",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(title="Frequency", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_all(countries: list[Country], directory: Path) -> None:
    """Draw every figure into a folder.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    directory : Path
        Folder of the figures, created if needed.
    """
    directory.mkdir(parents=True, exist_ok=True)
    plot_coverage(countries, directory / "coverage_by_continent.png")
    plot_years(countries, directory / "frequency_coverage_by_continent.png")
