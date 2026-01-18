#!/bin/bash
# Setup script for automated weekly email reminders

echo "=========================================="
echo "Weekly Email Reminder Setup"
echo "=========================================="
echo ""

# Get the absolute path to the tracker directory
TRACKER_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_CMD="python3"

echo "Tracker directory: $TRACKER_DIR"
echo ""

# Check if email_config.json exists
if [ ! -f "$TRACKER_DIR/email_config.json" ]; then
    echo "⚠️  Email configuration not found!"
    echo ""
    echo "Please create email_config.json with your SMTP settings:"
    echo "  cp email_config.json.example email_config.json"
    echo "  nano email_config.json  # Edit with your details"
    echo ""
    exit 1
fi

echo "✅ Email configuration found"
echo ""

# Test the email reminder
echo "Testing email reminder..."
cd "$TRACKER_DIR"
$PYTHON_CMD weekly_reminder.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Email reminder test failed"
    echo "Please check your email_config.json settings"
    exit 1
fi

echo ""
echo "✅ Email reminder test successful!"
echo ""

# Ask if user wants to set up cron job
read -p "Do you want to set up automated weekly emails? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 0
fi

# Suggest cron schedule
echo ""
echo "When should the weekly reminder be sent?"
echo "  1) Every Monday at 9:00 AM"
echo "  2) Every Monday at 8:00 AM"
echo "  3) Every Sunday at 6:00 PM"
echo "  4) Custom schedule"
echo ""
read -p "Choose option (1-4): " -n 1 -r
echo ""

case $REPLY in
    1)
        CRON_SCHEDULE="0 9 * * 1"
        DESCRIPTION="Every Monday at 9:00 AM"
        ;;
    2)
        CRON_SCHEDULE="0 8 * * 1"
        DESCRIPTION="Every Monday at 8:00 AM"
        ;;
    3)
        CRON_SCHEDULE="0 18 * * 0"
        DESCRIPTION="Every Sunday at 6:00 PM"
        ;;
    4)
        echo "Enter cron schedule (e.g., '0 9 * * 1' for Mon 9AM):"
        read CRON_SCHEDULE
        DESCRIPTION="Custom schedule: $CRON_SCHEDULE"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

# Create cron entry
CRON_COMMAND="cd $TRACKER_DIR && $PYTHON_CMD weekly_reminder.py >> $TRACKER_DIR/weekly_reminder.log 2>&1"
CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND"

echo ""
echo "The following cron job will be added:"
echo "  Schedule: $DESCRIPTION"
echo "  Command: $CRON_COMMAND"
echo ""
read -p "Proceed? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 0
fi

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Cron job added successfully!"
    echo ""
    echo "Your weekly email reminders are now automated."
    echo "Emails will be sent to:"
    echo "  - alan.tkleung@gmail.com"
    echo "  - alan@tkstrat.net"
    echo ""
    echo "Schedule: $DESCRIPTION"
    echo "Log file: $TRACKER_DIR/weekly_reminder.log"
    echo ""
    echo "To view your cron jobs: crontab -l"
    echo "To edit your cron jobs: crontab -e"
    echo "To remove this job: crontab -e (and delete the line)"
else
    echo ""
    echo "❌ Failed to add cron job"
    echo "You can manually add this to your crontab:"
    echo "$CRON_ENTRY"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
