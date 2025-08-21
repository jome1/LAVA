#!/usr/bin/env python3
"""Simplified aggregation of LAVA available land results.

This script searches for all raster files matching ``*_available_land_*.tif``
inside ``data/**/available_land/``. The technology and scenario are parsed
from the file name and rasters belonging to the same technology and scenario
are reprojected to ``EPSG:4326`` and merged into a single raster. This
combined raster is then converted to vector polygons. The polygons are
written as layers to a GeoPackage (``aggregated_available_land.gpkg`` by
default).

Usage::

    python simple_results_analysis.py [--root PATH] [--output FILE]

By default ``--root`` is the directory containing this script, i.e. the
repository root. ``--output`` sets the resulting GeoPackage path.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.crs import CRS
from rasterio.features import shapes
from rasterio.merge import merge
from rasterio.vrt import WarpedVRT
from shapely.geometry import shape
from shapely.ops import unary_union


_PATTERN = re.compile(r"(.+)_([A-Za-z0-9]+)_([A-Za-z0-9]+)_available_land_.*\.tif$")


def _parse_info(path: Path):
    match = _PATTERN.match(path.name)
    if not match:
        return None
    region, tech, scenario = match.groups()
    return region, tech, scenario



TARGET_CRS = CRS.from_epsg(4326)


def _merge_rasters(paths: list[Path]):
    """Reproject rasters to EPSG:4326, merge and return data, transform, nodata and crs."""
    srcs = [rasterio.open(p) for p in paths]
    vrts = [WarpedVRT(src, crs=TARGET_CRS) for src in srcs]
    try:
        mosaic, out_trans = merge(vrts)
        nodata = vrts[0].nodata
    finally:
        for vrt in vrts:
            vrt.close()
        for src in srcs:
            src.close()
    return mosaic[0], out_trans, nodata, TARGET_CRS


def _array_to_gdf(data, transform, nodata, crs) -> gpd.GeoDataFrame:
    mask = data != nodata
    geoms = [shape(geom) for geom, val in shapes(data, mask=mask, transform=transform) if val != nodata]
    return gpd.GeoDataFrame({"geometry": geoms}, crs=crs)


def aggregate_available_land(root: Path, output: Path) -> None:
    files = list(root.glob("data/**/available_land/*_available_land_*.tif"))
    groups: dict[tuple[str, str], list[Path]] = {}
    for f in files:
        info = _parse_info(f)
        if not info:
            continue
        _, tech, scen = info
        groups.setdefault((tech, scen), []).append(f)

    if not groups:
        print("No available land rasters found.")
        return

    for (tech, scen), paths in groups.items():
        data, transform, nodata, crs = _merge_rasters(paths)
        gdf = _array_to_gdf(data, transform, nodata, crs)
        merged_geom = unary_union(gdf.geometry)
        gdf = gpd.GeoDataFrame(
            {"technology": [tech], "scenario": [scen], "geometry": [merged_geom]},
            crs=crs,
        )
        layer = f"{tech}_{scen}"
        gdf.to_file(output, layer=layer, driver="GPKG")
        print(f"Written layer {layer} with {len(paths)} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate available land rasters")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Project root containing data directory",
    )
    parser.add_argument("--output", type=Path, default=Path("aggregated_available_land.gpkg"), help="Output GeoPackage path")
    args = parser.parse_args()
    aggregate_available_land(args.root, args.output)
