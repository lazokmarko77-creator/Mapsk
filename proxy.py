"""
MapSK – Proxy (ZBGIS WFS + Overpass)
Deploy: render.com → New Web Service
Build:  pip install -r requirements.txt
Start:  gunicorn proxy:app
"""
from flask import Flask, request, jsonify, Response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── ZBGIS WFS parcella ────────────────────────────
WFS_BASE = "https://kataster.skgeodesy.sk/eskn-portal/services/public/CP_WFS/MapServer/WFSServer"

@app.route("/api/parcel")
def parcel():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    if not lat or not lng:
        return jsonify({"error": "lat/lng required"}), 400
    d = 0.0003
    bbox = f"{float(lng)-d},{float(lat)-d},{float(lng)+d},{float(lat)+d}"
    url = (
        f"{WFS_BASE}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature"
        f"&TYPENAMES=CP_WFS:CadastralParcel"
        f"&BBOX={bbox},urn:ogc:def:crs:EPSG::4326"
        f"&outputFormat=application/json&count=1"
    )
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "MapSK/1.0"})
        return Response(r.content, mimetype="application/json")
    except Exception as e:
        return jsonify({"error": str(e)}), 502

# ── Overpass API (transport) ──────────────────────
OVERPASS = "https://overpass-api.de/api/interpreter"

@app.route("/api/overpass", methods=["POST"])
def overpass():
    query = request.get_data(as_text=True)
    if not query:
        return jsonify({"error": "empty query"}), 400
    try:
        r = requests.post(OVERPASS, data=query, timeout=50,
                          headers={"User-Agent": "MapSK/1.0",
                                   "Content-Type": "application/x-www-form-urlencoded"})
        return Response(r.content, mimetype="application/json")
    except Exception as e:
        return jsonify({"error": str(e)}), 502

# ── Health ────────────────────────────────────────
@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
