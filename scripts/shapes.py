r"""Write the shapes of the map of the list, with DemandCast's code.

The map of the site colours each country and subdivision of the list by
its years of data. ``data/shapes.geojson`` holds their outlines, one
feature per line, each with the label of its entity: every country of
Natural Earth at 1:50m, under its code, and each subdivision of the
list, under its country code and subdivision code, as DemandCast draws
it, from Natural Earth or from the shapes of grid regions of DemandCast.
Grid regions without a shape in DemandCast are unions of regions of
Natural Earth, without the parts of some regions outside the grid,
which hand-drawn polygons mark. The outlines are simplified and rounded
to 0.01 degrees, enough for a map of the world.

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
# Subdivisions without a shape in DemandCast, as unions of regions of
# Natural Earth at 1:10m, by their ISO 3166-2 codes: the departments of
# Bolivia, which its layer at 1:50m does not have, the price areas of
# Denmark, the North and South Islands of New Zealand, without the
# Chatham and outlying islands, and the interconnected power systems of
# Russia, whose regions SO UES lists on the page of each system.
COMPOSITES = {
    "BOL-B": "BO-B",
    "BOL-C": "BO-C",
    "BOL-H": "BO-H",
    "BOL-L": "BO-L",
    "BOL-O": "BO-O",
    "BOL-P": "BO-P",
    "BOL-S": "BO-S",
    "BOL-T": "BO-T",
    "DNK-DK1": "DK-81 DK-82 DK-83",
    "DNK-DK2": "DK-84 DK-85",
    "NZL-NI": (
        "NZ-AUK NZ-BOP NZ-GIS NZ-HKB NZ-MWT NZ-NTL NZ-TKI NZ-WGN NZ-WKO"
    ),
    "NZL-SI": "NZ-CAN NZ-MBH NZ-NSN NZ-OTA NZ-STL NZ-TAS NZ-WTC",
    "RUS-CENTER": (
        "RU-BEL RU-BRY RU-IVA RU-KLU RU-KOS RU-KRS RU-LIP RU-MOS RU-MOW "
        "RU-ORL RU-RYA RU-SMO RU-TAM RU-TUL RU-TVE RU-VLA RU-VLG RU-VOR "
        "RU-YAR"
    ),
    "RUS-EAST": "RU-AMU RU-KHA RU-PRI RU-SA RU-YEV",
    "RUS-NORTHWEST": (
        "RU-ARK RU-KGD RU-KO RU-KR RU-LEN RU-MUR RU-NEN RU-NGR RU-PSK RU-SPE"
    ),
    "RUS-SIBERIA": (
        "RU-AL RU-ALT RU-BU RU-IRK RU-KEM RU-KK RU-KYA RU-NVS RU-OMS "
        "RU-TOM RU-TY RU-ZAB"
    ),
    "RUS-SOUTH": (
        "RU-AD RU-AST RU-CE RU-DA RU-IN RU-KB RU-KC RU-KDA RU-KL RU-ROS "
        "RU-SE RU-STA RU-VGG UA-40 UA-43"
    ),
    "RUS-URALS": (
        "RU-BA RU-CHE RU-KGN RU-KHM RU-KIR RU-ORE RU-PER RU-SVE RU-TYU "
        "RU-UD RU-YAN"
    ),
    "RUS-VOLGA": "RU-CU RU-ME RU-MO RU-NIZ RU-PNZ RU-SAM RU-SAR RU-TA RU-ULY",
}
# Parts of regions outside their grid region, as polygons of longitude
# and latitude in WKT, drawn along the borders of their districts: the
# 13 Arctic districts of Yakutia, outside the western, central and
# south Yakutian energy districts of the East, and Taimyr and Norilsk,
# an isolated power system in Krasnoyarsk Krai.
CUTS = {
    "RU-SA": (
        "POLYGON ((91.3 66.5, 106.3 66.5, 108 66.4, 108.8 66.8, "
        "109.5 66.1, 112.7 66.6, 113.5 65.9, 112.3 65.6, 112.8 65.5, "
        "112.6 65.1, 114.1 64.6, 117.2 65.3, 118.3 66.1, 118.1 66.4, "
        "119.2 66.7, 119 66.9, 120.3 66.5, 120.5 65.7, 121.2 65.3, "
        "123.4 64.7, 127 65.6, 127.6 66, 126.9 66.2, 127.3 66.6, "
        "128.5 66.7, 130 66.5, 130.1 66.2, 131.7 65.7, 131.5 65.5, "
        "132.4 64.6, 132.8 64.6, 133.2 65.3, 136.8 66.2, 144.2 65, "
        "146.4 64.2, 171.4 64.2, 171.4 82, 91.3 82, 91.3 66.5))"
    ),
    "RU-KYA": (
        "POLYGON ((67.7 68.4, 82.7 68.4, 84.8 67.2, 85.7 68, 86.4 68.1, "
        "87.5 67.3, 90.6 67.4, 93 68.4, 94.2 68.4, 95.4 69.3, 98 69.8, "
        "99.7 69.9, 103.8 69.3, 106.4 69.5, 131.4 69.5, 131.4 82, "
        "67.7 82, 67.7 68.4))"
    ),
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


def composite(regions: Any, codes: list[str]) -> Any:
    """Return the regions of a grid region, without their cut parts.

    Parameters
    ----------
    regions : geopandas.GeoDataFrame
        The regions of Natural Earth.
    codes : list of str
        The ISO 3166-2 codes of the regions of the grid region.

    Returns
    -------
    geopandas.GeoDataFrame
        The regions, each without the polygon of ``CUTS`` it has.
    """
    shape = regions[regions["iso_3166_2"].isin(codes)].copy()
    for code, cut in CUTS.items():
        rows = shape["iso_3166_2"] == code
        shape.loc[rows, "geometry"] = shape.loc[rows, "geometry"].difference(
            shapely.from_wkt(cut)
        )
    return shape


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
                shape = composite(regions, COMPOSITES[label].split())
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
