"""
MapSK – ZBGIS WFS Proxy
Deploy ingyen: render.com → New Web Service → connect GitHub repo
Requirements: flask, requests, flask-cors
"""
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # engedélyezi a böngészőből jövő kéréseket

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
        r = requests.get(url, timeout=8)
        return app.response_class(r.content, mimetype="application/json")
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
