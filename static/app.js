// Build a basic MapLibre map with an OpenStreetMap basemap.
const map = new maplibregl.Map({
  container: "map",
  style: {
    version: 8,
    sources: {
      osm: {
        type: "raster",
        tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
        tileSize: 256,
        attribution: "© OpenStreetMap contributors",
      },
    },
    layers: [
      {
        id: "osm",
        type: "raster",
        source: "osm",
      },
    ],
  },
  center: [-98, 39],
  zoom: 3,
});

const fileInput = document.getElementById("shapefileInput");
const uploadButton = document.getElementById("uploadButton");
const statusText = document.getElementById("status");

function setStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.style.color = isError ? "#dc2626" : "#065f46";
}

function addGeoJsonToMap(geojson, bounds) {
  // If user uploads again, remove old layers/sources first.
  ["uploaded-points", "uploaded-lines", "uploaded-polygons"].forEach((layerId) => {
    if (map.getLayer(layerId)) {
      map.removeLayer(layerId);
    }
  });
  if (map.getSource("uploaded-data")) {
    map.removeSource("uploaded-data");
  }

  // Add new uploaded data source.
  map.addSource("uploaded-data", {
    type: "geojson",
    data: geojson,
  });

  // Draw polygons.
  map.addLayer({
    id: "uploaded-polygons",
    type: "fill",
    source: "uploaded-data",
    paint: {
      "fill-color": "#0ea5e9",
      "fill-opacity": 0.4,
      "fill-outline-color": "#0369a1",
    },
    filter: [
      "any",
      ["==", ["geometry-type"], "Polygon"],
      ["==", ["geometry-type"], "MultiPolygon"],
    ],
  });

  // Draw lines.
  map.addLayer({
    id: "uploaded-lines",
    type: "line",
    source: "uploaded-data",
    paint: {
      "line-color": "#0369a1",
      "line-width": 2,
    },
    filter: [
      "any",
      ["==", ["geometry-type"], "LineString"],
      ["==", ["geometry-type"], "MultiLineString"],
    ],
  });

  // Draw points.
  map.addLayer({
    id: "uploaded-points",
    type: "circle",
    source: "uploaded-data",
    paint: {
      "circle-radius": 5,
      "circle-color": "#1d4ed8",
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": 1,
    },
    filter: [
      "any",
      ["==", ["geometry-type"], "Point"],
      ["==", ["geometry-type"], "MultiPoint"],
    ],
  });

  // Zoom the map to the uploaded layer's bounds.
  map.fitBounds(
    [
      [bounds[0], bounds[1]],
      [bounds[2], bounds[3]],
    ],
    { padding: 30, duration: 600 }
  );
}

uploadButton.addEventListener("click", async () => {
  const selectedFile = fileInput.files[0];
  if (!selectedFile) {
    setStatus("Please choose a zip file first.", true);
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);

  setStatus("Uploading and processing...");

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      setStatus(data.error || "Upload failed.", true);
      return;
    }

    // Wait until map style is ready before adding layers.
    if (!map.isStyleLoaded()) {
      await new Promise((resolve) => map.once("load", resolve));
    }

    addGeoJsonToMap(data.geojson, data.bounds);
    setStatus("Upload successful. Layer added to map.");
  } catch (error) {
    setStatus(`Error: ${error.message}`, true);
  }
});
