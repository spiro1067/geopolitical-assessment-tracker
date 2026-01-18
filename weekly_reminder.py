#!/usr/bin/env python3
"""
Weekly Email Reminder for Overdue Assessments

Sends automated email reminders for overdue assessments.
Designed to be run as a cron job every Monday morning.

Usage:
    python3 weekly_reminder.py

Configuration (in order of security):
    1. Set SENDGRID_API_KEY environment variable (most secure)
    2. Set EMAIL_* environment variables (more secure)
    3. Create email_config.json (least secure)

See secure_email.py for setup instructions.
"""

import json
from pathlib import Path
from datetime import datetime
from secure_email import email_sender


# Email recipients
RECIPIENTS = [
    'alan.tkleung@gmail.com',
    'alan@tkstrat.net'
]

# Configuration
DATA_DIR = Path("./data")
CONFIG_FILE = Path("./email_config.json")


def load_data():
    """Load assessment data from JSON files."""
    assessments_file = DATA_DIR / "assessments.json"
    history_file = DATA_DIR / "history.json"

    if not assessments_file.exists():
        print("Error: No assessments file found")
        return {}, {}

    with open(assessments_file, 'r') as f:
        assessments = json.load(f)

    history = {}
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)

    return assessments, history


def get_overdue_assessments(assessments):
    """Get list of overdue assessments."""
    today = datetime.now().date()
    overdue = []
    due_soon = []

    for key, assessment in assessments.items():
        if assessment.get('next_review'):
            next_review = datetime.strptime(assessment['next_review'], "%Y-%m-%d").date()
            days_diff = (next_review - today).days

            if days_diff < 0:
                overdue.append({
                    'key': key,
                    'title': assessment['title'],
                    'days_overdue': abs(days_diff),
                    'next_review': assessment['next_review']
                })
            elif days_diff <= 3:
                due_soon.append({
                    'key': key,
                    'title': assessment['title'],
                    'days_until': days_diff,
                    'next_review': assessment['next_review']
                })
        elif assessment.get('current_probability') is None:
            overdue.append({
                'key': key,
                'title': assessment['title'],
                'days_overdue': None,
                'next_review': 'Never'
            })

    return overdue, due_soon


def build_email_body(overdue, due_soon, assessments):
    """Build HTML email body."""
    today = datetime.now().strftime('%A, %B %d, %Y')

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background: linear-gradient(135deg, #2E86AB, #A23B72);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .section {{
                margin-bottom: 30px;
            }}
            .section h2 {{
                color: #2E86AB;
                border-bottom: 2px solid #2E86AB;
                padding-bottom: 10px;
            }}
            .overdue {{
                background-color: #ffebee;
                border-left: 4px solid #E74C3C;
                padding: 15px;
                margin-bottom: 10px;
            }}
            .due-soon {{
                background-color: #fff8e1;
                border-left: 4px solid #F39C12;
                padding: 15px;
                margin-bottom: 10px;
            }}
            .assessment {{
                margin-bottom: 5px;
            }}
            .title {{
                font-weight: bold;
                font-size: 1.1em;
            }}
            .details {{
                color: #666;
                font-size: 0.9em;
            }}
            .cta {{
                background-color: #2E86AB;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 4px;
                display: inline-block;
                margin-top: 20px;
            }}
            .summary {{
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Weekly Assessment Tracker Reminder</h1>
            <p>{today}</p>
        </div>
        <div class="content">
    """

    # Summary
    total_needing_attention = len(overdue) + len(due_soon)
    html += f"""
            <div class="summary">
                <strong>Summary:</strong> You have {total_needing_attention} assessment(s) needing attention
                ({len(overdue)} overdue, {len(due_soon)} due soon)
            </div>
    """

    # Overdue assessments
    if overdue:
        html += """
            <div class="section">
                <h2>🔴 Overdue Assessments</h2>
                <p>These assessments are past their review date and require immediate attention:</p>
        """
        for item in overdue:
            if item['days_overdue'] is None:
                days_text = "Never assessed"
            else:
                days_text = f"{item['days_overdue']} days overdue"

            html += f"""
                <div class="overdue">
                    <div class="title">{item['title']}</div>
                    <div class="details">{days_text}</div>
                </div>
            """
        html += """
            </div>
        """

    # Due soon
    if due_soon:
        html += """
            <div class="section">
                <h2>🟡 Due Soon (Next 3 Days)</h2>
                <p>These assessments are coming up for review:</p>
        """
        for item in due_soon:
            days_text = f"Due in {item['days_until']} day{'s' if item['days_until'] != 1 else ''} ({item['next_review']})"

            html += f"""
                <div class="due-soon">
                    <div class="title">{item['title']}</div>
                    <div class="details">{days_text}</div>
                </div>
            """
        html += """
            </div>
        """

    # Call to action
    html += """
            <div class="section">
                <p>To update your assessments, use one of these options:</p>
                <ul>
                    <li><strong>Web Dashboard:</strong> <code>python3 tracker.py dashboard</code> then open http://127.0.0.1:5000</li>
                    <li><strong>Command Line:</strong> <code>python3 tracker.py update</code></li>
                    <li><strong>Weekly Workflow:</strong> <code>python3 tracker.py weekly</code> (update + report + visualize)</li>
                </ul>
            </div>
    """

    html += """
        </div>
    </body>
    </html>
    """

    return html


def send_email(subject, html_body, recipients):
    """Send HTML email using secure email sender."""
    return email_sender.send_email(subject, html_body, recipients)


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("WEEKLY ASSESSMENT REMINDER")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Configuration is handled by secure_email.py
    # It will try: SendGrid → Environment Variables → email_config.json

    # Load assessments
    print("Loading assessment data...")
    assessments, history = load_data()

    if not assessments:
        print("❌ No assessments found")
        return

    # Get overdue/due soon
    print("Checking for overdue assessments...")
    overdue, due_soon = get_overdue_assessments(assessments)

    print(f"Found: {len(overdue)} overdue, {len(due_soon)} due soon\n")

    # Only send email if there are assessments needing attention
    if not overdue and not due_soon:
        print("✅ All assessments are up to date!")
        print("No email reminder needed.")
        return

    # Build email
    print("Building email...")
    subject = f"Assessment Tracker Weekly Reminder - {len(overdue)} Overdue"
    html_body = build_email_body(overdue, due_soon, assessments)

    # Send email
    print(f"Sending email to {len(RECIPIENTS)} recipient(s)...")
    success = send_email(subject, html_body, RECIPIENTS)

    if success:
        print("\n✅ Weekly reminder sent successfully!")
    else:
        print("\n❌ Failed to send weekly reminder")

    print("="*70 + "\n")


if __name__ == '__main__':
    main()
