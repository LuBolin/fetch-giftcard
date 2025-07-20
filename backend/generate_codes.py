import random
import string
import csv
import os

GIFT_CODE_LENGTH = 16  # Common for gift cards
CSV_FILE = "gift_cards.csv"


def generate_gift_code(length=GIFT_CODE_LENGTH):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def load_existing_codes(filepath=CSV_FILE):
    """Load existing gift codes to prevent duplication"""
    existing_codes = set()

    if os.path.exists(filepath):
        with open(filepath, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'gift_code' in row and row['gift_code']:
                    existing_codes.add(row['gift_code'])

    return existing_codes


def generate_gift_cards(count, output_file=CSV_FILE):
    existing_codes = load_existing_codes(output_file)
    new_codes = []

    print(f"Found {len(existing_codes)} existing gift codes")

    attempts = 0
    max_attempts = count * 10  # Prevent infinite loops

    while len(new_codes) < count and attempts < max_attempts:
        new_code = generate_gift_code()

        if new_code not in existing_codes:
            new_codes.append({'gift_code': new_code})
            existing_codes.add(new_code)

        attempts += 1

    if attempts >= max_attempts and len(new_codes) < count:
        print(f"⚠️ Warning: Only generated {len(new_codes)} unique codes after {max_attempts} attempts")

    if new_codes:
        # Check if file exists and has content
        file_exists = os.path.exists(output_file)
        write_header = not file_exists or os.path.getsize(output_file) == 0

        with open(output_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['gift_code'])
            
            if write_header:
                writer.writeheader()
            
            writer.writerows(new_codes)

        print(f"✅ Generated and saved {len(new_codes)} gift codes to {output_file}")
    else:
        print("❌ No new gift codes were generated")


if __name__ == "__main__":
    generate_gift_cards(count=10)  # Modify count here
