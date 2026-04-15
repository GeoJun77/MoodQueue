import resend
from app.core.config import settings

# Initialize Resend with our API key
resend.api_key = settings.RESEND_API_KEY

# Sender address — using Resend's default domain
FROM_EMAIL = "MoodQueue <onboarding@resend.dev>"


async def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Sends a password reset email with a link containing the reset token.
    The link points to our web frontend reset page.
    Returns True if the email was sent successfully, False otherwise.
    """
    # Build the reset URL — points to the web frontend
    reset_url = f"http://localhost:5173/reset-password?token={reset_token}"

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": "Reset your MoodQueue password 🎵",
            "html": f"""
            <div style="font-family: -apple-system, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px; background: #0a0a0f; color: #f1f5f9;">
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #1DB954, #17a34a); border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 16px;">
                        🎵
                    </div>
                    <h1 style="font-size: 24px; font-weight: 800; margin: 0; color: #f1f5f9;">MoodQueue</h1>
                </div>

                <div style="background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 32px;">
                    <h2 style="font-size: 20px; font-weight: 700; margin: 0 0 12px; color: #f1f5f9;">
                        Reset your password
                    </h2>
                    <p style="color: #64748b; font-size: 15px; line-height: 1.6; margin: 0 0 24px;">
                        We received a request to reset your password. Click the button below to create a new one.
                        This link expires in <strong style="color: #f1f5f9;">1 hour</strong>.
                    </p>

                    <a href="{reset_url}"
                       style="display: block; background: linear-gradient(135deg, #1DB954, #17a34a); color: #fff; text-decoration: none; text-align: center; padding: 14px 0; border-radius: 12px; font-size: 15px; font-weight: 700;">
                        Reset my password →
                    </a>

                    <p style="color: #475569; font-size: 12px; margin: 20px 0 0; text-align: center;">
                        If you didn't request this, you can safely ignore this email.
                    </p>
                </div>

                <p style="color: #334155; font-size: 12px; text-align: center; margin-top: 24px;">
                    © 2025 MoodQueue — Your mood, your soundtrack
                </p>
            </div>
            """,
        })
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False