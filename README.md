# Automated Weekly Assessment Tracker

A comprehensive system for maintaining ongoing risk assessments with automated weekly updates, historical tracking, visualizations, and custom topic management.

## Features

### Core Functionality
✅ **Custom Topic Management** - Add, edit, or remove any assessment topics
✅ **6 Pre-configured Questions** - Standard geopolitical scenarios ready to use
✅ **Weekly Update Workflow** - Guided prompts to update assessments
✅ **Historical Logging** - Every change tracked with timestamps
✅ **Indicator Monitoring** - Track status of key indicators (🟢🟡🔴)
✅ **Change Detection** - Automatic calculation of probability shifts

### Visualization & Reporting
✅ **Probability Timelines** - Visual charts showing assessment evolution
✅ **Current Snapshot Charts** - Color-coded bar charts of all probabilities
✅ **Comparison Views** - All topics side-by-side in one chart
✅ **Comprehensive Reports** - Weekly summary with risk levels and trends

### Web Dashboard
✅ **Interactive Dashboard** - Real-time web interface with charts and status cards
✅ **Mobile Responsive** - Works on desktop, tablet, and mobile devices
✅ **REST API** - JSON endpoints for integration with other tools

### Data Export & Notifications
✅ **CSV Export** - Export all data for spreadsheet analysis
✅ **Markdown Reports** - Generate shareable documentation
✅ **Overdue Tracking** - Status dashboard for due/overdue assessments
✅ **Email Reminders** - Automated notifications for overdue reviews
✅ **Desktop Notifications** - System alerts for pending assessments

## Installation

### Prerequisites

**For CLI usage only:**
```bash
pip install matplotlib --break-system-packages
```

**For web dashboard (includes matplotlib):**
```bash
pip install -r requirements.txt --break-system-packages
```

Or install individually:
```bash
pip install matplotlib Flask --break-system-packages
```

Core functionality uses Python standard library only!

### Setup

1. Place the tracker files in your working directory
2. The system will automatically create necessary directories:
   - `data/` - Stores assessments, history, and topic configurations
   - `visualizations/` - Generated charts

**Note:** On first run, the system will create `data/topics.json` with the 6 standard questions. You can modify this file directly or use the topic management commands.

## Quick Start

### First Time Use

Run the weekly update workflow to initialize your first assessments:

```bash
python3 tracker.py update
```

This will guide you through updating each of the 6 standard questions.

### Weekly Workflow (Recommended)

Every Monday morning (or your preferred cadence), run:

```bash
python3 tracker.py update
```

The system will:
1. Show which assessments need review
2. Display previous assessment for context
3. Guide you through updating probability, drivers, and indicators
4. Log all changes with timestamps
5. Schedule next review

**Time estimate: 10-15 minutes per week** (vs 1-2 hours manually tracking)

## Usage Guide

### Core Assessment Commands

**View current assessments:**
```bash
python3 tracker.py view                    # See all assessments
python3 tracker.py view iranian_collapse   # View specific topic
```

**View historical changes:**
```bash
python3 tracker.py history iranian_collapse
```
Shows:
- All past probability assessments
- Probability changes (↗ increase, ↘ decrease)
- Key drivers for each update
- Notes on what changed

**Update assessments:**
```bash
python3 tracker.py update                  # Weekly workflow (all due topics)
python3 tracker.py update iranian_collapse # Update single topic
```

**Check status:**
```bash
python3 tracker.py status                  # Show overdue/due-soon assessments
python3 tracker.py status --check-overdue  # Check and send notifications
```

### Visualization Commands

**Generate visualizations:**
```bash
python3 tracker.py visualize               # Create all charts
python3 tracker.py visualize iran_collapse # Chart for specific topic
```

Charts generated:
- **current_snapshot.png** - Bar chart of current probabilities (color-coded by risk level)
- **{topic}_timeline.png** - Line chart showing probability evolution over time
- **all_topics_comparison.png** - Multi-panel view of all topics

### Reporting Commands

**Generate comprehensive report:**
```bash
python3 tracker.py report
```
Shows:
- Status overview (total/assessed/overdue)
- Current risk levels (grouped by severity)
- Significant recent changes (±5% or more)

**Weekly workflow (all-in-one):**
```bash
python3 tracker.py weekly
```
Combines: update → report → visualize in one command

### Export Commands

