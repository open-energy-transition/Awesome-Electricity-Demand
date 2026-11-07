"""Draw the figures of the coverage of the list.

The figures are computed from the countries and time series loaded by
`registry`, and from the outlines of its shapes file: a map of the
countries and subdivisions with data, coloured by their years of data;
the years of data of each continent by time resolution; and the share
of the countries, population and land area of each continent that have
data. Each figure is drawn twice, as ``<name>_light.png`` and
``<name>_dark.png``, for the light and dark themes of the reader.
"""

from __future__ import annotations

import bisect
import dataclasses
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PathCollection
from matplotlib.colors import LinearSegmentedColormap, to_hex
from matplotlib.patches import Patch
from matplotlib.path import Path as PlotPath
from matplotlib.transforms import blended_transform_factory

from registry import CONTINENTS, Country, Polygon

if TYPE_CHECKING:
    from pathlib import Path

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from numpy.typing import NDArray

WIDTH = 7.2
DPI = 200
YEAR_CLASSES = (5, 10, 20)
# En dashes, as in typeset ranges of years.
YEAR_LABELS = ("1–4 years", "5–9", "10–19", "20+")  # noqa: RUF001
METRICS = (
    ("Countries", "countries"),
    ("People", "population"),
    ("Land", "land"),
)
# Robinson projection: the length of each parallel and its distance
# from the equator, every 5 degrees of latitude from 0 to 90.
ROBINSON_LATITUDES = np.arange(0, 91, 5)
ROBINSON_LENGTHS = np.array(
    [
        *(1.0000, 0.9986, 0.9954, 0.9900, 0.9822, 0.9730, 0.9600),
        *(0.9427, 0.9216, 0.8962, 0.8679, 0.8350, 0.7986, 0.7597),
        *(0.7186, 0.6732, 0.6213, 0.5722, 0.5322),
    ]
)
ROBINSON_HEIGHTS = np.array(
    [
        *(0.0000, 0.0620, 0.1240, 0.1860, 0.2480, 0.3100, 0.3720),
        *(0.4340, 0.4958, 0.5571, 0.6176, 0.6769, 0.7346, 0.7903),
        *(0.8435, 0.8936, 0.9394, 0.9761, 1.0000),
    ]
)


@dataclasses.dataclass(frozen=True)
class Theme:
    """Colours of the figures for a light or a dark page.

    Attributes
    ----------
    name : str
        Suffix of the files of the theme.
    surface : str
        Background.
    ink, ink2, muted : str
        Titles and values, labels, and axis notes.
    grid, base : str
        Grid lines, and the axis line and the range of the dots.
    land : str
        Countries without national data.
    classes : tuple of str
        The classes of years of data, from the fewest years.
    resolutions : tuple of str
        Ramp of the time resolutions, from the finest.
    metrics : tuple of str
        Countries, people and land in the share of each continent.

    Notes
    -----
    The ramps are one blue, with the strongest colour for the most
    years and the finest resolution: darker on a light page, lighter on
    a dark one. Each ramp was checked for its contrast with the surface
    and for the separation of adjacent steps with colour vision
    deficiencies. The green of the metrics has less than 3:1 contrast
    with the light surface, so every dot has its value written.
    """

    name: str
    surface: str
    ink: str
    ink2: str
    muted: str
    grid: str
    base: str
    land: str
    classes: tuple[str, ...]
    resolutions: tuple[str, ...]
    metrics: tuple[str, ...]


