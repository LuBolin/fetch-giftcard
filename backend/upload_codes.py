import csv
import os
from supabase_tool import SupabaseClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)

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

if __name__ == "__main__":
    codes = read_gift_codes("gift_cards.csv")
    print(f"Found {len(codes)} codes to upload")
    
    if codes:
        supabase.upload_codes(codes)
    else:
        print("No codes found in gift_cards.csv")