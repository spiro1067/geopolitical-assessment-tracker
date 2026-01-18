#!/usr/bin/env python3
"""
Secure email sending with multiple authentication methods

Supports:
1. OAuth 2.0 (Gmail - Most Secure)
2. Environment Variables (Better than plain text)
3. SendGrid API (Professional service)
4. SMTP with App Password (fallback)
"""

import os
import json
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional


class SecureEmailSender:
    """Handles secure email sending with multiple authentication methods."""

    def __init__(self):
        self.config_file = Path("./email_config.json")

    def send_email(self, subject: str, html_body: str, recipients: list) -> bool:
        """
        Send email using the most secure method available.

        Priority order:
        1. Brevo API (if API key available) - 300 emails/day free
        2. SendGrid API (if API key available) - 100 emails/day free
        3. Mailjet API (if API keys available) - 200 emails/day free
        4. Resend API (if API key available) - 100 emails/day free
        5. Environment variables SMTP (if set)
        6. email_config.json (if exists)
        """

        # Method 1: Try Brevo API (best free tier - 300/day)
        if os.getenv('BREVO_API_KEY'):
            return self._send_via_brevo(subject, html_body, recipients)

        # Method 2: Try SendGrid API (good docs - 100/day)
        if os.getenv('SENDGRID_API_KEY'):
            return self._send_via_sendgrid(subject, html_body, recipients)

        # Method 3: Try Mailjet API (good free tier - 200/day)
        if os.getenv('MAILJET_API_KEY') and os.getenv('MAILJET_SECRET_KEY'):
            return self._send_via_mailjet(subject, html_body, recipients)

        # Method 4: Try Resend API (developer-friendly - 100/day)
        if os.getenv('RESEND_API_KEY'):
            return self._send_via_resend(subject, html_body, recipients)

        # Method 5: Try environment variables
        if self._has_env_config():
            return self._send_via_env_smtp(subject, html_body, recipients)

        # Method 6: Try email_config.json
        if self.config_file.exists():
            return self._send_via_config_file(subject, html_body, recipients)

        print("❌ No email configuration found!")
        print("\nAvailable FREE options (no password storage required):")
        print("1. Brevo API (300/day): export BREVO_API_KEY='your-key'")
        print("2. SendGrid API (100/day): export SENDGRID_API_KEY='your-key'")
        print("3. Mailjet API (200/day): export MAILJET_API_KEY='key' MAILJET_SECRET_KEY='secret'")
        print("4. Resend API (100/day): export RESEND_API_KEY='your-key'")
        print("5. Environment variables: export EMAIL_SMTP_SERVER=... (less secure)")
        print("6. email_config.json (least secure)")
        print("\nSee FREE_EMAIL_SERVICES.md for comparison of all free options")
        return False

    def _send_via_brevo(self, subject: str, html_body: str, recipients: list) -> bool:
        """Send email via Brevo (formerly Sendinblue) API - 300 emails/day free."""
        try:
            import sib_api_v3_sdk
            from sib_api_v3_sdk.rest import ApiException

            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')

            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

            from_email = os.getenv('EMAIL_FROM', 'noreply@assessmenttracker.com')

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": email} for email in recipients],
                html_content=html_body,
                sender={"email": from_email},
                subject=subject
            )

            api_instance.send_transac_email(send_smtp_email)

            print(f"✅ Email sent via Brevo to: {', '.join(recipients)}")
            return True

        except ImportError:
            print("⚠️  Brevo library not installed. Install with: pip install sib-api-v3-sdk")
            return False
        except Exception as e:
            print(f"❌ Brevo error: {e}")
            return False

    def _send_via_mailjet(self, subject: str, html_body: str, recipients: list) -> bool:
        """Send email via Mailjet API - 200 emails/day free."""
        try:
            from mailjet_rest import Client

            api_key = os.getenv('MAILJET_API_KEY')
            api_secret = os.getenv('MAILJET_SECRET_KEY')
            from_email = os.getenv('EMAIL_FROM', 'noreply@assessmenttracker.com')

            mailjet = Client(auth=(api_key, api_secret), version='v3.1')

            data = {
                'Messages': [
                    {
                        "From": {"Email": from_email},
                        "To": [{"Email": email} for email in recipients],
                        "Subject": subject,
                        "HTMLPart": html_body
                    }
                ]
            }

            result = mailjet.send.create(data=data)

            if result.status_code == 200:
                print(f"✅ Email sent via Mailjet to: {', '.join(recipients)}")
                return True
            else:
                print(f"❌ Mailjet error: {result.status_code}")
                return False

        except ImportError:
            print("⚠️  Mailjet library not installed. Install with: pip install mailjet-rest")
            return False
        except Exception as e:
            print(f"❌ Mailjet error: {e}")
            return False

    def _send_via_resend(self, subject: str, html_body: str, recipients: list) -> bool:
        """Send email via Resend API - 100 emails/day free."""
        try:
            import resend

            resend.api_key = os.getenv('RESEND_API_KEY')
            from_email = os.getenv('EMAIL_FROM', 'noreply@assessmenttracker.com')

            params = {
                "from": from_email,
                "to": recipients,
                "subject": subject,
                "html": html_body
            }

            resend.Emails.send(params)

            print(f"✅ Email sent via Resend to: {', '.join(recipients)}")
            return True

        except ImportError:
            print("⚠️  Resend library not installed. Install with: pip install resend")
            return False
        except Exception as e:
            print(f"❌ Resend error: {e}")
            return False

    def _send_via_sendgrid(self, subject: str, html_body: str, recipients: list) -> bool:
        """Send email via SendGrid API - 100 emails/day free."""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            from_email = os.getenv('EMAIL_FROM', 'noreply@assessmenttracker.com')

            message = Mail(
                from_email=from_email,
                to_emails=recipients,
                subject=subject,
                html_content=html_body
            )

            sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
            response = sg.send(message)

            print(f"✅ Email sent via SendGrid to: {', '.join(recipients)}")
            return True

        except ImportError:
            print("⚠️  SendGrid library not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            print(f"❌ SendGrid error: {e}")
            return False

    def _has_env_config(self) -> bool:
        """Check if all required environment variables are set."""
        required = ['EMAIL_SMTP_SERVER', 'EMAIL_SMTP_PORT', 'EMAIL_USER',
                   'EMAIL_PASSWORD', 'EMAIL_FROM']
        return all(os.getenv(var) for var in required)

    def _send_via_env_smtp(self, subject: str, html_body: str, recipients: list) -> bool:
        """Send email using environment variables (more secure than config file)."""
        try:
            config = {
                'smtp_server': os.getenv('EMAIL_SMTP_SERVER'),
                'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
                'smtp_user': os.getenv('EMAIL_USER'),
                'smtp_password': os.getenv('EMAIL_PASSWORD'),
                'from_email': os.getenv('EMAIL_FROM')
            }

            return self._send_smtp(subject, html_body, recipients, config)

        except Exception as e:
            print(f"❌ Environment variable email error: {e}")
            return False

    def _send_via_config_file(self, subject: str, html_body: str, recipients: list) -> bool:
        """Send email using email_config.json (least secure, but simplest)."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            print("⚠️  Warning: Using email_config.json is less secure!")
            print("   Consider using environment variables or SendGrid instead.")

            return self._send_smtp(subject, html_body, recipients, config)

        except Exception as e:
            print(f"❌ Config file email error: {e}")
            return False

    def _send_smtp(self, subject: str, html_body: str, recipients: list, config: Dict) -> bool:
        """Send email via SMTP (common backend for env vars and config file)."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = config['from_email']
            msg['To'] = ', '.join(recipients)

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['smtp_user'], config['smtp_password'])
                server.send_message(msg)

            print(f"✅ Email sent to: {', '.join(recipients)}")
            return True

        except Exception as e:
            print(f"❌ SMTP error: {e}")
            return False


