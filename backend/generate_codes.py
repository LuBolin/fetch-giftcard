import random
import string

def generate_code(prefix="GFT", length=12):
    chars = string.ascii_uppercase + string.digits
    return f"{prefix}-" + ''.join(random.choices(chars, k=length))

def generate_codes(count=100):
    return list({generate_code() for _ in range(count)})


append = True
if __name__ == "__main__":
    codes = generate_codes(10)

    with open("codes.txt", "a" if append else "w") as f:
      for code in codes:
        f.write(code + "\n")

    f.close()
    
    print(f"✅ Generated {len(codes)} codes and saved to codes.txt")

