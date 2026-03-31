#!/usr/bin/env python3
"""Create a demo user and place in the in-memory HBnB app."""

from __future__ import annotations

import json
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hbnb import create_app
from hbnb.demo_seed import seed_demo_data


def main():
    config = {}
    if os.environ.get("JWT_SECRET_KEY"):
        config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
    if os.environ.get("ENABLE_AUTH", "").strip().lower() in {"1", "true", "yes", "on"}:
        config["ENABLE_AUTH"] = True

    app = create_app(config)
    result = seed_demo_data(app)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()