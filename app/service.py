import re
from typing import Optional


def check_password(password) -> Optional[str]:
    """Валидация пароля с возвратом конкретной ошибки"""

    if len(password) < 8:
        return "Длина пароля должна быть не менее 8 символов."

    if not re.search(r"\d", password):
        return "Пароль должен содержать хотя бы одну цифру."

    if not re.search(r"[a-z]", password):
        return "Пароль должен содержать хотя бы один символ нижнего регистра."

    if not re.search(r"[A-Z]", password):
        return "Пароль должен содержать хотя бы один символ верхнего регистра."

    if not re.search(r"[!@#$%^&*()-_=+{};:,<.>]", password):
        return "Пароль должен содержать хотя бы один специальный символ из набора: !@#$%^&*()-_=+{};:,<.>."

    return None
