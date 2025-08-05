import csv
import os
from supabase_tool import SupabaseClient
from dotenv import load_dotenv
from datetime import datetime, timezone

def read_gift_codes(filepath):
    """Read gift codes from a CSV file with headers"""
    codes = []
    if os.path.exists(filepath):
        with open(filepath, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'gift_code' in row and row['gift_code']:
                    codes.append(row['gift_code'])
    return codes



load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)

# upload codes from CSV
if __name__ == "__main__":
    codes = read_gift_codes("gift_cards.csv")
    print(f"Found {len(codes)} codes to upload")
    card_value = 5 # specify in dollars $
    if codes: supabase.upload_codes(codes, card_value=card_value)

    # set expiry of serial 1 to 5 to december 31, 2025
    # expiry_datetime = datetime(2024, 12, 31, tzinfo=timezone.utc)
    # supabase.update_expiry(1, 5, expiry_datetime)

    # issue to "Seven-Eleven"
    # distributed_to = "Seven-Eleven"
    # supabase.distribute_cards(1, 3, distributed_to)
