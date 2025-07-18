from datetime import datetime
import supabase
from datetime import datetime, timedelta

# columns: code, uuid, created_at, is_redeemed, redeemed_at, recipient_email, recipient_phone, metadata

class SupabaseClient(supabase.Client):

    def __init__(self, url, key, expiry_months):
        super().__init__(url, key)
        self.expiry_months = expiry_months

    def upload_codes(self, uuid_codes, metadata = None):
        # codes are uuid - giftcode pairs
        for uuid, code in uuid_codes:
            data = {
                "code": code,
                "uuid": uuid,
                "metadata": metadata 
            }

            try:
                _ = self.table("gift_codes").insert(data).execute()
                print(f"✅ Inserted {code}")
            except Exception as e:
                error_message = e.message
                print(f"❌ Error inserting {code}: {error_message}")

    def redeem_code(self, code, recipient_email, recipient_phone, metadata=None):
        check_res = self.table("gift_codes").select("*").eq("code", code).execute()
        rows = check_res.data

        if not rows:
            raise ValueError(f"Code '{code}' not found in database.")

        row = rows[0]
        if row.get("is_redeemed"):
            raise ValueError(f"Code '{code}' has already been redeemed.")
        
        created_at = row.get("created_at")
        # Parse the created_at datetime and make comparison timezone-aware
        created_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        expiry_date = created_datetime + timedelta(days=self.expiry_months * 30)
        current_time = datetime.now(expiry_date.tzinfo)  # Use same timezone as expiry_date
        
        if current_time > expiry_date:
            raise ValueError(f"Code '{code}' has expired on {expiry_date.isoformat()}.")
    
        data = {
            "is_redeemed": True,
            "redeemed_at": datetime.now().isoformat(),
            "recipient_email": recipient_email,
            "recipient_phone": recipient_phone,
            "metadata": metadata
        }
        
        try:
            response = self.table("gift_codes").update(data)\
                .eq("code", code).eq("is_redeemed", False).execute()
            # response: postgrest.base_request_builder.APIResponse[TypeVar]
            # response.data: list of dicts
            # response.data[0]: dict with the updated row
            data = response.data
            if not data:
                raise ValueError(f"Code {code} not found or already redeemed.")
            updated_row = data[0]
            print(f"✅ Redeemed {code} for email {recipient_email}")
            print(f"Updated row: {updated_row}")
        except Exception as e:
            raise e
    
    # For testing only
    def reset_code(self, code):
        try:
            response = self.table("gift_codes").update({
                "is_redeemed": False,
                "recipient_email": None,
                "recipient_phone": None,
                "redeemed_at": None
            }).eq("code", code).execute()
            if response.data:
                print(f"✅ Reset {code} successfully.")
            else:
                print(f"❌ Code {code} not found or not redeemed.")
        except Exception as e:
            error_message = e.message if hasattr(e, 'message') else str(e)
            print(f"❌ Error resetting {code}: {error_message}")


# Load secrets
from dotenv import load_dotenv
import os
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# simulate redeem
if __name__ == "__main__":
    client = SupabaseClient(SUPABASE_URL, SUPABASE_KEY, 12)
    # Example usage
    try:
        client.redeem_code("B2DC5BH0LIRW0LY8", "andy518420@gmail.com", "85330618")
    except Exception as e:
        print(f"Error: {e}")