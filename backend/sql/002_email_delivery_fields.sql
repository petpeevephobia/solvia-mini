-- Migration: add email delivery tracking columns to lead_audits
-- Run once in Supabase SQL Editor (or via migration tool) after 001_lead_audits.sql

ALTER TABLE public.lead_audits
    ADD COLUMN IF NOT EXISTS email_sent_at     TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS email_failed_at   TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS email_error_message TEXT,
    ADD COLUMN IF NOT EXISTS email_attempts    INTEGER NOT NULL DEFAULT 0;
