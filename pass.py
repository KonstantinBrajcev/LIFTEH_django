from passlib.hash import pbkdf2_sha256

# 1. Введите ваш пароль (либо сгенерируйте случайный)
password = "000000"  # Замените на реальный пароль

# 2. Генерация хеша с автоматической солью
hash = pbkdf2_sha256.using(rounds=1000000).hash(password)

# 3. Вывод результата
print("Сгенерированный хеш:")
print('"', hash, '"')