THEMES = (
    Theme(
        name="light",
        surface="#fcfcfb",
        ink="#0b0b0b",
        ink2="#52514e",
        muted="#898781",
        grid="#e1e0d9",
        base="#c3c2b7",
        land="#e4e3dd",
        classes=("#86b6ef", "#3987e5", "#1c5cab", "#0d366b"),
        resolutions=("#0d366b", "#1c5cab", "#2a78d6", "#5598e7", "#86b6ef"),
        metrics=("#2a78d6", "#eb6834", "#1baf7a"),
    ),
    Theme(
        name="dark",
        surface="#1a1a19",
        ink="#f0efec",
        ink2="#c3c2b7",
        muted="#898781",
        grid="#2c2c2a",
        base="#383835",
        land="#2c2c2a",
        classes=("#184f95", "#256abf", "#5598e7", "#9ec5f4"),
        resolutions=("#b7d3f6", "#6da7ec", "#3987e5", "#256abf", "#184f95"),
        metrics=("#3987e5", "#d95926", "#199e70"),
    ),
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
        For each resolution in minutes, from the finest, the years of
        data of each continent, in the order of `CONTINENTS`.

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


def years_by_entity(countries: list[Country]) -> dict[str, int]:
    """Count the years of data of each country and subdivision.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.

    Returns
    -------
    dict
        The number of years with data from any source, by label of the
        entity: the country code for national data, and the country
        and subdivision codes for a subdivision.
    """
    covered: dict[str, set[int]] = {}
    for country in countries:
        for series in country.series:
            covered.setdefault(series.entity.label, set()).update(
                range(series.entity.start, series.end_year + 1)
            )
    return {label: len(years) for label, years in covered.items()}


def year_class(years: int) -> int:
    """Return the class of a number of years of data.

    Parameters
    ----------
    years : int
        Number of years, at least 1.

    Returns
    -------
    int
        Index of the class in `YEAR_LABELS`.
    """
    return bisect.bisect_right(YEAR_CLASSES, years)


def ramp(colours: tuple[str, ...], n: int) -> list[str]:
    """Pick n steps of a colour ramp.

    Parameters
    ----------
    colours : tuple of str
        The steps of the ramp, from the strongest.
    n : int
        Number of steps needed.

    Returns
    -------
    list of str
        The steps, spread over the ramp from its strongest step.

    Notes
    -----
    Up to the length of the ramp, the steps are its own. Beyond it, they
    are interpolated, so that a new resolution in the list never stops
    the build.
    """
    if n <= 1:
        return list(colours[:n])
    if n <= len(colours):
        last = len(colours) - 1
        return [colours[round(i * last / (n - 1))] for i in range(n)]
    cmap = LinearSegmentedColormap.from_list("ramp", list(colours))
    return [to_hex(cmap(i / (n - 1))) for i in range(n)]


def resolution_label(minutes: int) -> str:
    """Return the label of a time resolution.

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


def robinson(
    lon: NDArray[np.float64], lat: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Project longitudes and latitudes with the Robinson projection.

    Parameters
    ----------
    lon, lat : numpy.ndarray
        Coordinates in degrees.

    Returns
    -------
    x, y : numpy.ndarray
        Coordinates on a sphere of radius 1.

    Notes
    -----
    The projection interpolates linearly between the values of its
    table, every 5 degrees, which is exact enough for a map of the
    world.
    """
    alat = np.abs(lat)
    x = (
        0.8487
        * np.interp(alat, ROBINSON_LATITUDES, ROBINSON_LENGTHS)
        * np.radians(lon)
    )
    y = (
        1.3523
        * np.interp(alat, ROBINSON_LATITUDES, ROBINSON_HEIGHTS)
        * np.sign(lat)
    )
    return x, y


def outline_path(polygons: list[Polygon]) -> PlotPath:
    """Project the polygons of a shape into one path.

    Parameters
    ----------
    polygons : list of Polygon
        The polygons of the shape, each its exterior then its holes.

    Returns
    -------
    matplotlib.path.Path
        The rings, projected, which fill without the holes.
    """
    rings = []
    for polygon in polygons:
        for ring in polygon:
            coordinates = np.asarray(ring, dtype=float)
            x, y = robinson(coordinates[:, 0], coordinates[:, 1])
            rings.append(PlotPath(np.column_stack([x, y]), closed=True))
    return PlotPath.make_compound_path(*rings)


def _figure(theme: Theme, height: float) -> Figure:
    """Create a figure on the surface of a theme.

    Parameters
    ----------
    theme : Theme
        Colours of the figure.
    height : float
        Height in inches.

    Returns
    -------
    matplotlib.figure.Figure
        The figure.
    """
    return plt.figure(figsize=(WIDTH, height), facecolor=theme.surface)


def _style(ax: Axes, theme: Theme) -> None:
    """Draw recessive axes for horizontal bars or dots.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes.
    theme : Theme
        Colours of the figure.
    """
    ax.set_facecolor(theme.surface)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(theme.base)
    ax.tick_params(colors=theme.muted, labelcolor=theme.ink2, length=0)
    ax.grid(axis="x", color=theme.grid, linewidth=0.8)
    ax.set_axisbelow(True)


def _title(fig: Figure, theme: Theme, title: str, subtitle: str) -> None:
    """Write the title and subtitle of a figure, at its top left.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure.
    theme : Theme
        Colours of the figure.
    title, subtitle : str
        The texts.
    """
    inches = fig.get_figheight()
    fig.text(
        0.012,
        1 - 0.1 / inches,
        title,
        ha="left",
        va="top",
        fontsize=13,
        fontweight="bold",
        color=theme.ink,
    )
    fig.text(
        0.012,
        1 - 0.36 / inches,
        subtitle,
        ha="left",
        va="top",
        fontsize=9.5,
        color=theme.ink2,
    )


def _save(fig: Figure, path: Path) -> None:
    """Write a figure as PNG and close it.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure.
    path : Path
        PNG file to write.
    """
    fig.savefig(path, dpi=DPI, facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_map(
    countries: list[Country],
    shapes: dict[str, list[Polygon]],
    theme: Theme,
    path: Path,
) -> None:
    """Draw the map of the countries and subdivisions with data.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    shapes : dict
        The outlines of the countries and subdivisions, by label.
    theme : Theme
        Colours of the figure.
    path : Path
        PNG file to write.

    Notes
    -----
    Each country with national data, and each subdivision on top of its
    country, is coloured by its own years of data, in the classes of
    `YEAR_LABELS`. An entity without an outline is left out.
    """
    years = years_by_entity(countries)
    fig = _figure(theme, 4.3)
    ax = fig.add_axes((0.0, 0.11, 1.0, 0.75))
    ax.axis("off")
    latitudes = np.linspace(-90.0, 90.0, 181)
    edge_x, edge_y = robinson(np.full_like(latitudes, 180.0), latitudes)
    globe = np.concatenate(
        [
            np.column_stack([edge_x, edge_y]),
            np.column_stack([-edge_x[::-1], edge_y[::-1]]),
        ]
    )
    ax.fill(
        globe[:, 0],
        globe[:, 1],
        facecolor=theme.surface,
        edgecolor=theme.base,
        linewidth=0.8,
    )
    layers: tuple[list[tuple[PlotPath, str]], ...] = ([], [], [])
    for label, polygons in shapes.items():
        is_country = "-" not in label
        if label in years:
            colour = theme.classes[year_class(years[label])]
            layers[1 if is_country else 2].append(
                (outline_path(polygons), colour)
            )
        if is_country:
            layers[0].append((outline_path(polygons), theme.land))
    for layer in layers:
        ax.add_collection(
            PathCollection(
                [p for p, _ in layer],
                facecolors=[c for _, c in layer],
                edgecolors=theme.surface,
                linewidths=0.3,
            )
        )
    ax.set_xlim(globe[:, 0].min() - 0.02, globe[:, 0].max() + 0.02)
    ax.set_ylim(-1.38, 1.38)
    ax.set_aspect("equal")
    handles = [
        Patch(facecolor=c, label=label)
        for c, label in zip(theme.classes, YEAR_LABELS, strict=True)
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncols=len(handles),
        frameon=False,
        fontsize=8.5,
        labelcolor=theme.ink2,
        handlelength=1.1,
        columnspacing=1.2,
        bbox_to_anchor=(0.5, 0.0),
    )
    covered = sum(bool(c.series) for c in countries)
    subdivisions = sum("-" in label for label in years)
    _title(
        fig,
        theme,
        "Where the list has demand data",
        f"{covered} countries and {subdivisions} subdivisions, each "
        "coloured by its own years of data",
    )
    _save(fig, path)


def plot_years(countries: list[Country], theme: Theme, path: Path) -> None:
    """Draw the years of data of each continent by time resolution.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    theme : Theme
        Colours of the figure.
    path : Path
        PNG file to write.
    """
    years = years_by_resolution(countries)
    colours = ramp(theme.resolutions, len(years))
    fig = _figure(theme, 3.6)
    ax = fig.add_axes((0.16, 0.12, 0.77, 0.62))
    _style(ax, theme)
    rows = range(len(CONTINENTS) - 1, -1, -1)
    lefts = np.zeros(len(CONTINENTS))
    for colour, (resolution, values) in zip(
        colours, years.items(), strict=True
    ):
        ax.barh(
            rows,
            values,
            left=lefts,
            height=0.62,
            color=colour,
            edgecolor=theme.surface,
            linewidth=1.5,
            label=resolution_label(resolution),
        )
        lefts += np.asarray(values, dtype=float)
    for row, total in zip(rows, lefts, strict=True):
        ax.annotate(
            f"{total:.0f}",
            (total, row),
            xytext=(4, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=theme.ink,
        )
    ax.set_yticks(list(rows), CONTINENTS, fontsize=10)
    ax.tick_params(axis="x", labelsize=9)
    ax.set_xlim(0, max(lefts.max(), 1) * 1.1)
    ax.set_xlabel(
        "years of data, summed over the countries",
        fontsize=9,
        color=theme.muted,
    )
    ax.legend(
        ncols=max(len(years), 1),
        loc="lower left",
        bbox_to_anchor=(-0.01, 1.0),
        frameon=False,
        fontsize=9,
        handlelength=1.1,
        columnspacing=1.2,
        labelcolor=theme.ink2,
    )
    _title(
        fig,
        theme,
        "Years of demand data by continent",
        "Each country counts each year once per time resolution",
    )
    _save(fig, path)


def plot_coverage(countries: list[Country], theme: Theme, path: Path) -> None:
    """Draw the share of each continent that has data.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    theme : Theme
        Colours of the figure.
    path : Path
        PNG file to write.

    Notes
    -----
    The three shares of a continent are dots on one line, joined by
    their range, and written in columns on the right, whose headers are
    the legend.
    """
    shares = coverage_by_continent(countries)
    columns = (1.17, 1.41, 1.65)
    fig = _figure(theme, 3.6)
    ax = fig.add_axes((0.16, 0.12, 0.42, 0.58))
    _style(ax, theme)
    side = blended_transform_factory(ax.transAxes, ax.transData)
    rows = range(len(CONTINENTS) - 1, -1, -1)
    for row, i in zip(rows, range(len(CONTINENTS)), strict=True):
        values = [shares[key][i] for _, key in METRICS]
        ax.plot(
            [min(values), max(values)],
            [row, row],
            color=theme.base,
            linewidth=2,
            zorder=1,
        )
        for value, colour, x in zip(
            values, theme.metrics, columns, strict=True
        ):
            ax.scatter(
                value,
                row,
                s=60,
                color=colour,
                edgecolor=theme.surface,
                linewidth=1.5,
                zorder=3,
                clip_on=False,
            )
            ax.text(
                x,
                row,
                f"{value:.0f}%",
                transform=side,
                ha="right",
                va="center",
                fontsize=9,
                color=theme.ink2,
            )
    header = len(CONTINENTS) - 0.35
    for (label, _), colour, x in zip(
        METRICS, theme.metrics, columns, strict=True
    ):
        ax.text(
            x,
            header,
            label,
            transform=side,
            ha="right",
            va="center",
            fontsize=8.5,
            color=theme.ink2,
        )
        ax.scatter(
            [x - 0.05],
            [header + 0.42],
            transform=side,
            s=40,
            color=colour,
            edgecolor=theme.surface,
            linewidth=1.5,
            clip_on=False,
        )
    ax.set_yticks(list(rows), CONTINENTS, fontsize=10)
    ax.set_xlim(0, 100)
    ax.set_xticks(
        [0, 25, 50, 75, 100],
        ["0%", "25%", "50%", "75%", "100%"],
        fontsize=9,
    )
    _title(
        fig,
        theme,
        "Share of each continent with demand data",
        "Countries with any data source, and their population and land area",
    )
    _save(fig, path)


def plot_all(
    countries: list[Country],
    shapes: dict[str, list[Polygon]],
    directory: Path,
) -> None:
    """Draw every figure, in both themes, into a folder.

    Parameters
    ----------
    countries : list of Country
        Every country of the list.
    shapes : dict
        The outlines of the countries and subdivisions, by label.
    directory : Path
        Folder of the figures, created if needed.
    """
    directory.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        plot_map(countries, shapes, theme, directory / f"map_{theme.name}.png")
        plot_years(
            countries,
            theme,
            directory / f"years_by_continent_{theme.name}.png",
        )
        plot_coverage(
            countries,
            theme,
            directory / f"coverage_by_continent_{theme.name}.png",
        )
