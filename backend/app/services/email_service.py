"""
Password reset emails via Resend (optional).

Without RESEND_API_KEY the reset link is written to the server logs, so a
self-hosted instance can still recover accounts.
"""
import asyncio
import logging
from datetime import datetime

from app.core.config import settings

log = logging.getLogger("moodqueue.email")


def _html(reset_url: str) -> str:
    year = datetime.now().year
    return f"""
<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:480px;margin:0 auto;padding:40px 20px;background:#0a0a0f;color:#f1f5f9;">
  <div style="text-align:center;margin-bottom:32px;">
    <div style="font-size:40px;">🎵</div>
    <h1 style="font-size:24px;font-weight:800;margin:8px 0 0;">MoodQueue</h1>
  </div>
  <div style="background:#0f172a;border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:32px;">
    <h2 style="font-size:20px;margin:0 0 12px;">Reset your password</h2>
    <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin:0 0 24px;">
      We received a request to reset your password. This link expires in <strong style="color:#f1f5f9;">1 hour</strong>.
    </p>
    <a href="{reset_url}" style="display:block;background:#1DB954;color:#fff;text-decoration:none;text-align:center;padding:14px 0;border-radius:12px;font-weight:700;">
      Reset my password →
    </a>
    <p style="color:#64748b;font-size:12px;margin:20px 0 0;text-align:center;">
      If you didn't request this, you can ignore this email.
    </p>
  </div>
  <p style="color:#475569;font-size:12px;text-align:center;margin-top:24px;">© {year} MoodQueue — Your mood, your soundtrack</p>
</div>"""


async def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """Returns True if an email was sent, False if only logged."""
    if not settings.email_enabled:
        log.warning("Email not configured. Password reset link for %s: %s", to_email, reset_url)
        return False
    try:
        import resend  # optional dependency

        resend.api_key = settings.RESEND_API_KEY
        await asyncio.to_thread(
            resend.Emails.send,
            {
                "from": settings.EMAIL_FROM,
                "to": to_email,
                "subject": "Reset your MoodQueue password 🎵",
                "html": _html(reset_url),
            },
        )
        return True
    except Exception as e:
        log.error("Failed to send reset email (%s). Link for %s: %s", e, to_email, reset_url)
        return False
