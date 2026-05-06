from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from capture import capture_with_request
from extract import extract_features
from fingerprint import generate_fingerprint
import time

app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend",
    static_url_path="",
)
CORS(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url.startswith(("http://", "https://")):
        return jsonify({"Error": "Must start with URL http:// or https://"}), 400

    try:
        # Packets capture karo (10 seconds)
        packets, target_ip = capture_with_request(url, duration=10)

        # Features nikalo
        features = extract_features(packets)

        # Fingerprint banao
        fingerprint = generate_fingerprint(url, features)

        return jsonify(fingerprint)
    
    except ValueError as e:
        # Yeh wala block specifically domain missing ke liye chalega
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compare", methods=["POST"])
def compare():
    data = request.get_json()
    url1 = data.get("url1", "").strip()
    url2 = data.get("url2", "").strip()

    if not url1 or not url2:
        return jsonify({"error": "Dono URLs lazmi hain"}), 400

    # --- Site 1 Capture ---
    # Pehle site 1 ko capture karte hain
    p1, _ = capture_with_request(url1, duration=10)
    site1_res = generate_fingerprint(url1, extract_features(p1))

    # Chota sa break taake network socket release ho jaye
    time.sleep(1)

    # --- Site 2 Capture ---
    # Phir site 2 ko capture karte hain
    p2, _ = capture_with_request(url2, duration=10)
    site2_res = generate_fingerprint(url2, extract_features(p2))

    # --- Difference Calculation ---
    # Results ko compare karke diff object banate hain
    diff = {
        "more_bytes": url1
        if site1_res["total_bytes"] > site2_res["total_bytes"]
        else url2,
        "more_unique_ips": url1
        if len(site1_res["unique_ips"]) > len(site2_res["unique_ips"])
        else url2,
        "larger_packets": url1
        if site1_res["mean_packet_size"] > site2_res["mean_packet_size"]
        else url2,
    }

    # Final JSON response
    return jsonify({"site1": site1_res, "site2": site2_res, "diff": diff})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
