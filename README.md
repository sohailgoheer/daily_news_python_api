# Beginner Shapefile Uploader (Flask + GeoPandas + MapLibre)

This project is a **simple full-stack app** that lets you:

1. Upload a `.zip` file containing an ESRI Shapefile (`.shp`, `.shx`, `.dbf`, etc.).
2. Read and convert that shapefile to GeoJSON using **GeoPandas** on the backend.
3. Draw the uploaded features on a **MapLibre GL JS** map in the browser.

## Features

- Flask backend with one upload API endpoint
- Safe zip extraction (blocks unsafe paths)
- Validation for required shapefile parts (`.shp`, `.shx`, `.dbf`)
- Error handling for:
  - invalid zip
  - missing shapefile parts
  - unsupported geometry types
- Simple beginner-friendly frontend (file input, button, map)
- Map auto-zooms to uploaded layer bounds

---

## Exact run steps

### 1) Create and activate a virtual environment

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the Flask app

```bash
python main.py
```

### 4) Open the app in your browser

Visit:

```text
http://127.0.0.1:5000
```

### 5) Upload your zipped shapefile

- Click file input and select a `.zip`
- Click **Upload**
- The layer will appear on the map and zoom to its bounds

---

## Expected zip contents

Your zip should include matching files with the same base name, for example:

- `roads.shp`
- `roads.shx`
- `roads.dbf`
- optional: `roads.prj`, `roads.cpg`, etc.

You can also have nested folders in the zip; the app searches for a valid shapefile.

---

## Project structure

```text
.
├── main.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── styles.css
```

