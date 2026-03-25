-- Run once in Supabase SQL Editor (or via migration tool) before starting the API.
CREATE TABLE IF NOT EXISTS public.lead_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url VARCHAR(2048) NOT NULL,
    email VARCHAR(320) NOT NULL,
    status VARCHAR(32) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    report_markdown TEXT,
    page_audit_json JSONB,
    serp_analysis_json JSONB
);

CREATE INDEX IF NOT EXISTS idx_lead_audits_created_at ON public.lead_audits (created_at DESC);
