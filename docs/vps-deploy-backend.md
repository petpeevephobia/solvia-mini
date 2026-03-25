# VPS: FastAPI lead-audit API (systemd + Caddy)

The static site stays on Caddy at `/opt/solvia/landing`. The API listens on **127.0.0.1:8000**; Caddy proxies **`/api/*`** to Uvicorn.

## Prerequisites

- Python 3.11+ on the server (`python3 --version`).
- `backend/.env` on the server with `DATABASE_URL` (Supabase Postgres URI, include `?sslmode=require` if required) and `CORS_ORIGINS=https://solvia.app`.
- Table `lead_audits` created (run [`backend/sql/001_lead_audits.sql`](../backend/sql/001_lead_audits.sql) in Supabase SQL Editor).

## One-time: systemd unit

Create `/etc/systemd/system/solvia-audit-api.service`:

```ini
[Unit]
Description=Solvia lead audits FastAPI
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/solvia-site/backend
EnvironmentFile=/opt/solvia-site/backend/.env
ExecStart=/opt/solvia-site/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
cd /opt/solvia-site/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
systemctl daemon-reload
systemctl enable solvia-audit-api
systemctl start solvia-audit-api
systemctl status solvia-audit-api
```

## One-time: Caddy

In the Caddyfile for `solvia.app`, add a **`handle`** for `/api` **before** the static file handler so `/api/*` is proxied and everything else stays static. Example (adapt to your existing site block):

```caddyfile
solvia.app {
    handle /api/* {
        reverse_proxy 127.0.0.1:8000
    }
    handle {
        root * /opt/solvia/landing
        try_files {path} {path}/ /index.html
        file_server
    }
}
```

Reload Caddy (`caddy reload` or your usual process). Verify:

```bash
curl -sS https://solvia.app/api/health
```

Expect `{"status":"ok"}`.

## Outbound network

The VPS must reach Supabase Postgres (HTTPS/TLS to `db.*.supabase.co` on port 5432 or your pooler port). If you later restrict database access by IP in Supabase, add this server’s egress IP.

## CI/CD

After `git pull`, the deploy workflow installs `backend/requirements.txt` and runs `systemctl try-restart solvia-audit-api` when the backend folder exists. The unit must be installed once manually as above.
