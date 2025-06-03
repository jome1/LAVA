import json
import os
import geopandas as gpd
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

# --- Configuration ---
INPUT_FP = "data/NeiMongol/NeiMongol_4326.geojson"  # Path to your GADM JSON
OUTPUT_FP = "NeiMongol_simplified_360.geojson"
COORDS_OUTPUT_FP = "NeiMongol_simplified_360_coords.geojson"
QUERY_OUTPUT_FP = "NeiMongol_overpass_query.txt"
TARGET_VERTICES = 360
TOL_MIN, TOL_MAX = 0.0, 0.5  # Search range for simplification tolerance



def prepare_geometry(geom):
    """Ensure geometry is a single Polygon suitable for simplification."""
    if isinstance(geom, MultiPolygon):
        merged = unary_union(geom)
        if isinstance(merged, Polygon):
            return merged
        else:
            return max(merged.geoms, key=lambda p: p.area)
    elif isinstance(geom, Polygon):
        return geom
    else:
        raise ValueError("Input must be a Polygon or MultiPolygon.")



def find_tolerance_for_vertices(geom, target_vertices, tol_min=0.0, tol_max=0.5, iterations=10):
    def vertex_count(poly):
        return len(poly.exterior.coords)
    best_tol = tol_min
    best_count = vertex_count(geom)
    low, high = tol_min, tol_max
    for _ in range(iterations):
        mid = (low + high) / 2
        simp = geom.simplify(mid, preserve_topology=True)
        count = vertex_count(simp)
        if count <= target_vertices:
            best_tol, best_count = mid, count
            high = mid
        else:
            low = mid
    return best_tol, best_count


def simplify(geom, tol, output_path= None, export_json=False):
    if export_json and output_path is None:
        raise ValueError("output_path must be provided if export_json is True")
    simplified = geom.simplify(tol, preserve_topology=True)
    if export_json:
        feature = {
            "type": "Feature",
            "geometry": mapping(simplified),
            "properties": {}
        }
        fc = {"type": "FeatureCollection", "features": [feature]}
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fc, f, ensure_ascii=False, indent=2)
    return simplified

def export_overpass_polygon(poly):
    polygon_coords = poly.exterior.coords
    poly_str = " ".join(f"{lat} {lon}" for lon, lat in polygon_coords)
    if not isinstance(poly_str, str):
        raise TypeError("Output must be of type string")
    return poly_str


def generate_overpass_polygon(region_gdf: gpd.GeoDataFrame, target_vertices=360, tol_min=0.0, tol_max=0.5) -> str:
    """Simplify a region and return an Overpass-compatible polygon string."""
    raw_geom = region_gdf.unary_union
    geom = prepare_geometry(raw_geom)
    tol, count = find_tolerance_for_vertices(geom, target_vertices, tol_min, tol_max)
    simplified_geom = simplify(geom, tol)
    print(f"Tolerance used: {tol:.6f}°, resulting vertices: {count}")
    return export_overpass_polygon(simplified_geom)
