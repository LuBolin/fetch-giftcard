import os
from supabase_tool import SupabaseClient


def read_codes_from_file(filename="codes.txt"):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]
  
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

code_list = read_codes_from_file()
recent_codes = code_list[-10:]  # Get the last 10 codes
supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
supabase.upload_codes(recent_codes)