r"""Write the shapes of the map of the list, with DemandCast's code.

The map of the site colours each country and subdivision of the list by
its years of data. ``data/shapes.geojson`` holds their outlines, one
feature per line, each with the label of its entity: every country of
Natural Earth at 1:50m, under its code, France as metropolitan France,
as in the totals of the list, and each subdivision of the
list, under its country code and subdivision code, as DemandCast draws
it: a standard subdivision from Natural Earth, and a non-standard one,
such as the area of a grid, from the shapes of DemandCast, either a
shapefile or a union of standard subdivisions of Natural Earth in its
``composites.yaml``. The outlines are simplified and rounded to 0.01
degrees, enough for a map of the world.

Each country with subdivisions also gets the shares of its people and
of its land inside the union of their outlines, for the figure of the
coverage: the people from the density of population of SEDAC (GPW
v4.11) in 2020 at 30 arc-seconds, which DemandCast downloads into its
data folder, and the land from geodesic areas.

The script runs in the environment of DemandCast, whose code finds the
shapes, from the folder ``demandcast`` of its repository::

    PYTHONPATH=. uv run --locked python \
        path/to/Awesome-Electricity-Demand/scripts/shapes.py

It lists the subdivisions of the list without a shape.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import cartopy.io.shapereader
import geopandas
import numpy as np
import pyproj
import rasterio
import rasterio.mask
import retrievals.gridded_population
import shapely
import utils.paths
import utils.shapes

import registry

SHAPES_FILE = registry.DATA_DIR / registry.SHAPES_FILE
TOLERANCE = 0.05
GRID = 0.01
POPULATION_YEAR = 2020
GEOD = pyproj.Geod(ellps="WGS84")
# Radius of the sphere of the grid of population, in km.
EARTH_RADIUS = 6371.0088
# Half the width, in degrees, of the strips of a country outside its
# subdivisions that count as inside them.
SLIVER = 0.04
# Codes of Natural Earth that differ from those of the list.
COUNTRY_CODES = {"KOS": "XKX", "SDS": "SSD", "PSX": "PSE"}
# Countries whose totals in the list are those of one map unit of
# Natural Earth: metropolitan France, without its overseas departments.
COUNTRY_UNITS = {"FRA": "FXX"}


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
        to be left on the grid, under the code of the list, as one map
        unit for those of `COUNTRY_UNITS`.
    """
    countries = natural_earth("admin_0_countries", "50m")
    units = natural_earth("admin_0_map_units", "50m")
    features = []
    for code, geometry in zip(
        countries["ADM0_A3"], countries.geometry, strict=True
    ):
        outline = geometry
        if code in COUNTRY_UNITS:
            unit = units["SU_A3"] == COUNTRY_UNITS[code]
            outline = shapely.union_all(units.geometry[unit].to_numpy())
        if code != "ATA":
            shape = feature(COUNTRY_CODES.get(code, code), outline)
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


def population_grid() -> str:
    """Return the grid of the density of population, downloading it.

    Returns
    -------
    str
        Path of the GeoTIFF of the density of population of SEDAC in
        `POPULATION_YEAR`, in people per km², in the data folder of
        DemandCast, which downloads it if it is not there.
    """
    folder = utils.paths.get_gridded_folder("population", "raw")
    os.makedirs(folder, exist_ok=True)
    retrievals.gridded_population._download_historical_gridded_population_density(
        folder, POPULATION_YEAR
    )
    return os.path.join(folder, f"{POPULATION_YEAR}.tif")


def polygons(geometry: Any) -> list[Any]:
    """Return the polygons of a shape, without its lines and points.

    Parameters
    ----------
    geometry : shapely.Geometry
        The shape.

    Returns
    -------
    list of shapely.Polygon
        Its polygons.
    """
    return [
        part
        for part in shapely.get_parts(geometry)
        if part.geom_type == "Polygon"
    ]


