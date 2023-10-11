import os

USERNAME = os.environ.get("DB_USERNAME") or "default"


def get_username():
    return USERNAME
