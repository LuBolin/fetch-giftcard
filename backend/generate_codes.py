import uuid
import random
import string
import csv
import os

UUID_LENGTH = 36  # Standard UUID string, 32 chars + 4 hyphens
GIFT_CODE_LENGTH = 16  # Common for gift cards
CSV_FILE = "gift_cards.csv"


def generate_gift_code(length=GIFT_CODE_LENGTH):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def load_existing_cards(filepath=CSV_FILE):
    """Load existing UUIDs and codes to prevent duplication"""
    existing_uuids = set()
    existing_gift_codes = set()

    if os.path.exists(filepath):
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_uuids.add(row['uuid'])
                existing_gift_codes.add(row['gift_code'])

    return existing_uuids, existing_gift_codes


def generate_gift_cards(count, output_file=CSV_FILE):
    existing_uuids, existing_codes = load_existing_cards(output_file)
    new_cards = []

    print(f"Found {len(existing_uuids)} existing UUIDs and {len(existing_codes)} gift codes")

    attempts = 0
    max_attempts = count * 10  # Prevent infinite loops

    while len(new_cards) < count and attempts < max_attempts:
        new_uuid = str(uuid.uuid4())
        new_code = generate_gift_code()

        if new_uuid not in existing_uuids and new_code not in existing_codes:
            new_cards.append({'uuid': new_uuid, 'gift_code': new_code})
            existing_uuids.add(new_uuid)
            existing_codes.add(new_code)

        attempts += 1

    if attempts >= max_attempts and len(new_cards) < count:
        print(f"⚠️ Warning: Only generated {len(new_cards)} unique cards after {max_attempts} attempts")

    if new_cards:
        file_exists = os.path.exists(output_file)
        with open(output_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['uuid', 'gift_code'])
            if not file_exists:
                writer.writeheader()
            writer.writerows(new_cards)

        print(f"✅ Generated and saved {len(new_cards)} gift cards to {output_file}")
    else:
        print("❌ No new gift cards were generated")


if __name__ == "__main__":
    generate_gift_cards(count=10)  # Modify count here