def people(grid: Any, geometry: Any) -> float:
    """Count the people of a shape on the grid of density of population.

    Parameters
    ----------
    grid : rasterio.DatasetReader
        The grid of the density of population, in people per km².
    geometry : shapely.Geometry
        The shape, in degrees.

    Returns
    -------
    float
        The people of the cells whose centres are inside the shape.

    Notes
    -----
    Each polygon is read on its own, as the box of a whole country
    across the antimeridian, such as Russia, would be too large. The
    cells without data have a negative value.
    """
    total = 0.0
    for polygon in polygons(geometry):
        data, transform = rasterio.mask.mask(
            grid, [polygon], crop=True, filled=True, nodata=0
        )
        density = np.clip(data[0], 0, None)
        edges = transform.f + transform.e * np.arange(density.shape[0] + 1)
        areas = (
            EARTH_RADIUS**2
            * np.radians(abs(transform.a))
            * np.abs(np.diff(np.sin(np.radians(edges))))
        )
        total += float((density * areas[:, None]).sum())
    return total


def land(geometry: Any) -> float:
    """Return the geodesic area of a shape.

    Parameters
    ----------
    geometry : shapely.Geometry
        The shape, in degrees.

    Returns
    -------
    float
        Its area on the ellipsoid of WGS 84, in m².
    """
    return sum(
        abs(float(GEOD.geometry_area_perimeter(polygon)[0]))
        for polygon in polygons(geometry)
    )


def left_out(whole: Any, covered: Any, regions: Any) -> Any:
    """Return the part of a country outside its subdivisions.

    Parameters
    ----------
    whole : shapely.Geometry
        Outline of the country.
    covered : shapely.Geometry
        Union of the outlines of its subdivisions.
    regions : shapely.Geometry
        Union of its standard subdivisions of Natural Earth.

    Returns
    -------
    shapely.Geometry
        The polygons of the country outside its subdivisions.

    Notes
    -----
    The outlines of the countries and of their subdivisions are drawn
    at different scales, and disagree along the coasts. So the parts
    of the country outside its standard subdivisions, such as islands
    that only the outline of the country has, go to the nearer of the
    subdivisions and of the rest; and the strips narrower than twice
    `SLIVER`, about 8 km, stay inside, or the coastal cities would be
    left out.
    """
    excluded = shapely.union_all(
        polygons(whole.difference(covered).intersection(regions))
    )
    stray = polygons(whole.difference(covered).difference(regions))
    far = [
        part
        for part in stray
        if not excluded.is_empty
        and part.distance(covered) > part.distance(excluded)
    ]
    outside = shapely.union_all([excluded, *far])
    return shapely.union_all(
        polygons(outside.buffer(-SLIVER).buffer(SLIVER).intersection(outside))
    )


def add_shares(features: list[dict[str, Any]]) -> None:
    """Add the shares inside its subdivisions to each country feature.

    Parameters
    ----------
    features : list of dict
        The features of the countries and subdivisions. Each country
        with subdivisions gets the shares of its people and of its land
        inside the union of their outlines, as ``people`` and ``land``,
        rounded to 4 digits.
    """
    regions = natural_earth("admin_1_states_provinces", "10m")
    natural_earth_codes = {v: k for k, v in COUNTRY_CODES.items()}
    shapes = {
        f["properties"]["label"]: shapely.geometry.shape(f["geometry"])
        for f in features
    }
    parts: dict[str, list[Any]] = {}
    for label, shape in shapes.items():
        country, _, subdivision = label.partition("-")
        if subdivision:
            parts.setdefault(country, []).append(shape)
    with rasterio.open(population_grid()) as grid:
        for f in features:
            code = f["properties"]["label"]
            if code not in parts:
                continue
            whole = shapes[code]
            own = regions["adm0_a3"] == natural_earth_codes.get(code, code)
            outside = left_out(
                whole,
                shapely.union_all(parts[code]),
                shapely.union_all(regions.geometry[own].to_numpy()),
            )
            inside = whole.difference(outside)
            f["properties"]["people"] = round(
                people(grid, inside) / people(grid, whole), 4
            )
            f["properties"]["land"] = round(land(inside) / land(whole), 4)


def main() -> int:
    """Write the shapes file and list the subdivisions without a shape.

    Returns
    -------
    int
        0, also when some subdivisions have no shape.
    """
    subdivisions, missing = subdivision_features()
    features = country_features() + subdivisions
    add_shares(features)
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
