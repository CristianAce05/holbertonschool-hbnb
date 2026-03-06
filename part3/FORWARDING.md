Opening the HBnB dev server in your browser
==========================================

The dev server is running inside the workspace and listens on port 5001 (for example).
You can open it from your browser using one of these methods depending on your environment.

Try the direct URL first (works from inside the workspace or when port is forwarded):

  http://127.0.0.1:5001/health

If that shows a 403 in your browser, your IDE or remote environment is blocking loopback access. Use one of the options below:

- VS Code (Remote / Dev Containers / Codespaces):
  1. Open the Command Palette (Ctrl/Cmd+Shift+P) → "Forward a Port" or open the "Ports" view.
  2. Enter `5001` and forward it to a local port (usually `5001`).
  3. Click the forwarded entry and choose "Open in Browser" or open the provided forwarded URL.

- GitHub Codespaces: open the "Ports" panel in the Codespace UI, forward port `5001`, then click the public or preview URL shown.

- Gitpod: use the "Preview" → "Open Browser" or the Ports view to expose port `5001` and open the provided URL.

- SSH tunnel (from your local machine to the remote host):

```bash
# on your local machine, forward remote container's port 5001 to local
ssh -L 5001:127.0.0.1:5001 user@remote-host
# then open in your local browser:
http://127.0.0.1:5001/health
```

- If your IDE provides an automatically generated preview URL, open that URL instead of `127.0.0.1`.

Quick checks (inside the workspace terminal)

```bash
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5001/api/v1/users
```

If you want, I can also:
- Add a one-line file `FORWARDED_URL.txt` containing the likely URLs to open.
- Add `--host`/`--port` examples to `README.md` or update the launcher to write a small JSON file (`/tmp/hbnb_forward.json`) with the detected container IPs and port for IDEs to read.

Tell me which option you prefer and I'll add it.
