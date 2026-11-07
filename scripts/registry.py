"""Load and validate the electricity demand data sources of the list.

The list is kept in the data folder. ``sources/<id>.yaml`` holds one
data source, such as the ENTSO-E Transparency Platform, with its terms
of use and the countries and subdivisions (the entities) that it has
data for. The identifier of a source is that of its YAML file in
DemandCast, when DemandCast retrieves it. ``countries.csv`` holds every
country that the list considers, with its continent, its population in
millions and land area in km² (estimates for 2025).
``demandcast.yaml`` lists, for each source,
the entities whose series DemandCast retrieves, which the list marks.
``shapes.geojson`` holds the outlines of the countries and of the
subdivisions of the list, for the map of the figures. The README, the
map and the figures are generated from them.
"""

from __future__ import annotations

import csv
import datetime as dt
import re
from collections import Counter
from pathlib import Path
from typing import Annotated, Literal, get_args

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DEMANDCAST_FILE = "demandcast.yaml"
SHAPES_FILE = "shapes.geojson"
SOURCE_ID = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")

Continent = Literal[
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "Oceania",
]
CONTINENTS: tuple[Continent, ...] = get_args(Continent)

Url = Annotated[str, StringConstraints(pattern=r"^https?://\S+$")]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
CountryCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
EntityLabel = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}(-\S+)?$")]
Access = Literal["public", "on-request"]


def current_year() -> int:
    """Return the current year in UTC.

    Returns
    -------
    int
        The current year.
    """
    return dt.datetime.now(dt.UTC).year


