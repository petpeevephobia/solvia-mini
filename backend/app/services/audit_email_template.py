"""Build HTML + plain-text multipart content for the audit delivery email."""

from __future__ import annotations

import markdown as md

_CONTACT_EMAIL = "qamaria.mdsah@gmail.com"
_BRAND_COLOR = "#EC6019"
_DARK = "#0A0A0A"
_LIGHT_BG = "#F7F7F7"
_BORDER = "#E5E5E5"


def _render_html(report_markdown: str, audited_url: str) -> str:
    body_html = md.markdown(
        report_markdown,
        extensions=["extra", "nl2br"],
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your SEO Audit from Solvia Labs</title>
</head>
<body style="margin:0;padding:0;background-color:{_LIGHT_BG};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;color:{_DARK};">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{_LIGHT_BG};padding:32px 16px;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:8px;border:1px solid {_BORDER};overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="padding:28px 40px;text-align:center;">
              <h1>📦 Special Delivery from Solvia Mini</h1>
            </td>
          </tr>

          <!-- Intro band -->
          <tr>
            <td style="background-color:{_BRAND_COLOR};padding:24px 40px;">
              <p style="margin:0;font-size:15px;font-weight:600;color:#ffffff;line-height:1.4;">
                Your website SEO audit is ready
              </p>
              <p style="margin:6px 0 0;font-size:13px;color:rgba(255,255,255,0.85);line-height:1.5;">
                Audited: <a href="{audited_url}" style="color:#ffffff;text-decoration:underline;">{audited_url}</a>
              </p>
            </td>
          </tr>

          <!-- Report body -->
          <tr>
            <td style="padding:36px 40px;">
              <div style="font-size:15px;line-height:1.7;color:{_DARK};">
                {body_html}
              </div>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding:0 40px;">
              <hr style="border:none;border-top:1px solid {_BORDER};margin:0;">
            </td>
          </tr>


          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px;text-align:center;">
              <p style="margin:0;font-size:12px;color:#888888;line-height:1.6;">
                You received this email because you requested a free website SEO audit from
                <a href="https://solvia-mini.fly.dev" target="_blank" style="color:#888888;">solvia-mini.fly.dev</a>.
                This is a transactional message related to your request.
              </p>
              <p style="margin:10px 0 0;font-size:12px;color:#888888;line-height:1.6;">
                <a href="mailto:{_CONTACT_EMAIL}" style="color:#888888;text-decoration:underline;">Talk to the builder</a>
              </p>
              <p style="margin:10px 0 0;font-size:12px;color:#888888;">
                © 2026 Nadra Qamaria
              </p>
            </td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>

</body>
</html>"""


def _render_plaintext(report_markdown: str, audited_url: str) -> str:
    return f"""Your website SEO audit is ready
==============================

Audited URL: {audited_url}

{report_markdown}

--

You received this email because you requested a free SEO audit at solvia.app.
This is a transactional message related to your request.

Contact: {_CONTACT_EMAIL}

© Solvia Labs Pte. Ltd. · Singapore
"""


def build_audit_email(
    report_markdown: str,
    audited_url: str,
) -> tuple[str, str, str]:
    """Return (subject, html_body, plaintext_body)."""
    subject = f"Your SEO audit for {audited_url}"
    html = _render_html(report_markdown, audited_url)
    text = _render_plaintext(report_markdown, audited_url)
    return subject, html, text
