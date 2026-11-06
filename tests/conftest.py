"""Fixtures of the tests: a small, valid data folder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
import yaml

if TYPE_CHECKING:
    from pathlib import Path

COUNTRIES = """\
code,name,continent,population_millions,land_area_km2,searched
DZA,Algeria,Africa,40,2000,yes
EGY,Egypt,Africa,60,1000,yes
AGO,Angola,Africa,100,7000,no
JPN,Japan,Asia,120,300,yes
"""


def source(**changes: Any) -> dict[str, Any]:
    """Return a valid data source, with some fields changed.

    Parameters
    ----------
    **changes
        Fields to change or add.

    Returns
    -------
    dict
        The data source, as in a data file.
    """
    values: dict[str, Any] = {
        "provider": "Sonelgaz",
        "url": "https://example.org/data",
        "start": 2010,
        "end": 2019,
        "resolution": 60,
        "licence": {
            "name": "CC-BY 4.0",
            "url": "https://example.org/licence",
            "category": "open",
        },
    }
    return values | changes


def write_sources(data_dir: Path, code: str, sources: list[Any]) -> None:
    """Write the data file of a country.

    Parameters
    ----------
    data_dir : Path
        Data folder.
    code : str
        Code of the country, which names the file.
    sources : list
        Data sources of the country.
    """
    path = data_dir / "sources" / f"{code}.yaml"
    path.write_text(
        yaml.safe_dump({"sources": sources}, allow_unicode=True),
        encoding="utf-8",
    )


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Write a data folder with three countries, two of them with data.

    Parameters
    ----------
    tmp_path : Path
        Temporary folder of the test.

    Returns
    -------
    Path
        The data folder.
    """
    (tmp_path / "sources").mkdir()
    (tmp_path / "countries.csv").write_text(COUNTRIES, encoding="utf-8")
    write_sources(tmp_path, "DZA", [source()])
    write_sources(
        tmp_path,
        "JPN",
        [
            source(
                provider="TEPCO",
                subdivision_code="Kantō",
                subdivision_name="Kantō",
                start=2016,
                end="present",
                resolution=5,
                access="on-request",
            ),
            source(
                provider="ENTSO-E",
                url="https://example.org/a|b(c)",
                start=2015,
                end=2017,
                licence={
                    "name": "Personal use",
                    "url": "https://example.org/terms",
                    "category": "restricted",
                },
                note="Generation, proxy for demand",
            ),
        ],
    )
    return tmp_path
