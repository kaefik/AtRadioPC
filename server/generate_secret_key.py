import secrets
key = secrets.token_hex(32)  # Генерирует 32-байтный случайный ключ в hex формате

print(f"{key=}")