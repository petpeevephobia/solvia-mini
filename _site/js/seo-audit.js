(function () {
    'use strict';

    const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? 'http://localhost:8000/api/v1'
        : '/api/v1';

    const POLL_INTERVAL_MS = 3000;
    const MAX_POLL_ATTEMPTS = 60; // ~3 min before timeout message

    const STEP_ORDER = ['queued', 'scraping', 'analyzing', 'generating'];

    // DOM refs
    const form        = document.getElementById('audit-form');
    const urlInput    = document.getElementById('audit-url');
    const emailInput  = document.getElementById('audit-email');
    const submitBtn   = document.getElementById('audit-submit');
    const urlError    = document.getElementById('audit-url-error');
    const emailError  = document.getElementById('audit-email-error');
    const progressEl  = document.getElementById('audit-progress');
    const successEl   = document.getElementById('audit-success');
    const errorEl     = document.getElementById('audit-error-global');
    const retryBtn    = document.getElementById('audit-retry');
    const stepEls     = document.querySelectorAll('.audit-step');

    if (!form) return; // section not present on this page

    // ── Validation ────────────────────────────────────────────

    function validateUrl(value) {
        const v = value.trim();
        if (!v) return 'Please enter your website URL.';
        if (!/^https?:\/\//i.test(v)) return 'URL must start with https:// or http://';
        return null;
    }

    function validateEmail(value) {
        const v = value.trim();
        if (!v) return 'Please enter your email address.';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return 'Please enter a valid email address.';
        return null;
    }

    function showFieldError(el, msg) {
        el.textContent = msg;
        el.hidden = false;
    }

    function clearFieldError(el) {
        el.textContent = '';
        el.hidden = true;
    }

    // ── State transitions ─────────────────────────────────────

    function showForm() {
        form.hidden = false;
        progressEl.hidden = true;
        successEl.hidden = true;
        errorEl.hidden = true;
        submitBtn.disabled = false;
    }

    function showProgress() {
        form.hidden = true;
        progressEl.hidden = false;
        successEl.hidden = true;
        errorEl.hidden = true;
    }

    function showSuccess() {
        form.hidden = true;
        progressEl.hidden = true;
        successEl.hidden = false;
        errorEl.hidden = true;
    }

    function showFailure() {
        form.hidden = true;
        progressEl.hidden = true;
        successEl.hidden = true;
        errorEl.hidden = false;
    }

    // ── Progress step highlighting ────────────────────────────

    function setStep(status) {
        const activeIndex = STEP_ORDER.indexOf(status);
        stepEls.forEach(function (el) {
            const stepName = el.getAttribute('data-step');
            const stepIndex = STEP_ORDER.indexOf(stepName);
            el.classList.remove('active', 'done');
            if (stepIndex < activeIndex) {
                el.classList.add('done');
            } else if (stepName === status || (status === 'queued' && stepIndex === 0)) {
                el.classList.add('active');
            }
        });
    }

    // ── API calls ─────────────────────────────────────────────

    async function submitAudit(url, email) {
        const res = await fetch(API_BASE + '/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url.trim(), email: email.trim().toLowerCase() }),
        });
        if (res.status === 202) {
            return await res.json(); // { audit_id, status }
        }
        // Surface validation errors from server
        if (res.status === 422) {
            const body = await res.json().catch(function () { return {}; });
            throw new Error('validation:' + JSON.stringify(body));
        }
        throw new Error('server:' + res.status);
    }

    async function fetchStatus(auditId) {
        const res = await fetch(API_BASE + '/audit/' + auditId + '/status');
        if (!res.ok) throw new Error('poll:' + res.status);
        return await res.json(); // { audit_id, status, error_message }
    }

    // ── Polling loop ──────────────────────────────────────────

    function startPolling(auditId) {
        let attempts = 0;
        setStep('queued');

        const timer = setInterval(async function () {
            attempts++;

            if (attempts > MAX_POLL_ATTEMPTS) {
                clearInterval(timer);
                // Still running but taking long — inform user without showing failure
                const note = progressEl.querySelector('.audit-progress-note');
                if (note) {
                    note.textContent = 'Taking longer than expected — we\'ll email you as soon as it\'s ready.';
                }
                return;
            }

            try {
                const data = await fetchStatus(auditId);
                setStep(data.status);

                if (data.status === 'complete') {
                    clearInterval(timer);
                    showSuccess();
                } else if (data.status === 'failed') {
                    clearInterval(timer);
                    showFailure();
                }
            } catch (err) {
                // Network hiccup — keep polling until max attempts
                console.warn('[seo-audit] poll error:', err.message);
            }
        }, POLL_INTERVAL_MS);
    }

    // ── Form submit ───────────────────────────────────────────

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const urlVal   = urlInput.value;
        const emailVal = emailInput.value;

        const urlErr   = validateUrl(urlVal);
        const emailErr = validateEmail(emailVal);

        if (urlErr)   showFieldError(urlError, urlErr);   else clearFieldError(urlError);
        if (emailErr) showFieldError(emailError, emailErr); else clearFieldError(emailError);

        if (urlErr || emailErr) return;

        submitBtn.disabled = true;
        clearFieldError(urlError);
        clearFieldError(emailError);

        try {
            const data = await submitAudit(urlVal, emailVal);
            showProgress();
            startPolling(data.audit_id);
        } catch (err) {
            submitBtn.disabled = false;
            if (err.message && err.message.startsWith('validation:')) {
                // Try to surface the first server validation error
                try {
                    const body = JSON.parse(err.message.replace('validation:', ''));
                    const detail = body.detail;
                    if (Array.isArray(detail) && detail.length > 0) {
                        const first = detail[0];
                        const loc   = (first.loc || []).join('.');
                        const msg   = first.msg || 'Invalid input.';
                        if (loc.includes('url'))   showFieldError(urlError, msg);
                        else if (loc.includes('email')) showFieldError(emailError, msg);
                        else showFieldError(urlError, msg);
                        return;
                    }
                } catch (_) { /* fall through to generic error */ }
            }
            showFailure();
        }
    });

    // ── Retry button ──────────────────────────────────────────

    if (retryBtn) {
        retryBtn.addEventListener('click', function () {
            showForm();
            urlInput.focus();
        });
    }

    // ── Clear errors on input ─────────────────────────────────

    urlInput.addEventListener('input', function () { clearFieldError(urlError); });
    emailInput.addEventListener('input', function () { clearFieldError(emailError); });

}());
