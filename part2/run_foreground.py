#!/usr/bin/env python3
"""Launcher that prints container IP and suggested forwarded URL, then runs the app.

Use this when you need a visible container IP or a hint for IDE port forwarding.
"""
import socket
import sys
import argparse
from hbnb import create_app


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


def main():
    parser = argparse.ArgumentParser(description="Run HBnB dev server with helpful launcher messages")
    parser.add_argument("--port", "-p", type=int, default=5000, help="Port to bind the server to")
    args = parser.parse_args()
    app = create_app()
    port = args.port
    ips = _get_container_ips()
    print("Starting HBnB dev server")
    print("Bind: 0.0.0.0:%d" % port)
    print("Container IPs detected:")
    for ip in ips:
        print(" - %s:%d" % (ip, port))

    print("")
    print(f"If you're using an IDE (VS Code, Codespaces, Gitpod), forward container port {port} to your browser.")
    print("Examples:")
    print(" - curl from inside container:")
    print(f"    curl http://127.0.0.1:{port}/health")
    print(" - If port-forwarded by your IDE, open the forwarded URL the IDE shows in your browser.")
    print("")
    sys.stdout.flush()

    # Run the Flask app on all interfaces so forwarded ports work
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
