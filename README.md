# Automated Weekly Assessment Tracker

A system for maintaining ongoing geopolitical risk assessments with automated weekly updates, historical tracking, and probability timeline visualizations.

## Features

✅ **Track 6 Standard Questions** - Pre-configured for your most common analyses  
✅ **Weekly Update Workflow** - Guided prompts to update assessments  
✅ **Historical Logging** - Every change tracked with timestamps  
✅ **Probability Timelines** - Visual charts showing assessment evolution  
✅ **Indicator Monitoring** - Track status of key indicators (🟢🟡🔴)  
✅ **Change Detection** - Automatic calculation of probability shifts  
✅ **Next Review Scheduling** - Never miss an update  

## Installation

### Prerequisites

```bash
pip install matplotlib --break-system-packages
```

No other dependencies needed - uses Python standard library!

### Setup

1. Place the tracker files in your working directory
2. The system will automatically create necessary directories:
   - `data/` - Stores assessments and history
   - `visualizations/` - Generated charts

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

### View Current Assessments

See all current probability assessments:

```bash
python3 tracker.py view
```

View specific topic:

```bash
python3 tracker.py view iranian_collapse
```

### View Historical Changes

See how your assessment has evolved:

```bash
python3 tracker.py history iranian_collapse
```

This shows:
- All past probability assessments
- Probability changes (↗ increase, ↘ decrease)
- Key drivers for each update
- Notes on what changed

### Update Single Assessment

Update just one topic instead of full weekly workflow:

```bash
python3 tracker.py update iranian_collapse
```

### Generate Visualizations

Create all charts:

```bash
python3 visualize.py
```

This generates:
- **current_snapshot.png** - Bar chart of current probabilities
- **{topic}_timeline.png** - Line chart for each topic showing evolution
- **all_topics_comparison.png** - All topics on one chart

Generate for specific topic only:

```bash
python3 visualize.py --topic iranian_collapse
```

## Standard Questions

The tracker includes these pre-configured questions:

1. **iranian_collapse** - Iranian government collapse (3 months)
2. **venezuela_civil_war** - Venezuela civil war (3 months)
3. **ukraine_agreement** - Russia-Ukraine political agreement (3 months)
4. **taiwan_invasion** - Taiwan invasion by China (6 months)
5. **food_security_crisis** - Global food security crisis (6 months)
6. **greenland_control** - US control of Greenland (6 months)

Each includes pre-defined key indicators to track.

## File Structure

```
assessment-tracker/
├── tracker.py              # Main tracking script
├── visualize.py            # Visualization generator
├── data/
│   ├── assessments.json    # Current assessments database
│   └── history.json        # Historical log of all changes
├── visualizations/         # Generated charts (PNG files)
└── outputs/               # Optional: exported reports
```

## Data Format

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

**Both files are human-readable JSON** - you can view/edit them directly if needed.

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
$ python3 visualize.py

======================================================================
GENERATING VISUALIZATIONS
======================================================================

📊 Creating current snapshot...
✅ Saved snapshot chart: visualizations/current_snapshot.png

📈 Creating individual timelines...
   - iranian_collapse
✅ Saved timeline chart: visualizations/iranian_collapse_timeline.png
   - venezuela_civil_war
✅ Saved timeline chart: visualizations/venezuela_civil_war_timeline.png
   - ukraine_agreement
✅ Saved timeline chart: visualizations/ukraine_agreement_timeline.png

📊 Creating comparison chart...
✅ Saved comparison chart: visualizations/all_topics_comparison.png

✅ All visualizations generated!
📁 Output directory: /path/to/visualizations
```

## Tips for Effective Use

### 1. Consistent Weekly Updates
- Set a recurring calendar reminder (e.g., Monday 9am)
- Budget 15 minutes per week
- Update even if "no change" - this creates valuable time-series data

### 2. Be Specific with Drivers
- Cite concrete events, not vague trends
- Examples:
  - ✅ "New EU sanctions package announced Jan 10"
  - ❌ "Economic pressure increasing"

### 3. Track Indicator Status Systematically
- 🟢 Stable: No concerning changes
- 🟡 Watch: Something to monitor closely
- 🔴 Critical: Reached concerning threshold

### 4. Document Change Notes
- Explain WHY probability shifted
- This creates institutional memory
- Useful when reviewing past reasoning

### 5. Generate Visualizations Regularly
- Run weekly after updates
- Share charts with decision-makers
- Include in reports/presentations

### 6. Review History Before Major Decisions
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
- Run `python3 tracker.py view` to see all available topics
- Use tab completion if your shell supports it

## Future Enhancements

Potential additions:
- [ ] Export to PDF report
- [ ] Email reminders for due reviews
- [ ] Automated source collection integration
- [ ] Confidence interval bands on charts
- [ ] Custom questions beyond the 6 standard ones
- [ ] Dashboard web interface

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
