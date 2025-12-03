from utils.auth import hash_password

passwords = {
    "admin123": "Admin password",
    "faculty2025": "Faculty password",
    "student2025": "Student password"
}

print("\n=== Generated Password Hashes ===\n")

for password, description in passwords.items():
    hashed = hash_password(password)
    print(f"{description}: {password}")
    print(f"Hash: {hashed}")
    print()