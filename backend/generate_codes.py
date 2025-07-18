import random
import string
import os


def generate_code(prefix="GFT", length=12):
    chars = string.ascii_uppercase + string.digits
    return f"{prefix}-" + ''.join(random.choices(chars, k=length))

def load_existing_codes():
    """Load existing codes from codes.txt to avoid duplicates"""
    if not os.path.exists("codes.txt"):
        return set()
    
    with open("codes.txt", "r") as f:
        return set(line.strip() for line in f if line.strip())

def generate_codes(count):
    """Generate unique codes that don't already exist in codes.txt"""
    existing_codes = load_existing_codes()
    new_codes = set()
    
    print(f"Found {len(existing_codes)} existing codes")
    
    # Generate codes until we have enough unique ones
    attempts = 0
    max_attempts = count * 10  # Prevent infinite loop
    
    while len(new_codes) < count and attempts < max_attempts:
        code = generate_code()
        if code not in existing_codes and code not in new_codes:
            new_codes.add(code)
        attempts += 1
    
    if attempts >= max_attempts:
        print(f"⚠️ Warning: Only generated {len(new_codes)} unique codes after {max_attempts} attempts")
    
    return list(new_codes)

        
append = True
if __name__ == "__main__":
    # Generate X many new codes
    codes = generate_codes(10)

    if codes:
        with open("codes.txt", "a" if append else "w") as f:
            for code in codes:
                f.write(code + "\n")

        print(f"✅ Generated {len(codes)} new unique codes and saved to codes.txt")
    else:
        print("❌ No new codes were generated")