Accessing the HBnB development server
====================================

The HBnB dev server listens on `0.0.0.0:5000`. Some web IDEs block direct access to `http://127.0.0.1:5000`.
If you see a "403 Access to 127.0.0.1 was denied" in your browser, use one of the options below.

Run the launcher in the workspace (prints container IPs and starts the app):

```bash
python3 run_foreground.py
```

From inside the container or workspace terminal (no forwarding needed):

```bash
curl http://127.0.0.1:5000/health
```

Use your IDE's port-forwarding / preview feature to forward container port 5000 to your host, then open the forwarded URL the IDE shows in the browser.

SSH local port-forwarding example (host forwards remote container port to your local machine):

```bash
# forward remote:5000 to local:5000
ssh -L 5000:127.0.0.1:5000 user@remote-host
# then open http://127.0.0.1:5000 on your local browser
```

If you want, I can also add an explicit message to `run.py` itself, or create a systemd-style unit or supervisor config for production deployment.
