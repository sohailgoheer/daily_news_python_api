import json
import tempfile
import zipfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request
import geopandas as gpd

app = Flask(__name__)

# We only allow common geometry types that MapLibre can draw directly.
SUPPORTED_GEOMETRIES = {
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
}


def _safe_extract_zip(zip_path: Path, extract_to: Path) -> None:
    """Extract a zip file while blocking path traversal attacks."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = extract_to / member.filename
            # Resolve the final path and confirm it stays inside extract_to.
            if not str(member_path.resolve()).startswith(str(extract_to.resolve())):
                raise ValueError("Zip contains unsafe file paths.")
        zf.extractall(extract_to)


def _find_shapefile(extract_to: Path) -> Path:
    """Find a .shp file and verify the matching .shx and .dbf exist."""
    shp_files = sorted(extract_to.rglob("*.shp"))
    if not shp_files:
        raise FileNotFoundError("No .shp file found in the uploaded zip.")

    for shp_file in shp_files:
        stem = shp_file.with_suffix("")
        shx_file = stem.with_suffix(".shx")
        dbf_file = stem.with_suffix(".dbf")
        if shx_file.exists() and dbf_file.exists():
            return shp_file

    raise FileNotFoundError(
        "Missing required shapefile parts. Make sure .shp, .shx, and .dbf are included."
    )


@app.route("/")
def index():
    """Serve the simple upload + map page."""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_shapefile():
    """Receive a zipped shapefile, convert it to GeoJSON, and return it."""
    uploaded_file = request.files.get("file")

    if not uploaded_file or uploaded_file.filename == "":
        return jsonify({"error": "Please choose a zip file to upload."}), 400

    if not uploaded_file.filename.lower().endswith(".zip"):
        return jsonify({"error": "Only .zip files are supported."}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "upload.zip"
        extract_to = temp_path / "extracted"
        extract_to.mkdir(parents=True, exist_ok=True)

        # Save uploaded file to a temporary location.
        uploaded_file.save(zip_path)

        try:
            _safe_extract_zip(zip_path, extract_to)
            shp_path = _find_shapefile(extract_to)

            # Read the shapefile with GeoPandas.
            gdf = gpd.read_file(shp_path)

            if gdf.empty:
                return jsonify({"error": "Shapefile has no features."}), 400

            # Remove rows with empty/null geometry so conversion is cleaner.
            gdf = gdf[gdf.geometry.notnull()]
            gdf = gdf[~gdf.geometry.is_empty]
            if gdf.empty:
                return jsonify({"error": "No valid geometry found in shapefile."}), 400

            # Validate geometry types for beginner-friendly behavior.
            geometry_types = set(gdf.geometry.geom_type.unique())
            unsupported = sorted(geometry_types - SUPPORTED_GEOMETRIES)
            if unsupported:
                return (
                    jsonify(
                        {
                            "error": "Unsupported geometry type(s): "
                            + ", ".join(unsupported)
                        }
                    ),
                    400,
                )

            # Reproject to WGS84 (EPSG:4326), expected by web maps.
            if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            # Convert to plain GeoJSON dictionary.
            geojson = json.loads(gdf.to_json())

            minx, miny, maxx, maxy = gdf.total_bounds.tolist()
            return jsonify({"geojson": geojson, "bounds": [minx, miny, maxx, maxy]})

        except zipfile.BadZipFile:
            return jsonify({"error": "Invalid zip file. Please upload a valid .zip."}), 400
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 400
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            # Generic fallback for unexpected errors.
            return jsonify({"error": f"Could not process shapefile: {exc}"}), 500


if __name__ == "__main__":
    # debug=True is helpful for local beginner development.
    app.run(debug=True)
