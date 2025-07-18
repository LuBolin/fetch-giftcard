from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from supabase_tool import SupabaseClient

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

CORS(app, origins=[
    "https://fetch-giftcard.onrender.com",  # Production domain
    "http://localhost:8080",       # If serving frontend via python -m http.server
    "http://127.0.0.1:8080",
    "http://localhost:5500",       # If using VSCode Live Server
    "null"                         # If opening redeem.html directly from file://
])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EXPIRY_MONTHS = int(os.getenv("EXPIRY_MONTHS", 12))

supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY, EXPIRY_MONTHS)


@app.route("/")
def serve_html():
    return send_from_directory(app.static_folder, "redeem.html")

@app.route("/redeem", methods=["POST"])
def redeem_endpoint():
    data = request.get_json()
    print(f"Received data: {data}")
    
    code = data.get("code")
    recipient_email = data.get("recipient_email")
    recipient_phone = data.get("recipient_phone")
    metadata = data.get("metadata", {})

    print(f"Parsed - code: {code}, email: {recipient_email}, phone: {recipient_phone}")

    if not code or not recipient_email or not recipient_phone:
        return jsonify({"success": False, "message": "Missing code or recipient information"}), 400

    try:
        _ = supabase.redeem_code(code, recipient_email, recipient_phone, metadata=metadata)
        return jsonify({"success": True, "message": "Code redeemed successfully!"})
    except Exception as e:
        print(f"Error in redeem_endpoint: {type(e).__name__}: {str(e)}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets $PORT
    app.run(host="0.0.0.0", port=port)
