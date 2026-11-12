r"""Write the shapes of the map of the list, with DemandCast's code.

The map of the site colours each country and subdivision of the list by
its years of data. ``data/shapes.geojson`` holds their outlines, one
feature per line, each with the label of its entity: every country of
Natural Earth at 1:50m, under its code, and each subdivision of the
list, under its country code and subdivision code, as DemandCast draws
it, from Natural Earth or from the shapes of grid regions of DemandCast.
The outlines are simplified and rounded to 0.01 degrees, enough for a
map of the world.

The script runs in the environment of DemandCast, whose code finds the
shapes, from the folder ``demandcast`` of its repository::

    PYTHONPATH=. uv run --locked python \
        path/to/Awesome-Electricity-Demand/scripts/shapes.py

It lists the subdivisions of the list without a shape.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import cartopy.io.shapereader
import geopandas
import shapely
import utils.shapes

import registry

SHAPES_FILE = registry.DATA_DIR / registry.SHAPES_FILE
TOLERANCE = 0.05
GRID = 0.01
# Codes of Natural Earth that differ from those of the list.
COUNTRY_CODES = {"KOS": "XKX", "SDS": "SSD", "PSX": "PSE"}
# Price areas without a shape in DemandCast, as unions of regions.
COMPOSITES = {
    "DNK-DK1": ["DK-81", "DK-82", "DK-83"],
    "DNK-DK2": ["DK-84", "DK-85"],
}


def natural_earth(name: str, resolution: str) -> Any:
    """Read a layer of the cultural shapes of Natural Earth.

    Parameters
    ----------
    name : str
        Name of the layer, such as "admin_0_countries".
    resolution : str
        Scale of the layer: "10m", "50m" or "110m".

    Returns
    -------
    geopandas.GeoDataFrame
        The shapes of the layer.
    """
    path = cartopy.io.shapereader.natural_earth(
        resolution=resolution, category="cultural", name=name
    )
    return geopandas.read_file(path)


def feature(label: str, geometry: Any) -> dict[str, Any] | None:
    """Simplify a shape into a GeoJSON feature of an entity.

    Parameters
    ----------
    label : str
        Label of the entity.
    geometry : shapely.Geometry
        Shape of the entity, in degrees.

    Returns
    -------
    dict or None
        The feature, with its exterior rings anticlockwise and its holes
        clockwise, as the maps fill them, or None if nothing is left of
        the shape on the grid, as for the smallest territories.
    """
    geometry = shapely.simplify(geometry, TOLERANCE, preserve_topology=True)
    geometry = shapely.set_precision(geometry, GRID)
    if geometry.is_empty:
        return None
    geometry = shapely.orient_polygons(geometry)
    return {
        "type": "Feature",
        "properties": {"label": label},
        "geometry": shapely.geometry.mapping(geometry),
    }


def country_features() -> list[dict[str, Any]]:
    """Return the shapes of the countries of Natural Earth.

    Returns
    -------
    list of dict
        A feature for each country but Antarctica and those too small
        to be left on the grid, under the code of the list.
    """
    countries = natural_earth("admin_0_countries", "50m")
    features = []
    for code, geometry in zip(
        countries["ADM0_A3"], countries.geometry, strict=True
    ):
        if code != "ATA":
            shape = feature(COUNTRY_CODES.get(code, code), geometry)
            if shape is not None:
                features.append(shape)
    return features


def subdivision_features() -> tuple[list[dict[str, Any]], list[str]]:
    """Return the shapes of the subdivisions of the list.

    Returns
    -------
    features : list of dict
        A feature for each subdivision with a shape.
    missing : list of str
        The labels of the subdivisions without a shape, with the error.
    """
    regions = natural_earth("admin_1_states_provinces", "10m")
    labels = sorted(
        {
            entity.label
            for source in registry.load_sources().values()
            for entity in source.entities
            if entity.subdivision_code is not None
        }
    )
    features, missing = [], []
    for label in labels:
        try:
            if label in COMPOSITES:
                shape = regions[regions["iso_3166_2"].isin(COMPOSITES[label])]
            else:
                shape = utils.shapes.get_entity_shape(
                    label.replace("-", "_", 1), make_plot=False
                )
            shape = shape if shape.crs is None else shape.to_crs(4326)
            geometry = shapely.union_all(shape.geometry.to_numpy())
        except Exception as e:  # noqa: BLE001 - list every missing shape.
            missing.append(f"{label}: {type(e).__name__}: {e}")
            continue
        shape = feature(label, geometry)
        if shape is None:
            missing.append(f"{label}: empty after simplification")
            continue
        features.append(shape)
    return features, missing


def main() -> int:
    """Write the shapes file and list the subdivisions without a shape.

    Returns
    -------
    int
        0, also when some subdivisions have no shape.
    """
    subdivisions, missing = subdivision_features()
    features = country_features() + subdivisions
    lines = [json.dumps(f, separators=(",", ":")) for f in features]
    SHAPES_FILE.write_text(
        '{"type":"FeatureCollection","features":[\n'
        + ",\n".join(lines)
        + "\n]}\n",
        encoding="utf-8",
    )
    sys.stdout.write(f"{len(features)} shapes written to {SHAPES_FILE}.\n")
    for line in missing:
        sys.stdout.write(f"No shape for {line}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
