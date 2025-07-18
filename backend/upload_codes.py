import csv
import os
from supabase_tool import SupabaseClient



SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EXPIRY_MONTHS = int(os.getenv("EXPIRY_MONTHS", 12))

supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY, EXPIRY_MONTHS)

def read_uuid_giftcards(filepath):
    """Read UUID and gift code pairs from a CSV file"""
    uuid_codes = []
    if os.path.exists(filepath):
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                uuid_codes.append((row['uuid'], row['gift_code']))
    return uuid_codes

supabase.upload_codes(read_uuid_giftcards("gift_cards.csv"))