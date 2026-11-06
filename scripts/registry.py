"""Load and validate the electricity demand data sources of the list.

The list is kept in the data folder. ``sources/<code>.yaml`` holds the
data sources of one country, and is named after its ISO 3166-1
alpha-3 code. ``countries.csv`` holds every country that the list
considers, with its continent, its population in millions and land
area in km² (estimates for 2025), and whether it has been searched for
data. The README, the map and the figures are generated from them.
"""

from __future__ import annotations

import csv
import datetime as dt
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


class Source(StrictModel):
    """Time series of electricity demand from one provider.

    Attributes
    ----------
    provider : str
        Name of the organisation or platform that publishes the data.
    url : str
        Page where the data can be downloaded or requested.
    subdivision_code, subdivision_name : str or None
        Code and name of the subdivision or grid region that the data
        covers, or None for the whole country.
    start : int
        First year with data.
    end : int or "present"
        Last year with data, or "present" if the data is still updated.
    resolution : int
        Time step of the data in minutes, which divides 60.
    access : {"public", "on-request"}
        ``on-request``: the data is given only after a request or a
        registration.
    licence : Licence
        Terms of use of the data.
    note : str or None
        Remark shown in the list, such as what the data measures when
        it is not demand.

    Notes
    -----
    The subdivision code is the ISO 3166-2 code without the country
    prefix, or for grid regions without one, the code that DemandCast
    uses, so that the two lists can be compared.
    """

    provider: Text
    url: Url
    subdivision_code: Text | None = None
    subdivision_name: Text | None = None
    start: int = Field(ge=1900)
    end: int | Literal["present"]
    resolution: int
    access: Literal["public", "on-request"] = "public"
    licence: Licence
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
    def _check_fields(self) -> Source:
        """Check the subdivision and the years of the source.

        Returns
        -------
        Source
            The source, unchanged.

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
    def end_year(self) -> int:
        """Last year with data, with "present" as the current year."""
        return current_year() if self.end == "present" else self.end

    @property
    def period(self) -> str:
        """Years with data, such as "2015-present" or "2018"."""
        if self.end == self.start:
            return str(self.start)
        return f"{self.start}-{self.end}"


class CountrySources(StrictModel):
    """Content of the data file of one country.

    Attributes
    ----------
    sources : list of Source
        Data sources of the country and of its subdivisions.
    """

    sources: list[Source] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_sources(self) -> CountrySources:
        """Check that subdivisions have one name and sources are unique.

        Returns
        -------
        CountrySources
            The content, unchanged.

        Raises
        ------
        ValueError
            If a subdivision code has two names, or if a source is
            listed twice.
        """
        names: dict[str, str | None] = {}
        for source in self.sources:
            if source.subdivision_code is None:
                continue
            name = names.setdefault(
                source.subdivision_code, source.subdivision_name
            )
            if name != source.subdivision_name:
                raise ValueError(
                    f"subdivision {source.subdivision_code!r} has two "
                    f"names: {name!r} and {source.subdivision_name!r}"
                )
        for source, count in Counter(self.sources).items():
            if count > 1:
                raise ValueError(
                    f"duplicate source: {source.provider} {source.period}"
                )
        return self


class Country(StrictModel):
    """Country considered by the list, with its data sources.

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
    searched : bool
        Whether the country has been searched for data.
    sources : tuple of Source
        Data sources of the country and of its subdivisions.
    """

    code: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
    name: Text
    continent: Continent
    population_millions: float = Field(gt=0)
    land_area_km2: int = Field(gt=0)
    searched: bool
    sources: tuple[Source, ...] = ()

    @property
    def years(self) -> int:
        """Number of calendar years covered by at least one source."""
        covered: set[int] = set()
        for source in self.sources:
            covered.update(range(source.start, source.end_year + 1))
        return len(covered)


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


def _read_sources(
    directory: Path, codes: set[str]
) -> tuple[dict[str, tuple[Source, ...]], list[str]]:
    """Read and validate the data files of the countries.

    Parameters
    ----------
    directory : Path
        Folder of the data files, one per country.
    codes : set of str
        Codes of the countries in the countries file.

    Returns
    -------
    sources : dict
        The data sources of each country, by country code.
    problems : list of str
        The problems of the data files.
    """
    sources: dict[str, tuple[Source, ...]] = {}
    problems = []
    for path in sorted(directory.iterdir()):
        name = f"{directory.parent.name}/{directory.name}/{path.name}"
        if path.suffix != ".yaml":
            problems.append(f"{name}: data files must end in .yaml")
        elif path.stem not in codes:
            problems.append(
                f"{name}: {path.stem} is not a country code of countries.csv"
            )
        else:
            try:
                content = yaml.safe_load(path.read_text(encoding="utf-8"))
                parsed = CountrySources.model_validate(content)
                sources[path.stem] = tuple(parsed.sources)
            except yaml.YAMLError as e:
                problems.append(f"{name}: invalid YAML: {e}")
            except ValidationError as e:
                problems.extend(_describe(name, e))
    return sources, problems


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
    sources, source_problems = _read_sources(data_dir / "sources", set(rows))
    problems += source_problems

    countries = []
    for code, (location, row) in rows.items():
        if row.get("searched") not in {"yes", "no"}:
            problems.append(f"{location}: searched must be yes or no")
            continue
        values = row | {
            "searched": row["searched"] == "yes",
            "sources": sources.get(code, ()),
        }
        try:
            country = Country.model_validate(values)
        except ValidationError as e:
            problems.extend(_describe(location, e))
            continue
        if country.sources and not country.searched:
            problems.append(
                f"{location}: {code} has data sources, so searched must be yes"
            )
        countries.append(country)

    if problems:
        raise RegistryError("\n".join(problems))
    return sorted(
        countries, key=lambda c: (CONTINENTS.index(c.continent), c.name)
    )
