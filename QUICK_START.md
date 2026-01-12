# 🚀 Quick Start Guide - Assessment Tracker

## What You Just Received

The **Automated Weekly Assessment Tracker** - Tool #1 from your workflow improvement plan!

This system solves your biggest pain points:
- ✅ No more memory reliance for tracking assessments
- ✅ Systematic logging of probability changes over time
- ✅ Visual timeline showing how your thinking has evolved
- ✅ 15 minutes/week vs 1-2 hours manual tracking

## Files Included

```
assessment-tracker/
├── tracker.py              # Main tracking script ⭐
├── visualize.py            # Chart generator ⭐
├── create_demo.py          # Demo data generator
├── README.md               # Comprehensive documentation
├── data/
│   ├── assessments.json    # Current assessments (pre-loaded with demo)
│   └── history.json        # Historical log (pre-loaded with demo)
└── visualizations/         # Sample charts (already generated!)
    ├── current_snapshot.png
    ├── iranian_collapse_timeline.png
    ├── ukraine_agreement_timeline.png
    ├── taiwan_invasion_timeline.png
    └── all_topics_comparison.png
```

## Try It Now (5 Minutes)

### 1. View Demo Data

```bash
cd assessment-tracker
python3 tracker.py view
```

You'll see 3 topics with full assessments (Iranian collapse, Ukraine agreement, Taiwan invasion) and 3 empty ones.

### 2. Check History

```bash
python3 tracker.py history iranian_collapse
```

This shows 4 weeks of historical data with probability changes (12% → 15% → 18% → 20%).

### 3. Look at Visualizations

Open the `visualizations/` folder. You'll see:
- **current_snapshot.png** - Bar chart of current probabilities
- **iranian_collapse_timeline.png** - Line chart showing the upward trend
- **all_topics_comparison.png** - All 3 topics on one chart

These are what you'll generate weekly!

### 4. Try Your First Update (Optional)

```bash
python3 tracker.py update iranian_collapse
```

This walks you through updating the Iranian collapse assessment. Try entering:
- Probability: 22 (it will show ↗ +2% from 20%)
- Confidence: Medium
- Add a new driver
- Update indicator status

## Real-World Usage

### Monday Morning Routine (Recommended)

**Time: 15 minutes**

1. **Run weekly update:**
   ```bash
   python3 tracker.py update
   ```

2. The system shows which assessments need review and walks you through each

3. **Generate visualizations:**
   ```bash
   python3 visualize.py
   ```

4. **Share with stakeholders:**
   - Attach charts to weekly email
   - Include in reports/presentations
   - Post to internal dashboards

### When You Need It

**Before starting new analysis:**
```bash
python3 tracker.py history [topic]
```
Review past reasoning before diving deep.

**For presentations:**
```bash
python3 visualize.py
```
Generate fresh charts with latest data.

**Quick status check:**
```bash
python3 tracker.py view
```
See all current assessments at a glance.

## Resetting for Real Use

When you're ready to start tracking your actual assessments:

```bash
# Backup demo data (optional)
mv data data-demo-backup

# System will auto-create fresh data/ on next run
python3 tracker.py update
```

Or keep the demo data and just start adding your own updates!

## Installation (First Time Only)

```bash
pip install matplotlib --break-system-packages
```

That's it! Everything else is Python standard library.

## Key Benefits Recap

| Before | After |
|--------|-------|
| Memory-based tracking | Systematic database |
| No historical record | Complete audit trail |
| Manual trend analysis | Automated visualizations |
| 1-2 hours/week | 15 minutes/week |
| Scattered notes | Centralized system |

## Next Steps

1. **This week:** Play with demo data, get comfortable with commands
2. **Next week:** Start your first real update
3. **Week 3:** Review your first historical trend
4. **Week 4:** Share visualizations with stakeholders

**After 4 weeks, you'll have:**
- 4 data points per topic (trending analysis!)
- Professional charts showing evolution
- Documented reasoning for every change
- Time saved: 3-6 hours

## Getting Help

- **Full documentation:** Read `README.md`
- **Command help:** `python3 tracker.py -h`
- **Issues:** Ask Claude!

## What's Next?

After you've used this for a few weeks, we can build:
- **Tool #2:** Dynamic Source Collection Dashboard (saves 30-45 min/day)
- **Tool #3:** One-Click Dashboard Generator (leverages this tracker's data!)

But start here first. Master Tool #1 and you'll immediately feel the efficiency gains.

---

**🎯 Action Item:** Set a calendar reminder right now for next Monday 9am: "Weekly Assessment Update"
