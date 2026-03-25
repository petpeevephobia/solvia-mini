# Supabase connection (lead audits / FastAPI)

Use the **same Supabase project** as the Solvia web app. The FastAPI backend reads/writes `lead_audits` via a direct Postgres connection string (`DATABASE_URL`), not the REST `anon` / `service_role` keys.

## Connection string

1. Open **Project Settings** (gear) → **Database**.
2. Under **Connection string**, choose **URI** (direct connection is usually port **5432**).
3. Copy the URI and replace `[YOUR-PASSWORD]` with your **database password** (set or reset under Database settings).

Example shape:

```text
postgresql://postgres:[YOUR-PASSWORD]@db.<project-ref>.supabase.co:5432/postgres
```

**Verify the host** matches your dashboard (`db.<project-ref>.supabase.co`). If the project ref in the UI differs from what you expect, copy it from the dashboard—do not guess.

## Local env

Copy [`backend/.env.example`](../backend/.env.example) to `backend/.env`, set `DATABASE_URL`, and never commit `.env`.

Create the table by running [`backend/sql/001_lead_audits.sql`](../backend/sql/001_lead_audits.sql) in the Supabase SQL Editor before calling the API.

## Optional: Supabase Agent Skills (Cursor)

Supabase publishes optional skills for AI tooling:

```bash
npx skills add supabase/agent-skills
```

Run only if you use Cursor skills and want Supabase-specific guidance in-editor.

## Related

- Table: `lead_audits` (create in **Table Editor** or SQL).
- RLS: server-only access via FastAPI is typical; avoid broad `anon`/`authenticated` SELECT policies on PII.