def setup_env_variables():
    """Helper to guide user through setting up environment variables."""
    print("\n" + "="*70)
    print("SECURE EMAIL SETUP - Environment Variables")
    print("="*70)
    print("\nThis is more secure than storing passwords in files.\n")

    print("Add these to your ~/.bashrc or ~/.zshrc:\n")
    print("export EMAIL_SMTP_SERVER='smtp.gmail.com'")
    print("export EMAIL_SMTP_PORT='587'")
    print("export EMAIL_USER='your_email@gmail.com'")
    print("export EMAIL_PASSWORD='your_app_password'")
    print("export EMAIL_FROM='your_email@gmail.com'")
    print("\nThen run: source ~/.bashrc")
    print("\nOr for this session only:")
    print("export EMAIL_SMTP_SERVER='smtp.gmail.com' EMAIL_SMTP_PORT='587' ...")


def setup_sendgrid():
    """Helper to guide user through setting up SendGrid."""
    print("\n" + "="*70)
    print("SECURE EMAIL SETUP - SendGrid (Recommended)")
    print("="*70)
    print("\nSendGrid is more secure and professional for automated emails.\n")

    print("Steps:")
    print("1. Sign up at: https://signup.sendgrid.com/")
    print("2. Create an API key: Settings → API Keys → Create API Key")
    print("3. Install SendGrid: pip install sendgrid")
    print("4. Set environment variable:")
    print("   export SENDGRID_API_KEY='your-api-key'")
    print("   export EMAIL_FROM='your-verified-sender@yourdomain.com'")
    print("\nBenefits:")
    print("  ✓ No password storage needed")
    print("  ✓ API keys can be revoked instantly")
    print("  ✓ Better deliverability")
    print("  ✓ Free tier: 100 emails/day")


# Singleton instance
email_sender = SecureEmailSender()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'setup-env':
        setup_env_variables()
    elif len(sys.argv) > 1 and sys.argv[1] == 'setup-sendgrid':
        setup_sendgrid()
    else:
        print("\nSecure Email Sender Configuration")
        print("="*70)
        print("\nUsage:")
        print("  python3 secure_email.py setup-env       # Setup environment variables")
        print("  python3 secure_email.py setup-sendgrid  # Setup SendGrid")
        print("\nCurrent configuration status:")

        if os.getenv('SENDGRID_API_KEY'):
            print("  ✅ SendGrid API key found (most secure)")
        else:
            print("  ❌ SendGrid not configured")

        if email_sender._has_env_config():
            print("  ✅ Environment variables configured")
        else:
            print("  ❌ Environment variables not set")

        if email_sender.config_file.exists():
            print("  ⚠️  email_config.json found (least secure)")
        else:
            print("  ❌ email_config.json not found")
