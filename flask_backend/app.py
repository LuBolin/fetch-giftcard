from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase_tool import SupabaseClient
from cleancloud_tool import myCleancloudClient

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

###
# To launch: flask run
###

# Enable CORS for all routes and origins
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        "supports_credentials": False
    }
})

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CLEANCLOUD_API_TOKEN = os.getenv("CLEANCLOUD_API_TOKEN")

# Initialize clients
supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
cleancloud = None

# Initialize CleanCloud client if API token is available
if CLEANCLOUD_API_TOKEN:
    try:
        cleancloud = myCleancloudClient(CLEANCLOUD_API_TOKEN, print_gift_card_source_accounts=False)
        print("✅ CleanCloud client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize CleanCloud client: {e}")
        cleancloud = None
else:
    print("⚠️ CleanCloud API token not found in environment variables")

@app.route("/")
def serve_html():
    return send_from_directory(app.static_folder, "redeem.html")

@app.route("/test-cors", methods=["GET", "POST", "OPTIONS"])
def test_cors():
    if request.method == "OPTIONS":
        return jsonify({"status": "CORS preflight OK"}), 200
    return jsonify({"message": "CORS test successful", "method": request.method})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'false')
    return response

@app.route("/redeem", methods=["POST", "OPTIONS"])
def redeem_endpoint():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200
    
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
        # Step 1: Redeem the code in Supabase
        print("🎫 Redeeming code in Supabase...")
        _ = supabase.redeem_code(code, recipient_email, recipient_phone, metadata=metadata)
        print("✅ Code redeemed successfully in Supabase")
        
        # Step 2: Purchase and send CleanCloud gift card
        if cleancloud:
            try:
                print("🎁 Purchasing CleanCloud gift card...")
                
                # Extract recipient name from email (before @) or use "Valued Customer"
                to_name = recipient_email.split('@')[0].title() if '@' in recipient_email else "Valued Customer"
                
                # Gift card parameters
                amount = float(os.getenv("GIFT_CARD_AMOUNT", "10.0"))  # Default $10
                
                # Send immediately
                today = datetime.now()
                send_date = today.strftime("%Y-%m-%d")
                send_hour = today.strftime("%H:%M")
                
                message = f"Congratulations! Your redemption code {code} has been processed. Enjoy your gift card!"
                
                print("=" * 60)
                print("🎁 CLEANCLOUD GIFT CARD PURCHASE DETAILS")
                print("=" * 60)
                print(f"📧 Recipient Name: {to_name}")
                print(f"📧 Recipient Email: {recipient_email}")
                print(f"📱 Recipient Phone: {recipient_phone}")
                print(f"💰 Gift Card Amount: ${amount}")
                print(f"📅 Send Date: {send_date}")
                print(f"🕒 Send Time: {send_hour}")
                print(f"💬 Message: {message}")
                print(f"📨 Notification Method: Email")
                print("=" * 60)
                
                # Attempt to purchase gift card
                cleancloud_response = cleancloud.gift_card_buy(
                    to_name=to_name,
                    to_email=recipient_email,
                    to_tel=recipient_phone,
                    amount=amount,
                    send_date=send_date,
                    send_hour=send_hour,
                    message=message,
                    notify_by=2  # Email notification
                )
                
                print("=" * 60)
                print("🎯 CLEANCLOUD API RESPONSE")
                print("=" * 60)
                print(f"Response Type: {type(cleancloud_response)}")
                print(f"Response Content: {cleancloud_response}")
                print("=" * 60)
                
                if "Success" in str(cleancloud_response):
                    print("🎉 SUCCESS! CleanCloud gift card purchased and sent successfully!")
                    print(f"✅ ${amount} gift card sent to {recipient_email}")
                    print("=" * 60)
                    return jsonify({
                        "success": True, 
                        "message": f"Code {code} redeemed successfully! A ${amount} gift card has been sent to your email."
                    })
                else:
                    print("❌ FAILED! CleanCloud gift card purchase failed")
                    print(f"⚠️ Code was redeemed but gift card could not be sent")
                    print(f"🔍 Failure reason: {cleancloud_response}")
                    print("=" * 60)
                    return jsonify({
                        "success": True, 
                        "message": f"Code {code} redeemed successfully! However, there was an issue sending your gift card. Please contact support."
                    })
                    
            except Exception as cleancloud_error:
                print("=" * 60)
                print("💥 CLEANCLOUD EXCEPTION OCCURRED")
                print("=" * 60)
                print(f"Exception Type: {type(cleancloud_error).__name__}")
                print(f"Exception Message: {str(cleancloud_error)}")
                print(f"⚠️ Code was redeemed but gift card purchase failed due to exception")
                print("=" * 60)
                return jsonify({
                    "success": True, 
                    "message": f"Code {code} redeemed successfully! However, there was an issue sending your gift card. Please contact support."
                })
        else:
            print("=" * 60)
            print("⚠️ CLEANCLOUD NOT AVAILABLE")
            print("=" * 60)
            print("🚫 CleanCloud client not initialized")
            print("💡 Check CLEANCLOUD_API_TOKEN in environment variables")
            print("✅ Code was redeemed but no gift card sent")
            print("=" * 60)
            return jsonify({"success": True, "message": f"Code {code} redeemed successfully!"})
            
    except Exception as e:
        print(f"❌ Error in redeem_endpoint: {type(e).__name__}: {str(e)}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets $PORT
    app.run(host="0.0.0.0", port=port)
