"""Run script for the HBNB API."""

import os

from hbnb import create_app
from hbnb.demo_seed import seed_demo_data


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _build_app_config() -> dict:
    config: dict = {}

    if _env_flag("ENABLE_AUTH"):
        config["ENABLE_AUTH"] = True

    if os.environ.get("JWT_SECRET_KEY"):
        config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]

    if os.environ.get("CORS_ALLOW_ORIGIN"):
        config["CORS_ALLOW_ORIGIN"] = os.environ["CORS_ALLOW_ORIGIN"]

    return config


def _should_seed_demo_data() -> bool:
    raw = os.environ.get("SEED_DEMO_DATA")
    if raw is None:
        return True
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def main():
    app = create_app(_build_app_config())
    if _should_seed_demo_data():
        result = seed_demo_data(app)
        place = result.get("place") or {}
        credentials = result.get("credentials") or {}
        print(
            "Demo data ready: "
            f"{credentials.get('email')} / {credentials.get('password')} "
            f"(place id: {place.get('id', 'n/a')})"
        )
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
