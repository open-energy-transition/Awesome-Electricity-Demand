"""Fixtures of the tests: a small, valid data folder."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
import yaml

if TYPE_CHECKING:
    from pathlib import Path

COUNTRIES = """\
code,name,continent,population_millions,land_area_km2
DZA,Algeria,Africa,40,2000
EGY,Egypt,Africa,60,1000
AGO,Angola,Africa,100,7000
JPN,Japan,Asia,120,300
"""


def entity(**changes: Any) -> dict[str, Any]:
    """Return a valid entity, with some fields changed.

    Parameters
    ----------
    **changes
        Fields to change or add.

    Returns
    -------
    dict
        The entity, as in a data file.
    """
    values: dict[str, Any] = {
        "country_code": "DZA",
        "start": 2010,
        "end": 2019,
        "resolution": 60,
    }
    return values | changes


def source(entities: list[Any], **changes: Any) -> dict[str, Any]:
    """Return a valid data source, with some fields changed.

    Parameters
    ----------
    entities : list
        Entities of the source.
    **changes
        Fields to change or add.

    Returns
    -------
    dict
        The data source, as in a data file.
    """
    values: dict[str, Any] = {
        "name": "Sonelgaz",
        "url": "https://example.org/data",
        "licence": {
            "name": "CC BY 4.0",
            "url": "https://example.org/licence",
            "category": "open",
        },
        "entities": entities,
    }
    return values | changes


def write_source(data_dir: Path, source_id: str, content: Any) -> None:
    """Write the data file of a source.

    Parameters
    ----------
    data_dir : Path
        Data folder.
    source_id : str
        Identifier of the source, which names the file.
    content : Any
        Content of the file.
    """
    path = data_dir / "sources" / f"{source_id}.yaml"
    path.write_text(
        yaml.safe_dump(content, allow_unicode=True), encoding="utf-8"
    )


def write_shapes(data_dir: Path, labels: list[str]) -> None:
    """Write a shapes file with a square for each entity.

    Parameters
    ----------
    data_dir : Path
        Data folder.
    labels : list of str
        Labels of the entities, each with a square of 10 degrees along
        the equator, the first with a square hole.
    """
    features = []
    for i, label in enumerate(labels):
        x = 10.0 * i
        rings = [[[x, 0.0], [x + 9, 0.0], [x + 9, 9.0], [x, 9.0], [x, 0.0]]]
        if i == 0:
            rings.append([[2, 2], [2, 4], [4, 4], [4, 2], [2, 2]])
        features.append(
            {
                "type": "Feature",
                "properties": {"label": label},
                "geometry": {"type": "Polygon", "coordinates": rings},
            }
        )
    (data_dir / "shapes.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Write a data folder with four countries, two of them with data.

    Parameters
    ----------
    tmp_path : Path
        Temporary folder of the test.

    Returns
    -------
    Path
        The data folder.

    Notes
    -----
    Japan has a national series from a source that covers two
    countries, and a series of a subdivision that needs a request.
    DemandCast retrieves the series of Sonelgaz and of TEPCO. Each
    country and the subdivision have a shape.
    """
    (tmp_path / "sources").mkdir()
    (tmp_path / "countries.csv").write_text(COUNTRIES, encoding="utf-8")
    write_source(tmp_path, "sonelgaz", source([entity()]))
    write_source(
        tmp_path,
        "entsoe",
        source(
            [
                entity(
                    country_code="JPN",
                    start=2015,
                    end=2017,
                    url="https://example.org/a|b(c)",
                    note="Generation, proxy for demand",
                ),
                entity(country_code="DZA", start=2012, end=2013),
            ],
            name="ENTSO-E",
            licence={
                "name": "Personal use",
                "url": "https://example.org/terms",
                "category": "restricted",
            },
        ),
    )
    write_source(
        tmp_path,
        "tepco",
        source(
            [
                entity(
                    country_code="JPN",
                    subdivision_code="Kantō",
                    subdivision_name="Kantō",
                    start=2016,
                    end="present",
                    resolution=5,
                )
            ],
            name="TEPCO",
            access="on-request",
        ),
    )
    (tmp_path / "demandcast.yaml").write_text(
        "sources:\n  sonelgaz:\n  - DZA\n  tepco:\n  - JPN-Kantō\n",
        encoding="utf-8",
    )
    write_shapes(tmp_path, ["DZA", "EGY", "AGO", "JPN", "JPN-Kantō"])
    return tmp_path
