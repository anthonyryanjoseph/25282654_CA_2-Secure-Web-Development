import re

def validate_password(password):
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if len(password) > 64:
        return False, "Password must not be more than 64 characters."

    return True, ""

def validate_username(username):
    if len(username) < 3:
        return False, "Username must contain at least 3 characters."
    
    if len(username) > 30:
        return False, "Username must not exceed 30 characters."
    
    if not re.fullmatch(r"[A-Za-z0-9_]+", username):
        return False, "Username can only contain letters, numbers, and underscores."

    return True, ""