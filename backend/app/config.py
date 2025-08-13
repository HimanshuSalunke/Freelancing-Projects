import os


def auth_disabled() -> bool:
    return os.getenv("DISABLE_AUTH", "false").strip().lower() in {"1", "true", "yes"}


def org_name() -> str:
    return os.getenv("ORG_NAME", "Reliance Jio Infotech Solutions")


