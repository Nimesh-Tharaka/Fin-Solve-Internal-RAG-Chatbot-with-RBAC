USERS = {
    "fiona": {"password": "finance123", "role": "finance"},
    "mark": {"password": "marketing123", "role": "marketing"},
    "harry": {"password": "hr123", "role": "hr"},
    "eng1": {"password": "eng123", "role": "engineering"},
    "ceo": {"password": "ceo123", "role": "c_level"},
    "emp1": {"password": "emp123", "role": "employee"},
}


def authenticate_user(username: str, password: str):
    user = USERS.get(username)
    if user and user["password"] == password:
        return {"username": username, "role": user["role"]}
    return None