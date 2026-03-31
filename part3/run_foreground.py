#!/usr/bin/env python3
"""Launcher that prints container IP and suggested forwarded URL, then runs the app.

Use this when you need a visible container IP or a hint for IDE port forwarding.
"""

import socket
import sys
import argparse
import os
from hbnb import create_app
from hbnb.demo_seed import seed_demo_data


def _get_container_ips():
    ips = set()
    try:
        # hostname-based addresses
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            ips.add(ip)
    except Exception:
        pass
    try:
        # getaddrinfo fallback for common families
        for res in socket.getaddrinfo(socket.gethostname(), None):
            ips.add(res[4][0])
    except Exception:
        pass
    # always include loopback
    ips.add("127.0.0.1")
    return sorted(list(ips))


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
    parser = argparse.ArgumentParser(
        description="Run HBnB dev server with helpful launcher messages"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=5000, help="Port to bind the server to"
    )
    args = parser.parse_args()
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
    port = args.port
    ips = _get_container_ips()
    print("Starting HBnB dev server")
    print("Bind: 0.0.0.0:%d" % port)
    print("Container IPs detected:")
    for ip in ips:
        print(" - %s:%d" % (ip, port))

    print("")
    print(
        f"If you're using an IDE (VS Code, Codespaces, Gitpod), forward container port {port} to your browser."
    )
    print("Examples:")
    print(" - curl from inside container:")
    print(f"    curl http://127.0.0.1:{port}/health")
    print(
        " - If port-forwarded by your IDE, open the forwarded URL the IDE shows in your browser."
    )
    print("")
    sys.stdout.flush()

    # Run the Flask app on all interfaces so forwarded ports work
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