class StrictModel(BaseModel):
    """Immutable model that rejects the fields it does not have."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Licence(StrictModel):
    """Terms under which the data of a source can be used.

    Attributes
    ----------
    name : str
        Short description of the terms, as shown in the list.
    url : str
        Page with the full terms.
    category : {"open", "non-commercial", "restricted"}
        ``open``: any use, possibly with attribution.
        ``non-commercial``: only non-commercial use.
        ``restricted``: personal use, all rights reserved, or use only
        with an authorisation.
    """

    name: Text
    url: Url
    category: Literal["open", "non-commercial", "restricted"]


class Entity(StrictModel):
    """Time series of a source for a country or one of its subdivisions.

    Attributes
    ----------
    country_code : str
        ISO 3166-1 alpha-3 code of the country, or XKX for Kosovo.
    subdivision_code, subdivision_name : str or None
        Code and name of the subdivision or grid region that the data
        covers, or None for the whole country.
    start : int
        First year with data.
    end : int or "present"
        Last year with data, or "present" if the data is still updated.
    resolution : int
        Time step of the data in minutes, which divides 60.
    url : str or None
        Page of the data of this entity, if it is not the page of the
        source.
    note : str or None
        Remark shown in the list, such as what the data measures when
        it is not demand.

    Notes
    -----
    The subdivision code is the ISO 3166-2 code without the country
    prefix, or for grid regions without one, the code that DemandCast
    uses, so that the two lists can be compared.
    """

    country_code: CountryCode
    subdivision_code: Text | None = None
    subdivision_name: Text | None = None
    start: int = Field(ge=1900)
    end: int | Literal["present"]
    resolution: int
    url: Url | None = None
    note: Text | None = None

    @field_validator("resolution")
    @classmethod
    def _divides_an_hour(cls, value: int) -> int:
        """Check that the resolution is an hour or a fraction of it.

        Parameters
        ----------
        value : int
            Time step in minutes.

        Returns
        -------
        int
            The time step, unchanged.

        Raises
        ------
        ValueError
            If the time step does not divide 60 minutes.
        """
        if value <= 0 or 60 % value:
            raise ValueError("must be a number of minutes that divides 60")
        return value

    @model_validator(mode="after")
    def _check_fields(self) -> Entity:
        """Check the subdivision and the years of the entity.

        Returns
        -------
        Entity
            The entity, unchanged.

        Raises
        ------
        ValueError
            If only one of the subdivision fields is given, or if the
            years are in the future or in the wrong order.
        """
        if (self.subdivision_code is None) != (self.subdivision_name is None):
            raise ValueError(
                "subdivision_code and subdivision_name must be given together"
            )
        year = current_year()
        if self.start > year:
            raise ValueError(f"start ({self.start}) is in the future")
        if self.end != "present":
            if self.end < self.start:
                raise ValueError(
                    f"end ({self.end}) is before start ({self.start})"
                )
            if self.end > year:
                raise ValueError(
                    f"end ({self.end}) is in the future: use 'present'"
                )
        return self

    @property
    def label(self) -> str:
        """Country code, and subdivision code after a dash."""
        if self.subdivision_code is None:
            return self.country_code
        return f"{self.country_code}-{self.subdivision_code}"

    @property
    def key(self) -> tuple[str, str | None, int, int | str, int]:
        """Country, subdivision, years and resolution of the entity."""
        return (
            self.country_code,
            self.subdivision_code,
            self.start,
            self.end,
            self.resolution,
        )


class Source(StrictModel):
    """Content of the data file of one data source.

    Attributes
    ----------
    name : str
        Name of the source, as shown in the list.
    url : str
        Page where the data can be downloaded or requested.
    access : {"public", "on-request"}
        ``on-request``: the data is given only after a request or a
        registration.
    licence : Licence
        Terms of use of the data.
    entities : list of Entity
        Countries and subdivisions with data, with their years.
    """

    name: Text
    url: Url
    access: Access = "public"
    licence: Licence
    entities: list[Entity] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_entities(self) -> Source:
        """Check that the entities are unique and need their own URL.

        Returns
        -------
        Source
            The source, unchanged.

        Raises
        ------
        ValueError
            If an entity is listed twice, or has the URL of the source.
        """
        for key, count in Counter(e.key for e in self.entities).items():
            if count > 1:
                raise ValueError(f"duplicate entity: {key}")
        for entity in self.entities:
            if entity.url == self.url:
                raise ValueError(
                    f"the url of the entity {entity.key} is that of the "
                    "source: leave it out"
                )
        return self


class Series(StrictModel):
    """Time series of one entity in one source, as listed in the README.

    Attributes
    ----------
    source_id : str
        Identifier of the source, the name of its data file.
    name : str
        Name of the source.
    url : str
        Page of the data of the entity.
    source_url : str
        Page of the source.
    access : {"public", "on-request"}
        Whether the data needs a request or a registration.
    licence : Licence
        Terms of use of the data.
    entity : Entity
        Country or subdivision, years and resolution of the data.
    demandcast : bool
        Whether DemandCast retrieves the series.
    """

    source_id: str
    name: str
    url: str
    source_url: str
    access: Access
    licence: Licence
    entity: Entity
    demandcast: bool = False

    @property
    def end_year(self) -> int:
        """Last year with data, with "present" as the current year."""
        end = self.entity.end
        return current_year() if end == "present" else end

    @property
    def period(self) -> str:
        """Years with data, such as "2015-present" or "2018"."""
        start, end = self.entity.start, self.entity.end
        return str(start) if end == start else f"{start}-{end}"


class Retrieved(StrictModel):
    """Content of the file of the series that DemandCast retrieves.

    Attributes
    ----------
    sources : dict
        For each source, the labels of the entities whose series
        DemandCast retrieves, such as "USA-TEX" or "DNK".
    """

    sources: dict[str, list[EntityLabel]] = Field(default_factory=dict)


class Country(StrictModel):
    """Country considered by the list, with its time series.

    Attributes
    ----------
    code : str
        ISO 3166-1 alpha-3 code, or XKX for Kosovo.
    name : str
        Common English name.
    continent : str
        One of `CONTINENTS`.
    population_millions : float
        Population in millions.
    land_area_km2 : int
        Land area in km².
    series : tuple of Series
        Time series of the country and of its subdivisions.
    """

    code: CountryCode
    name: Text
    continent: Continent
    population_millions: float = Field(gt=0)
    land_area_km2: int = Field(gt=0)
    series: tuple[Series, ...] = ()

    @property
    def years(self) -> int:
        """Number of calendar years covered by at least one series."""
        covered: set[int] = set()
        for series in self.series:
            covered.update(range(series.entity.start, series.end_year + 1))
        return len(covered)


Position = tuple[float, float]
Polygon = list[list[Position]]


class PolygonShape(StrictModel):
    """GeoJSON polygon: its exterior ring, then its holes."""

    type: Literal["Polygon"]
    coordinates: Polygon


class MultiPolygonShape(StrictModel):
    """GeoJSON multipolygon: the rings of each of its polygons."""

    type: Literal["MultiPolygon"]
    coordinates: list[Polygon]


class ShapeLabel(StrictModel):
    """Properties of a shape: the label of its entity."""

    label: EntityLabel


class ShapeFeature(StrictModel):
    """GeoJSON feature with the outline of a country or subdivision."""

    type: Literal["Feature"]
    properties: ShapeLabel
    geometry: Annotated[
        PolygonShape | MultiPolygonShape, Field(discriminator="type")
    ]


class ShapeCollection(StrictModel):
    """GeoJSON feature collection of the shapes file."""

    type: Literal["FeatureCollection"]
    features: list[ShapeFeature]


class RegistryError(Exception):
    """Invalid data files, with one problem per line of the message."""


def _describe(prefix: str, error: ValidationError) -> list[str]:
    """Describe each error of a validation, after a prefix.

    Parameters
    ----------
    prefix : str
        Where the errors are, such as the name of the file.
    error : ValidationError
        Error raised by pydantic.

    Returns
    -------
    list of str
        One line per error, with the field and the message.
    """
    lines = []
    for e in error.errors():
        location = ".".join(str(part) for part in e["loc"])
        lines.append(f"{prefix}: {location}: {e['msg']}")
    return lines


def _read_countries(
    path: Path,
) -> tuple[dict[str, tuple[str, dict[str, str]]], list[str]]:
    """Read the rows of the countries file.

    Parameters
    ----------
    path : Path
        The countries file.

    Returns
    -------
    rows : dict
        The location of each row in the file and its values, by country
        code.
    problems : list of str
        The duplicate countries.
    """
    rows: dict[str, tuple[str, dict[str, str]]] = {}
    problems = []
    with path.open(encoding="utf-8", newline="") as f:
        for line, row in enumerate(csv.DictReader(f), start=2):
            location = f"{path.parent.name}/{path.name}:{line}"
            code = row.get("code", "")
            if code in rows:
                problems.append(f"{location}: duplicate country {code}")
            rows[code] = (location, row)
    return rows, problems


def _read_sources(directory: Path) -> tuple[dict[str, Source], list[str]]:
    """Read and validate the data files of the sources.

    Parameters
    ----------
    directory : Path
        Folder of the data files, one per source.

    Returns
    -------
    sources : dict
        The sources, by identifier.
    problems : list of str
        The problems of the data files.
    """
    sources: dict[str, Source] = {}
    problems = []
    for path in sorted(directory.iterdir()):
        name = f"{directory.parent.name}/{directory.name}/{path.name}"
        if path.suffix != ".yaml":
            problems.append(f"{name}: data files must end in .yaml")
        elif not SOURCE_ID.match(path.stem):
            problems.append(
                f"{name}: the name must be lower-case letters and digits, "
                "separated by underscores"
            )
        else:
            try:
                content = yaml.safe_load(path.read_text(encoding="utf-8"))
                sources[path.stem] = Source.model_validate(content)
            except yaml.YAMLError as e:
                problems.append(f"{name}: invalid YAML: {e}")
            except ValidationError as e:
                problems.extend(_describe(name, e))
    return sources, problems


def _read_demandcast(
    path: Path, sources: dict[str, Source]
) -> tuple[set[tuple[str, str]], list[str]]:
    """Read the series that DemandCast retrieves.

    Parameters
    ----------
    path : Path
        File of the series that DemandCast retrieves.
    sources : dict
        The sources, by identifier.

    Returns
    -------
    marks : set of tuple
        The identifier of the source and the label of the entity of each
        series that DemandCast retrieves, or none if there is no file.
    problems : list of str
        The sources and entities of the file that the list lacks.
    """
    if not path.exists():
        return set(), []
    name = f"{path.parent.name}/{path.name}"
    try:
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
        retrieved = Retrieved.model_validate(content or {})
    except yaml.YAMLError as e:
        return set(), [f"{name}: invalid YAML: {e}"]
    except ValidationError as e:
        return set(), _describe(name, e)
    marks: set[tuple[str, str]] = set()
    problems = []
    for source_id, labels in retrieved.sources.items():
        source = sources.get(source_id)
        if source is None:
            if not (path.parent / "sources" / f"{source_id}.yaml").exists():
                problems.append(f"{name}: {source_id} is not a data source")
            continue
        known = {entity.label for entity in source.entities}
        for label in labels:
            if label not in known:
                problems.append(f"{name}: {source_id} has no entity {label}")
            marks.add((source_id, label))
    return marks, problems


def _series(
    sources: dict[str, Source],
    codes: set[str],
    marks: set[tuple[str, str]],
) -> tuple[dict[str, list[Series]], list[str]]:
    """Group the entities of the sources by country.

    Parameters
    ----------
    sources : dict
        The sources, by identifier.
    codes : set of str
        Codes of the countries in the countries file.
    marks : set of tuple
        The source and entity of each series that DemandCast retrieves.

    Returns
    -------
    series : dict
        The time series of each country, by country code.
    problems : list of str
        Entities of unknown countries, and subdivisions with two names.
    """
    series: dict[str, list[Series]] = {}
    names: dict[tuple[str, str], str | None] = {}
    problems = []
    for source_id, source in sources.items():
        prefix = f"data/sources/{source_id}.yaml"
        for entity in source.entities:
            code = entity.country_code
            if code not in codes:
                problems.append(
                    f"{prefix}: {code} is not a country code of countries.csv"
                )
                continue
            if entity.subdivision_code is not None:
                key = (code, entity.subdivision_code)
                name = names.setdefault(key, entity.subdivision_name)
                if name != entity.subdivision_name:
                    problems.append(
                        f"{prefix}: subdivision {code} "
                        f"{entity.subdivision_code} is named "
                        f"{entity.subdivision_name!r} here and {name!r} "
                        "elsewhere"
                    )
            series.setdefault(code, []).append(
                Series(
                    source_id=source_id,
                    name=source.name,
                    url=entity.url or source.url,
                    source_url=source.url,
                    access=source.access,
                    licence=source.licence,
                    entity=entity,
                    demandcast=(source_id, entity.label) in marks,
                )
            )
    return series, problems


def load_sources(data_dir: Path = DATA_DIR) -> dict[str, Source]:
    """Load and validate the data files of the sources.

    Parameters
    ----------
    data_dir : Path, default DATA_DIR
        Folder with the ``sources`` folder.

    Returns
    -------
    dict
        The sources, by identifier.

    Raises
    ------
    RegistryError
        If any data file of a source is invalid.
    """
    sources, problems = _read_sources(data_dir / "sources")
    if problems:
        raise RegistryError("\n".join(problems))
    return sources


def load_demandcast(
    data_dir: Path = DATA_DIR,
) -> set[tuple[str, str]]:
    """Load the series that the list marks as retrieved by DemandCast.

    Parameters
    ----------
    data_dir : Path, default DATA_DIR
        Folder with the ``sources`` folder and the file of the series
        that DemandCast retrieves.

    Returns
    -------
    set of tuple
        The identifier of the source and the label of the entity of each
        series that DemandCast retrieves.

    Raises
    ------
    RegistryError
        If a data file of a source, or the file of the series, is
        invalid.
    """
    sources = load_sources(data_dir)
    marks, problems = _read_demandcast(data_dir / DEMANDCAST_FILE, sources)
    if problems:
        raise RegistryError("\n".join(problems))
    return marks


def load_shapes(data_dir: Path = DATA_DIR) -> dict[str, list[Polygon]]:
    """Load the outlines of the countries and subdivisions of the map.

    Parameters
    ----------
    data_dir : Path, default DATA_DIR
        Folder with the shapes file.

    Returns
    -------
    dict
        The polygons of each country and subdivision, in degrees of
        longitude and latitude, by label of the entity.

    Raises
    ------
    RegistryError
        If the shapes file is missing or invalid, or has a label twice.

    Notes
    -----
    The file is written by ``scripts/shapes.py``. A polygon is a list
    of rings: the exterior anticlockwise, then the holes clockwise.
    """
    path = data_dir / SHAPES_FILE
    try:
        collection = ShapeCollection.model_validate_json(
            path.read_bytes(), strict=True
        )
    except OSError as e:
        raise RegistryError(f"{SHAPES_FILE}: {e.strerror}") from e
    except ValidationError as e:
        raise RegistryError("\n".join(_describe(SHAPES_FILE, e))) from e
    shapes: dict[str, list[Polygon]] = {}
    for feature in collection.features:
        label = feature.properties.label
        if label in shapes:
            raise RegistryError(f"{SHAPES_FILE}: duplicate shape {label}")
        geometry = feature.geometry
        shapes[label] = (
            [geometry.coordinates]
            if isinstance(geometry, PolygonShape)
            else geometry.coordinates
        )
    return shapes


def load(data_dir: Path = DATA_DIR) -> list[Country]:
    """Load and validate the data files of the list.

    Parameters
    ----------
    data_dir : Path, default DATA_DIR
        Folder with ``countries.csv`` and the ``sources`` folder.

    Returns
    -------
    list of Country
        Every country, by continent in the order of `CONTINENTS`, then
        by name.

    Raises
    ------
    RegistryError
        If any data file is invalid. The message lists every problem,
        so that they can all be fixed at once.
    """
    rows, problems = _read_countries(data_dir / "countries.csv")
    sources, source_problems = _read_sources(data_dir / "sources")
    marks, mark_problems = _read_demandcast(
        data_dir / DEMANDCAST_FILE, sources
    )
    series, series_problems = _series(sources, set(rows), marks)
    problems += source_problems + mark_problems + series_problems

    countries = []
    for code, (location, row) in rows.items():
        values = row | {"series": tuple(series.get(code, ()))}
        try:
            country = Country.model_validate(values)
        except ValidationError as e:
            problems.extend(_describe(location, e))
            continue
        countries.append(country)

    if problems:
        raise RegistryError("\n".join(problems))
    return sorted(
        countries, key=lambda c: (CONTINENTS.index(c.continent), c.name)
    )
