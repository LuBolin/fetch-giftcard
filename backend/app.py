from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from supabase_tool import SupabaseClient

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

CORS(app, origins=[
    "http://localhost:8080",       # If serving frontend via python -m http.server
    "http://127.0.0.1:8080",
    "http://localhost:5500",       # If using VSCode Live Server
    "null"                         # If opening redeem.html directly from file://
])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def serve_html():
    return send_from_directory(app.static_folder, "redeem.html")

@app.route("/redeem", methods=["POST"])
def redeem_endpoint():
    data = request.get_json()
    code = data.get("code")
    recipient = data.get("recipient")
    metadata = data.get("metadata", {})

    if not code or not recipient:
        return jsonify({"success": False, "message": "Missing code or recipient"}), 400

    try:
        _ = supabase.redeem_code(code, recipient, metadata=metadata)
        return jsonify({"success": True, "message": "Code redeemed successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {repr(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets $PORT
    app.run(host="0.0.0.0", port=port)