**Export to CSV:**
```bash
python3 tracker.py export --format csv
python3 tracker.py export --format csv --output my_export.csv
```

**Export to Markdown:**
```bash
python3 tracker.py export --format markdown
python3 tracker.py export --format markdown --output report.md
```

### Topic Management Commands

**List all topics:**
```bash
python3 tracker.py list-topics
```

**Add custom topic:**
```bash
python3 tracker.py add-topic my_custom_risk
```
Prompts for:
- Title
- Assessment question
- Time horizon
- Key indicators to track

**Edit existing topic:**
```bash
python3 tracker.py edit-topic iranian_collapse
```

**Remove topic:**
```bash
python3 tracker.py remove-topic my_old_topic
```
Requires typing 'DELETE' to confirm (prevents accidental data loss)

### Notification Commands

**Send desktop notification:**
```bash
python3 tracker.py notify
```

**Send email reminder:**
```bash
python3 tracker.py notify --email-config email_config.json
```

**Email configuration file format** (`email_config.json`):
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your_email@gmail.com",
  "smtp_password": "your_app_password",
  "from_email": "your_email@gmail.com",
  "to_email": "recipient@example.com"
}
```

### Web Dashboard

**Start the interactive web dashboard:**
```bash
python3 tracker.py dashboard
```

The dashboard will start at http://127.0.0.1:5000 by default.

**Custom port and host:**
```bash
python3 tracker.py dashboard --port 8080 --host 0.0.0.0
```

**Dashboard Features:**
- **Real-time overview**: Visual status cards showing total topics, assessed count, overdue, and due-soon
- **Risk-level cards**: Color-coded assessment cards showing current probabilities
- **Interactive charts**: Click on any topic to see detailed timeline charts
- **Trend indicators**: Visual arrows showing if probabilities are increasing/decreasing
- **Mobile responsive**: Works on desktop, tablet, and mobile devices
- **API endpoints**: JSON data available at `/api/assessments` and `/api/topic/<key>`

The dashboard automatically reads from your `data/` directory and displays current assessments. Refresh the page to see the latest data after running updates.

**Alternative: Run dashboard directly:**
```bash
python3 dashboard.py                    # Start with defaults
python3 dashboard.py --port 8080        # Custom port
python3 dashboard.py --host 0.0.0.0     # Allow external connections
```

**Dashboard Requirements:**
```bash
pip install Flask --break-system-packages
```

## Pre-configured Topics

The tracker includes these 6 standard questions (stored in `data/topics.json`):

1. **iranian_collapse** - Iranian government collapse (3 months)
2. **venezuela_civil_war** - Venezuela civil war (3 months)
3. **ukraine_agreement** - Russia-Ukraine political agreement (3 months)
4. **taiwan_invasion** - Taiwan invasion by China (6 months)
5. **food_security_crisis** - Global food security crisis (6 months)
6. **greenland_control** - US control of Greenland (6 months)

Each includes pre-defined key indicators to track.

**You can add your own topics** using `python3 tracker.py add-topic <key>` - the system supports any number of custom assessment questions!

## File Structure

```
assessment-tracker/
├── tracker.py              # Main tracking script (includes all functionality)
├── dashboard.py            # Web dashboard server
├── visualize.py            # Legacy visualization script (still works)
├── create_demo.py          # Demo data generator
├── requirements.txt        # Python dependencies
├── data/
│   ├── topics.json         # Topic configuration (customizable!)
│   ├── assessments.json    # Current assessments database
│   └── history.json        # Historical log of all changes
├── templates/              # HTML templates for web dashboard
│   ├── dashboard.html      # Main dashboard view
│   └── topic_detail.html   # Topic detail view
├── static/                 # Static assets for web dashboard
│   ├── css/
│   │   └── dashboard.css   # Dashboard styles
│   └── js/
│       └── dashboard.js    # Dashboard interactivity
└── visualizations/         # Generated charts (PNG files)
```

## Data Format

### topics.json
Defines assessment topics (fully customizable):
- Topic key (unique identifier)
- Title and assessment question
- Time horizon (e.g., "3 months", "6 months")
- Key indicators to track

### assessments.json
Stores current state of each assessment:
- Current probability and descriptor
- Confidence level
- Key drivers and uncertainties
- Indicator status
- Last updated date
- Next review date

### history.json
Logs every update with:
- Date of update
- Probability and change from previous
- Key drivers cited
- Notes on what changed

**All files are human-readable JSON** - you can view/edit them directly if needed.

## Example Workflow

### Monday Morning (Week 1)

```bash
$ python3 tracker.py update

