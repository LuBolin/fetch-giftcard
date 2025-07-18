from datetime import datetime
import os
import supabase
from dotenv import load_dotenv

# Load secrets
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class SupabaseClient(supabase.Client):

    def upload_codes(self, codes, metadata = None):
        for code in codes:
            data = {
                "code": code,
                "is_redeemed": False,
                "metadata": metadata 
            }

            try:
                _ = self.table("gift_codes").insert(data).execute()
                print(f"✅ Inserted {code}")
            except Exception as e:
                error_message = e.message
                print(f"❌ Error inserting {code}: {error_message}")

    def redeem_code(self, code, recipient, metadata=None):
        check_res = self.table("gift_codes").select("*").eq("code", code).execute()
        rows = check_res.data

        if not rows:
            raise ValueError(f"Code '{code}' not found in database.")

        row = rows[0]
        if row.get("is_redeemed"):
            raise ValueError(f"Code '{code}' has already been redeemed.")
        
        data = {
            "recipient": recipient,
            "is_redeemed": True,
            "redeemed_at": datetime.now().isoformat(),
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
            print(f"✅ Redeemed {code} for user {recipient}")
            print(f"Updated row: {updated_row}")
        except Exception as e:
            raise e
    
    # For testing only
    def reset_code(self, code):
        try:
            response = self.table("gift_codes").update({
                "is_redeemed": False,
                "recipient": None,
                "redeemed_at": None
            }).eq("code", code).execute()
            if response.data:
                print(f"✅ Reset {code} successfully.")
            else:
                print(f"❌ Code {code} not found or not redeemed.")
        except Exception as e:
            error_message = e.message if hasattr(e, 'message') else str(e)
            print(f"❌ Error resetting {code}: {error_message}")


def read_codes_from_file(filename="codes.txt"):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

# if __name__ == "__main__":
#     # codes = read_codes_from_file()
#     sb_client = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
#     # sb_client.upload_codes(codes)
#     code = "GFT-1TO7IA4Q2J8I"  # Example code
#     sb_client.reset_code(code)
#     sb_client.redeem_code("GFT-1TO7IA4Q2J8I", "user@example.com", metadata={"source": "test"})