======================================================================
WEEKLY ASSESSMENT UPDATE WORKFLOW
======================================================================
Date: 2026-01-13

📋 3 assessment(s) due for review:

   1. Iranian Government Collapse
   2. Venezuela Civil War
   3. Russia-Ukraine Political Agreement

----------------------------------------------------------------------

Update Iranian Government Collapse? (y/n/skip all): y

======================================================================
UPDATE ASSESSMENT: Iranian Government Collapse
======================================================================

Question: What is the likelihood of a collapse of the Iranian government in the next 3 months?
Time Horizon: 3 months

📊 PREVIOUS ASSESSMENT: None (First update)

----------------------------------------------------------------------
PROBABILITY ASSESSMENT
----------------------------------------------------------------------
Current probability (1-100): 15
Confidence level (Low/Medium/High) [default: Medium]: Medium

----------------------------------------------------------------------
KEY DRIVERS (factors increasing likelihood)
----------------------------------------------------------------------
Enter up to 3 key drivers (press Enter to skip):
  Driver 1: Continued economic sanctions impact
  Driver 2: Elite defections increasing
  Driver 3: 

----------------------------------------------------------------------
CRITICAL UNCERTAINTIES (what we don't know)
----------------------------------------------------------------------
Enter up to 3 critical uncertainties (press Enter to skip):
  Uncertainty 1: Supreme Leader health status
  Uncertainty 2: IRGC cohesion under pressure
  Uncertainty 3: 

----------------------------------------------------------------------
INDICATOR STATUS
----------------------------------------------------------------------
Update status for each indicator (🟢 Stable / 🟡 Watch / 🔴 Critical / Enter to skip):
  Supreme Leader health/succession signals [current: Unknown]: 🟡 Watch
  IRGC elite cohesion [current: Unknown]: 🟢 Stable
  Protest frequency and size [current: Unknown]: 🟡 Watch
  Economic conditions (sanctions impact, inflation) [current: Unknown]: 🔴 Critical
  Regional isolation vs support [current: Unknown]: 🟢 Stable

----------------------------------------------------------------------
CHANGE NOTES
----------------------------------------------------------------------
What drove this assessment? (Enter for none): New sanctions package plus reports of elite discontent

✅ Assessment updated successfully!
📅 Next review scheduled: 2026-01-20
```

### Viewing Your Assessment

```bash
$ python3 tracker.py view iranian_collapse

======================================================================
CURRENT ASSESSMENTS
======================================================================

📌 Iranian Government Collapse
   Question: What is the likelihood of a collapse of the Iranian government in the next 3 months?
   Probability: 15% (Unlikely)
   Confidence: Medium
   Last Updated: 2026-01-13
   Next Review: 2026-01-20
   Key Drivers:
      • Continued economic sanctions impact
      • Elite defections increasing
   Indicator Status:
      🟡 Watch Supreme Leader health/succession signals
      🟢 Stable IRGC elite cohesion
      🟡 Watch Protest frequency and size
      🔴 Critical Economic conditions (sanctions impact, inflation)
      🟢 Stable Regional isolation vs support
----------------------------------------------------------------------
```

### Week 2 Update (Showing Change)

```bash
$ python3 tracker.py update iranian_collapse

📊 PREVIOUS ASSESSMENT (Updated: 2026-01-13)
   Probability: 15% (Unlikely)
   Confidence: Medium
   Key Drivers: Continued economic sanctions impact, Elite defections increasing

----------------------------------------------------------------------
PROBABILITY ASSESSMENT
----------------------------------------------------------------------
Current probability (1-100): 20
   ↗ Probability INCREASED by 5%

...
```

### Generating Visualizations

```bash
$ python3 tracker.py visualize

======================================================================
GENERATING VISUALIZATIONS
======================================================================

📊 Creating current snapshot...

📈 Creating individual timelines...
   - Iranian Government Collapse
   - Venezuela Civil War
   - Russia-Ukraine Political Agreement

📊 Creating comparison chart...

✅ All visualizations generated!
📁 Output directory: /path/to/visualizations
```

### Complete Weekly Workflow

```bash
$ python3 tracker.py weekly

Starting weekly workflow...

[Interactive update session for due assessments...]

[Comprehensive report showing risk levels and changes...]

[Automatic visualization generation...]
```

## Tips for Effective Use

### 1. Use the Weekly Command
```bash
python3 tracker.py weekly
```
One command for complete workflow: update → report → visualize

### 2. Set Up Automated Reminders
```bash
# Add to crontab for Monday 9am email reminder
0 9 * * 1 cd /path/to/tracker && python3 tracker.py notify --email-config email_config.json
```

### 3. Check Status Dashboard Regularly
```bash
python3 tracker.py status
```
Shows overdue and due-soon assessments at a glance

### 4. Be Specific with Drivers
- Cite concrete events, not vague trends
- Examples:
  - ✅ "New EU sanctions package announced Jan 10"
  - ❌ "Economic pressure increasing"

### 5. Track Indicator Status Systematically
- 🟢 Stable: No concerning changes
- 🟡 Watch: Something to monitor closely
- 🔴 Critical: Reached concerning threshold

### 6. Document Change Notes
- Explain WHY probability shifted
- This creates institutional memory
- Useful when reviewing past reasoning

### 7. Export Data for Analysis
```bash
# Export to CSV for spreadsheet analysis
python3 tracker.py export --format csv

# Generate markdown report for sharing
python3 tracker.py export --format markdown
```

### 8. Customize for Your Needs
```bash
# Add custom topics beyond the 6 standards
python3 tracker.py add-topic supply_chain_risk
python3 tracker.py add-topic regulatory_change

# List all configured topics
python3 tracker.py list-topics
```

### 9. Review History Before Major Decisions
- Check historical reasoning
- Identify assumption patterns
- See what you got right/wrong

## Integration with Geopolitical Risk Analysis Skill

This tracker complements your geopolitical risk analysis skill:

1. **Use skill for initial deep analysis** - Full 7-step workflow
2. **Use tracker for ongoing monitoring** - Weekly probability updates
3. **Reference history when doing new analysis** - Build on past assessments
4. **Visualizations for presentations** - Professional charts for stakeholders

## Troubleshooting

### "No history data" error
- Run `python3 tracker.py update` first to create initial assessments

### Visualization errors
- Install matplotlib: `pip install matplotlib --break-system-packages`
- Check that data/ directory has assessments.json and history.json

### Can't remember topic names
- Run `python3 tracker.py list-topics` to see all configured topics
- Run `python3 tracker.py view` to see all current assessments
- Use tab completion if your shell supports it

### Want to add custom topics
- Use `python3 tracker.py add-topic <key>` for interactive setup
- Or edit `data/topics.json` directly
- Topics can be for any domain (not just geopolitics!)

### Email notifications not working
- Check your email config JSON file format
- For Gmail, use an App Password (not regular password)
- Verify SMTP server and port settings
- Test with `python3 tracker.py notify --email-config your_config.json`

## Recent Enhancements (v2.0)

✅ **Completed Features:**
- ✅ **Interactive Web Dashboard** - Real-time browser-based interface (NEW!)
- ✅ Custom topic management (add/edit/remove topics)
- ✅ Integrated visualization (no separate script needed)
- ✅ CSV and Markdown export
- ✅ Comprehensive reporting command
- ✅ Status dashboard with overdue tracking
- ✅ Email reminder system
- ✅ Desktop notifications
- ✅ Weekly all-in-one workflow command

## Future Enhancements

Potential additions:
- [ ] PDF report generation (native, not markdown conversion)
- [ ] Automated source collection integration
- [ ] Confidence interval bands on charts
- [ ] Real-time dashboard updates (WebSocket support)
- [ ] User authentication for dashboard
- [ ] Mobile app for quick updates
- [ ] Multi-user collaboration features

## Data Backup

Your assessment history is valuable! Regularly backup:

```bash
# Backup your data
cp -r data/ data-backup-$(date +%Y%m%d)/

# Or use git
git add data/
git commit -m "Assessment update $(date +%Y-%m-%d)"
```

## Support

For issues or questions:
1. Check this README
2. Review the example workflow above
3. Examine the JSON files directly (they're human-readable)
4. Ask Claude for help!

---

**Remember**: This system is only as good as your consistent use. Set that calendar reminder now! ⏰
