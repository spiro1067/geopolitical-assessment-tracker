#!/usr/bin/env python3
"""
Automated Weekly Assessment Tracker

Maintains ongoing probability assessments for customizable topics,
tracks changes over time, and generates visualizations of probability evolution.

Core Commands:
    python3 tracker.py update [topic]       # Update assessments (interactive workflow)
    python3 tracker.py view [topic]         # View current assessments
    python3 tracker.py history <topic>      # View historical changes for a topic
    python3 tracker.py status               # Show overdue/due-soon assessments
    python3 tracker.py weekly               # Complete weekly workflow (update + report + visualize)

Visualization & Reporting:
    python3 tracker.py visualize [topic]    # Generate probability timeline charts
    python3 tracker.py report               # Generate comprehensive summary report
    python3 tracker.py export --format csv  # Export data to CSV
    python3 tracker.py export --format markdown  # Export to Markdown report

Topic Management:
    python3 tracker.py list-topics          # List all configured topics
    python3 tracker.py add-topic <key>      # Add a new custom topic
    python3 tracker.py edit-topic <key>     # Edit an existing topic
    python3 tracker.py remove-topic <key>   # Remove a topic (with confirmation)

Notifications:
    python3 tracker.py notify               # Send desktop notification for overdue items
    python3 tracker.py notify --email-config config.json  # Send email reminder
    python3 tracker.py status --check-overdue  # Check and notify for overdue assessments

Web Dashboard:
    python3 tracker.py dashboard            # Start interactive web dashboard (default: http://127.0.0.1:5000)
    python3 tracker.py dashboard --port 8080 --host 0.0.0.0  # Custom port and host
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys
import csv
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Visualization imports (conditional - only needed for visualize command)
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Standard questions configuration
STANDARD_QUESTIONS = {
    "iranian_collapse": {
        "title": "Iranian Government Collapse",
        "question": "What is the likelihood of a collapse of the Iranian government in the next 3 months?",
        "horizon": "3 months",
        "key_indicators": [
            "Supreme Leader health/succession signals",
            "IRGC elite cohesion",
            "Protest frequency and size",
            "Economic conditions (sanctions impact, inflation)",
            "Regional isolation vs support"
        ]
    },
    "venezuela_civil_war": {
        "title": "Venezuela Civil War",
        "question": "What is the likelihood of civil war in Venezuela in the next 3 months?",
        "horizon": "3 months",
        "key_indicators": [
            "Military loyalty/fragmentation",
            "Opposition unity and capability",
            "Economic collapse severity",
            "External support (US, China, Russia)",
            "Humanitarian crisis scale"
        ]
    },
    "ukraine_agreement": {
        "title": "Russia-Ukraine Political Agreement",
        "question": "What is the likelihood of a durable political agreement in the Russian-Ukraine war in the next 3 months?",
        "horizon": "3 months",
        "key_indicators": [
            "Battlefield momentum",
            "Western military/financial support",
            "Russian domestic politics",
            "Ukrainian position (maximalist vs realist)",
            "Third-party mediation efforts"
        ]
    },
    "taiwan_invasion": {
        "title": "Taiwan Invasion",
        "question": "What is the likelihood of an invasion of Taiwan by China in the next 6 months?",
        "horizon": "6 months",
        "key_indicators": [
            "PLA readiness signals",
            "US commitment credibility",
            "CCP internal politics",
            "Taiwan domestic politics",
            "Economic costs assessment"
        ]
    },
    "food_security_crisis": {
        "title": "Global Food Security Crisis",
        "question": "What is the likelihood of two major agricultural regions facing harvest reduction due to extreme weather within 6 months?",
        "horizon": "6 months",
        "key_indicators": [
            "Climate event probability (ENSO, droughts)",
            "Key agricultural region status",
            "Existing food security stress",
            "Conflict disruption to agriculture",
            "Export restrictions/protectionism"
        ]
    },
    "greenland_control": {
        "title": "US Control of Greenland",
        "question": "What is the likelihood of the United States obtaining de facto political control of Greenland in the next 6 months?",
        "horizon": "6 months",
        "key_indicators": [
            "Trump administration policy signals",
            "Danish government response",
            "Greenlandic domestic politics",
            "NATO dynamics",
            "Chinese/Russian Arctic activity"
        ]
    }
}

PROBABILITY_DESCRIPTORS = {
    (1, 10): "Remote/Highly Unlikely",
    (10, 30): "Unlikely",
    (30, 70): "Roughly Even Chance",
    (70, 90): "Likely/Probable",
    (90, 99): "Highly Likely/Almost Certain",
    (99, 100): "Certain"
}


class AssessmentTracker:
    """Manages geopolitical risk assessments and historical tracking."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_file = self.data_dir / "assessments.json"
        self.history_file = self.data_dir / "history.json"
        self.topics_file = self.data_dir / "topics.json"
        self.load_topics()
        self.load_data()
    
    def load_topics(self):
        """Load topics configuration from topics.json."""
        if self.topics_file.exists():
            with open(self.topics_file, 'r') as f:
                self.topics = json.load(f)
        else:
            # Use hardcoded defaults if topics.json doesn't exist
            self.topics = STANDARD_QUESTIONS
            # Save to topics.json for future use
            self.save_topics()

    def save_topics(self):
        """Save topics configuration to topics.json."""
        with open(self.topics_file, 'w') as f:
            json.dump(self.topics, f, indent=2)

    def load_data(self):
        """Load assessment database and history."""
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                self.assessments = json.load(f)
        else:
            self.assessments = self._initialize_assessments()

        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {key: [] for key in self.topics.keys()}
    
    def _initialize_assessments(self) -> Dict:
        """Initialize assessment database with configured topics."""
        assessments = {}
        for key, config in self.topics.items():
            assessments[key] = {
                "title": config["title"],
                "question": config["question"],
                "horizon": config["horizon"],
                "current_probability": None,
                "current_descriptor": None,
                "confidence": None,
                "key_drivers": [],
                "key_uncertainties": [],
                "indicator_status": {ind: "Unknown" for ind in config.get("key_indicators", [])},
                "last_updated": None,
                "next_review": None,
                "notes": ""
            }
        return assessments
    
    def save_data(self):
        """Save assessment database and history."""
        with open(self.db_file, 'w') as f:
            json.dump(self.assessments, f, indent=2)
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_descriptor(self, probability: int) -> str:
        """Get qualitative descriptor for probability percentage."""
        for (low, high), descriptor in PROBABILITY_DESCRIPTORS.items():
            if low <= probability < high:
                return descriptor
        return "Certain"
    
    def update_assessment(self, topic: str):
        """Interactive update workflow for a single assessment."""
        if topic not in self.assessments:
            print(f"Error: Unknown topic '{topic}'")
            print(f"Available topics: {', '.join(self.assessments.keys())}")
            return

        assessment = self.assessments[topic]
        config = self.topics[topic]
        
        print("\n" + "="*70)
        print(f"UPDATE ASSESSMENT: {assessment['title']}")
        print("="*70)
        print(f"\nQuestion: {assessment['question']}")
        print(f"Time Horizon: {assessment['horizon']}")
        
        # Show previous assessment
        if assessment['last_updated']:
            print(f"\n📊 PREVIOUS ASSESSMENT (Updated: {assessment['last_updated']})")
            print(f"   Probability: {assessment['current_probability']}% ({assessment['current_descriptor']})")
            print(f"   Confidence: {assessment['confidence']}")
            if assessment['key_drivers']:
                print(f"   Key Drivers: {', '.join(assessment['key_drivers'][:3])}")
        else:
            print("\n📊 PREVIOUS ASSESSMENT: None (First update)")
        
        # Interactive updates
        print("\n" + "-"*70)
        print("PROBABILITY ASSESSMENT")
        print("-"*70)
        
        while True:
            try:
                prob_input = input(f"Current probability (1-100): ").strip()
                if not prob_input:
                    print("Keeping previous assessment unchanged.")
                    return
                
                probability = int(prob_input)
                if 1 <= probability <= 100:
                    break
                print("Please enter a number between 1 and 100")
            except ValueError:
                print("Please enter a valid number")
        
        descriptor = self.get_descriptor(probability)
        
        confidence = input(f"Confidence level (Low/Medium/High) [default: Medium]: ").strip() or "Medium"
        
        # Track probability change
        prob_change = None
        if assessment['current_probability'] is not None:
            prob_change = probability - assessment['current_probability']
            if prob_change > 0:
                print(f"   ↗ Probability INCREASED by {prob_change}%")
            elif prob_change < 0:
                print(f"   ↘ Probability DECREASED by {abs(prob_change)}%")
            else:
                print(f"   → Probability UNCHANGED")
        
        # Key drivers
        print("\n" + "-"*70)
        print("KEY DRIVERS (factors increasing likelihood)")
        print("-"*70)
        print("Enter up to 3 key drivers (press Enter to skip):")
        
        drivers = []
        for i in range(3):
            driver = input(f"  Driver {i+1}: ").strip()
            if driver:
                drivers.append(driver)
            else:
                break
        
        # Key uncertainties
        print("\n" + "-"*70)
        print("CRITICAL UNCERTAINTIES (what we don't know)")
        print("-"*70)
        print("Enter up to 3 critical uncertainties (press Enter to skip):")
        
        uncertainties = []
        for i in range(3):
            uncertainty = input(f"  Uncertainty {i+1}: ").strip()
            if uncertainty:
                uncertainties.append(uncertainty)
            else:
                break


        # Indicator status
        print("\n" + "-"*70)
        print("INDICATOR STATUS")
        print("-"*70)
        print("Update status for each indicator (🟢 Stable / 🟡 Watch / 🔴 Critical / Enter to skip):")

        indicator_status = {}
        for indicator in config.get('key_indicators', []):
            current = assessment['indicator_status'].get(indicator, "Unknown")
            status = input(f"  {indicator} [current: {current}]: ").strip() or current
            indicator_status[indicator] = status
        
        # Notes on what changed
        print("\n" + "-"*70)
        print("CHANGE NOTES")
        print("-"*70)
        notes = input("What drove this assessment? (Enter for none): ").strip()
        
        # Save to history
        history_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "probability": probability,
            "descriptor": descriptor,
            "confidence": confidence,
            "change": prob_change,
            "drivers": drivers,
            "uncertainties": uncertainties,
            "notes": notes
        }
        self.history[topic].append(history_entry)
        
        # Update current assessment
        assessment['current_probability'] = probability
        assessment['current_descriptor'] = descriptor
        assessment['confidence'] = confidence
        assessment['key_drivers'] = drivers
        assessment['key_uncertainties'] = uncertainties
        assessment['indicator_status'] = indicator_status
        assessment['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        assessment['notes'] = notes
        
        # Calculate next review date based on horizon
        if "3 months" in assessment['horizon']:
            next_review = datetime.now() + timedelta(days=7)  # Weekly for 3-month horizon
        else:
            next_review = datetime.now() + timedelta(days=14)  # Bi-weekly for 6-month horizon
        assessment['next_review'] = next_review.strftime("%Y-%m-%d")
        
        self.save_data()
        
        print("\n✅ Assessment updated successfully!")
        print(f"📅 Next review scheduled: {assessment['next_review']}")
    
    def view_current(self, topic: Optional[str] = None):
        """View current assessments."""
        if topic:
            if topic not in self.assessments:
                print(f"Error: Unknown topic '{topic}'")
                return
            topics = [topic]
        else:
            topics = self.assessments.keys()
        
        print("\n" + "="*70)
        print("CURRENT ASSESSMENTS")
        print("="*70)
        
        for key in topics:
            assessment = self.assessments[key]
            print(f"\n📌 {assessment['title']}")
            print(f"   Question: {assessment['question']}")
            
            if assessment['current_probability'] is not None:
                print(f"   Probability: {assessment['current_probability']}% ({assessment['current_descriptor']})")
                print(f"   Confidence: {assessment['confidence']}")
                print(f"   Last Updated: {assessment['last_updated']}")
                print(f"   Next Review: {assessment['next_review']}")
                
                if assessment['key_drivers']:
                    print(f"   Key Drivers:")
                    for driver in assessment['key_drivers']:
                        print(f"      • {driver}")
                
                if assessment['indicator_status']:
                    print(f"   Indicator Status:")
                    for ind, status in assessment['indicator_status'].items():
                        print(f"      {status} {ind}")
            else:
                print(f"   Status: Not yet assessed")
            
            print("-"*70)
    
    def view_history(self, topic: str):
        """View historical changes for a topic."""
        if topic not in self.history:
            print(f"Error: Unknown topic '{topic}'")
            return
        
        history = self.history[topic]
        if not history:
            print(f"No history available for {topic}")
            return
        
        print("\n" + "="*70)
        print(f"ASSESSMENT HISTORY: {self.topics[topic]['title']}")
        print("="*70)
        
        for i, entry in enumerate(history, 1):
            print(f"\n#{i} - {entry['date']}")
            print(f"   Probability: {entry['probability']}% ({entry['descriptor']})")
            print(f"   Confidence: {entry['confidence']}")
            
            if entry.get('change') is not None:
                if entry['change'] > 0:
                    print(f"   Change: ↗ +{entry['change']}%")
                elif entry['change'] < 0:
                    print(f"   Change: ↘ {entry['change']}%")
                else:
                    print(f"   Change: → No change")
            
            if entry.get('drivers'):
                print(f"   Drivers: {', '.join(entry['drivers'])}")
            
            if entry.get('notes'):
                print(f"   Notes: {entry['notes']}")
            
            print("-"*70)
    
    def weekly_update_workflow(self):
        """Run through all assessments for weekly update."""
        print("\n" + "="*70)
        print("WEEKLY ASSESSMENT UPDATE WORKFLOW")
        print("="*70)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
        
        # Determine which assessments need review
        today = datetime.now().date()
        topics_to_review = []
        
        for key, assessment in self.assessments.items():
            if assessment['next_review']:
                next_review = datetime.strptime(assessment['next_review'], "%Y-%m-%d").date()
                if next_review <= today:
                    topics_to_review.append(key)
            else:
                # Never reviewed before
                topics_to_review.append(key)
        
        if not topics_to_review:
            print("✅ No assessments due for review this week!")
            print("\nCurrent assessments:")
            self.view_current()
            return
        
        print(f"📋 {len(topics_to_review)} assessment(s) due for review:\n")
        for i, key in enumerate(topics_to_review, 1):
            title = self.topics[key]['title']
            print(f"   {i}. {title}")

        print("\n" + "-"*70)

        for key in topics_to_review:
            proceed = input(f"\nUpdate {self.topics[key]['title']}? (y/n/skip all): ").strip().lower()

            if proceed == 'skip all':
                print("Skipping remaining assessments.")
                break
            elif proceed == 'y':
                self.update_assessment(key)
            else:
                print(f"Skipped {self.topics[key]['title']}")
        
        print("\n✅ Weekly update workflow complete!")

    def add_topic(self, topic_key: str):
        """Interactive workflow to add a new topic."""
        if topic_key in self.topics:
            print(f"Error: Topic '{topic_key}' already exists. Use 'edit-topic' to modify it.")
            return

        print("\n" + "="*70)
        print("ADD NEW TOPIC")
        print("="*70)
        print(f"Topic Key: {topic_key}\n")

        title = input("Title (e.g., 'Iranian Government Collapse'): ").strip()
        if not title:
            print("Error: Title is required")
            return

        question = input("Assessment Question: ").strip()
        if not question:
            print("Error: Question is required")
            return

        horizon = input("Time Horizon (e.g., '3 months', '6 months', '1 year'): ").strip()
        if not horizon:
            horizon = "3 months"

        print("\nEnter key indicators to track (press Enter on empty line to finish):")
        indicators = []
        i = 1
        while True:
            indicator = input(f"  Indicator {i}: ").strip()
            if not indicator:
                break
            indicators.append(indicator)
            i += 1

        # Add topic to configuration
        self.topics[topic_key] = {
            "title": title,
            "question": question,
            "horizon": horizon,
            "key_indicators": indicators
        }

        # Initialize assessment for this topic
        self.assessments[topic_key] = {
            "title": title,
            "question": question,
            "horizon": horizon,
            "current_probability": None,
            "current_descriptor": None,
            "confidence": None,
            "key_drivers": [],
            "key_uncertainties": [],
            "indicator_status": {ind: "Unknown" for ind in indicators},
            "last_updated": None,
            "next_review": None,
            "notes": ""
        }

        # Initialize history for this topic
        self.history[topic_key] = []

        # Save everything
        self.save_topics()
        self.save_data()

        print(f"\n✅ Topic '{topic_key}' added successfully!")
        print(f"   Title: {title}")
        print(f"   Horizon: {horizon}")
        print(f"   Indicators: {len(indicators)}")

    def edit_topic(self, topic_key: str):
        """Interactive workflow to edit an existing topic."""
        if topic_key not in self.topics:
            print(f"Error: Topic '{topic_key}' not found")
            print(f"Available topics: {', '.join(self.topics.keys())}")
            return

        topic = self.topics[topic_key]

        print("\n" + "="*70)
        print(f"EDIT TOPIC: {topic['title']}")
        print("="*70)
        print("Press Enter to keep current value\n")

        title = input(f"Title [{topic['title']}]: ").strip() or topic['title']
        question = input(f"Question [{topic['question']}]: ").strip() or topic['question']
        horizon = input(f"Horizon [{topic['horizon']}]: ").strip() or topic['horizon']

        print(f"\nCurrent indicators:")
        for i, ind in enumerate(topic.get('key_indicators', []), 1):
            print(f"  {i}. {ind}")

        edit_indicators = input("\nEdit indicators? (y/n) [n]: ").strip().lower()
        if edit_indicators == 'y':
            print("Enter new indicators (press Enter on empty line to finish):")
            indicators = []
            i = 1
            while True:
                indicator = input(f"  Indicator {i}: ").strip()
                if not indicator:
                    break
                indicators.append(indicator)
                i += 1
        else:
            indicators = topic.get('key_indicators', [])

        # Update topic
        self.topics[topic_key] = {
            "title": title,
            "question": question,
            "horizon": horizon,
            "key_indicators": indicators
        }

        # Update assessment if it exists
        if topic_key in self.assessments:
            self.assessments[topic_key]['title'] = title
            self.assessments[topic_key]['question'] = question
            self.assessments[topic_key]['horizon'] = horizon
            # Update indicator status, preserving existing values
            old_status = self.assessments[topic_key].get('indicator_status', {})
            new_status = {}
            for ind in indicators:
                new_status[ind] = old_status.get(ind, "Unknown")
            self.assessments[topic_key]['indicator_status'] = new_status

        self.save_topics()
        self.save_data()

        print(f"\n✅ Topic '{topic_key}' updated successfully!")

    def remove_topic(self, topic_key: str):
        """Remove a topic (with confirmation)."""
        if topic_key not in self.topics:
            print(f"Error: Topic '{topic_key}' not found")
            return

        topic = self.topics[topic_key]

        print("\n" + "="*70)
        print(f"REMOVE TOPIC: {topic['title']}")
        print("="*70)

        # Check if there's assessment data
        has_data = (topic_key in self.assessments and
                   self.assessments[topic_key].get('current_probability') is not None)

        if has_data:
            print(f"⚠️  WARNING: This topic has assessment data that will be deleted!")
            history_count = len(self.history.get(topic_key, []))
            print(f"   • {history_count} historical entries")
            print(f"   • Current probability: {self.assessments[topic_key]['current_probability']}%")

        confirm = input(f"\nType 'DELETE' to confirm removal: ").strip()

        if confirm == 'DELETE':
            # Remove from all data structures
            del self.topics[topic_key]
            if topic_key in self.assessments:
                del self.assessments[topic_key]
            if topic_key in self.history:
                del self.history[topic_key]

            self.save_topics()
            self.save_data()

            print(f"\n✅ Topic '{topic_key}' removed successfully!")
        else:
            print("\n❌ Removal cancelled")

    def list_topics(self):
        """List all configured topics."""
        print("\n" + "="*70)
        print("CONFIGURED TOPICS")
        print("="*70 + "\n")

        for key, config in self.topics.items():
            assessed = "✓" if self.assessments.get(key, {}).get('current_probability') is not None else "○"
            print(f"{assessed} {key}")
            print(f"   Title: {config['title']}")
            print(f"   Horizon: {config['horizon']}")
            print(f"   Indicators: {len(config.get('key_indicators', []))}")
            if key in self.history and self.history[key]:
                print(f"   History Entries: {len(self.history[key])}")
            print()

        print(f"Total Topics: {len(self.topics)}")
        print("Legend: ✓ = assessed, ○ = not yet assessed\n")

    def get_overdue_assessments(self) -> List[Dict]:
        """Get list of assessments that are overdue for review."""
        today = datetime.now().date()
        overdue = []
        due_soon = []

        for key, assessment in self.assessments.items():
            if assessment['next_review']:
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
            else:
                # Never reviewed before
                overdue.append({
                    'key': key,
                    'title': assessment['title'],
                    'days_overdue': None,
                    'next_review': 'Never'
                })

        return overdue, due_soon

    def show_status(self):
        """Show status of all assessments including overdue tracking."""
        overdue, due_soon = self.get_overdue_assessments()

        print("\n" + "="*70)
        print("ASSESSMENT STATUS")
        print("="*70)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")

        if overdue:
            print("🔴 OVERDUE ASSESSMENTS:")
            for item in overdue:
                if item['days_overdue'] is None:
                    print(f"   • {item['title']} - Never assessed")
                else:
                    print(f"   • {item['title']} - {item['days_overdue']} days overdue (due: {item['next_review']})")
            print()

        if due_soon:
            print("🟡 DUE SOON (within 3 days):")
            for item in due_soon:
                print(f"   • {item['title']} - Due in {item['days_until']} days ({item['next_review']})")
            print()

        if not overdue and not due_soon:
            print("✅ All assessments are up to date!\n")

        # Show current probabilities
        print("-"*70)
        print("CURRENT PROBABILITIES:")
        print("-"*70)
        for key, assessment in self.assessments.items():
            if assessment['current_probability'] is not None:
                print(f"   {assessment['title']}: {assessment['current_probability']}% ({assessment['current_descriptor']})")
            else:
                print(f"   {assessment['title']}: Not yet assessed")
        print()

    def send_email_reminder(self, config: Dict):
        """Send email reminder for overdue assessments."""
        overdue, due_soon = self.get_overdue_assessments()

        if not overdue and not due_soon:
            return

        # Build email content
        subject = f"Assessment Tracker Reminder - {len(overdue)} Overdue"

        body = f"Assessment Status Report - {datetime.now().strftime('%Y-%m-%d')}\n\n"

        if overdue:
            body += "OVERDUE ASSESSMENTS:\n"
            for item in overdue:
                if item['days_overdue'] is None:
                    body += f"  • {item['title']} - Never assessed\n"
                else:
                    body += f"  • {item['title']} - {item['days_overdue']} days overdue\n"
            body += "\n"

        if due_soon:
            body += "DUE SOON:\n"
            for item in due_soon:
                body += f"  • {item['title']} - Due in {item['days_until']} days\n"
            body += "\n"

        body += f"\nRun 'python3 tracker.py update' to complete your assessments.\n"

        # Send email
        try:
            msg = MIMEMultipart()
            msg['From'] = config['from_email']
            msg['To'] = config['to_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['smtp_user'], config['smtp_password'])
                server.send_message(msg)

            print(f"✅ Email reminder sent to {config['to_email']}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    def send_desktop_notification(self):
        """Send desktop notification for overdue assessments."""
        overdue, due_soon = self.get_overdue_assessments()

        if not overdue and not due_soon:
            return

        count = len(overdue) + len(due_soon)
        message = f"{len(overdue)} overdue, {len(due_soon)} due soon"

        try:
            # Try notify-send (Linux)
            subprocess.run([
                'notify-send',
                'Assessment Tracker',
                f'{count} assessments need review: {message}'
            ], check=False)
        except FileNotFoundError:
            # notify-send not available
            pass

    def export_to_csv(self, output_file: str):
        """Export assessment history to CSV format."""
        output_path = Path(output_file)

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Topic', 'Title', 'Date', 'Probability', 'Descriptor',
                           'Confidence', 'Change', 'Drivers', 'Uncertainties', 'Notes'])

            for topic_key, history in self.history.items():
                title = self.assessments.get(topic_key, {}).get('title', topic_key)
                for entry in history:
                    writer.writerow([
                        topic_key,
                        title,
                        entry['date'],
                        entry['probability'],
                        entry['descriptor'],
                        entry['confidence'],
                        entry.get('change', ''),
                        '; '.join(entry.get('drivers', [])),
                        '; '.join(entry.get('uncertainties', [])),
                        entry.get('notes', '')
                    ])

        print(f"✅ Exported to CSV: {output_path.absolute()}")

    def export_to_markdown(self, output_file: str):
        """Export current assessments and history to Markdown."""
        output_path = Path(output_file)

        with open(output_path, 'w') as f:
            f.write(f"# Assessment Tracker Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Current Assessments\n\n")
            for key, assessment in self.assessments.items():
                f.write(f"### {assessment['title']}\n\n")
                f.write(f"**Question:** {assessment['question']}\n\n")
                f.write(f"**Time Horizon:** {assessment['horizon']}\n\n")

                if assessment['current_probability'] is not None:
                    f.write(f"**Current Probability:** {assessment['current_probability']}% ({assessment['current_descriptor']})\n\n")
                    f.write(f"**Confidence:** {assessment['confidence']}\n\n")
                    f.write(f"**Last Updated:** {assessment['last_updated']}\n\n")
                    f.write(f"**Next Review:** {assessment['next_review']}\n\n")

                    if assessment['key_drivers']:
                        f.write("**Key Drivers:**\n")
                        for driver in assessment['key_drivers']:
                            f.write(f"- {driver}\n")
                        f.write("\n")

                    if assessment['key_uncertainties']:
                        f.write("**Critical Uncertainties:**\n")
                        for uncertainty in assessment['key_uncertainties']:
                            f.write(f"- {uncertainty}\n")
                        f.write("\n")

                    if assessment['notes']:
                        f.write(f"**Notes:** {assessment['notes']}\n\n")
                else:
                    f.write("**Status:** Not yet assessed\n\n")

                f.write("---\n\n")

            f.write("## Assessment History\n\n")
            for topic_key, history in self.history.items():
                if history:
                    title = self.assessments.get(topic_key, {}).get('title', topic_key)
                    f.write(f"### {title}\n\n")

                    for i, entry in enumerate(history, 1):
                        f.write(f"#### Update #{i} - {entry['date']}\n\n")
                        f.write(f"- **Probability:** {entry['probability']}% ({entry['descriptor']})\n")
                        f.write(f"- **Confidence:** {entry['confidence']}\n")

                        if entry.get('change') is not None:
                            change_symbol = "↗" if entry['change'] > 0 else "↘" if entry['change'] < 0 else "→"
                            f.write(f"- **Change:** {change_symbol} {entry['change']:+d}%\n")

                        if entry.get('drivers'):
                            f.write(f"- **Drivers:** {', '.join(entry['drivers'])}\n")

                        if entry.get('uncertainties'):
                            f.write(f"- **Uncertainties:** {', '.join(entry['uncertainties'])}\n")

                        if entry.get('notes'):
                            f.write(f"- **Notes:** {entry['notes']}\n")

                        f.write("\n")

                    f.write("---\n\n")

        print(f"✅ Exported to Markdown: {output_path.absolute()}")

    def generate_report(self):
        """Generate a comprehensive summary report."""
        print("\n" + "="*70)
        print("WEEKLY ASSESSMENT REPORT")
        print("="*70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Status overview
        overdue, due_soon = self.get_overdue_assessments()
        print("📊 STATUS OVERVIEW:")
        print(f"   Total Topics: {len(self.assessments)}")
        assessed_count = sum(1 for a in self.assessments.values() if a['current_probability'] is not None)
        print(f"   Assessed: {assessed_count}/{len(self.assessments)}")
        print(f"   Overdue: {len(overdue)}")
        print(f"   Due Soon: {len(due_soon)}\n")

        # Current probabilities summary
        print("-"*70)
        print("CURRENT RISK LEVELS:")
        print("-"*70)

        # Group by risk level
        risk_levels = {
            'Critical (70%+)': [],
            'Elevated (30-70%)': [],
            'Low (<30%)': [],
            'Not Assessed': []
        }

        for key, assessment in self.assessments.items():
            if assessment['current_probability'] is not None:
                prob = assessment['current_probability']
                if prob >= 70:
                    risk_levels['Critical (70%+)'].append((assessment['title'], prob, assessment['confidence']))
                elif prob >= 30:
                    risk_levels['Elevated (30-70%)'].append((assessment['title'], prob, assessment['confidence']))
                else:
                    risk_levels['Low (<30%)'].append((assessment['title'], prob, assessment['confidence']))
            else:
                risk_levels['Not Assessed'].append((assessment['title'], None, None))

        for level, items in risk_levels.items():
            if items:
                print(f"\n{level}:")
                for title, prob, conf in items:
                    if prob is not None:
                        print(f"   • {title}: {prob}% (Confidence: {conf})")
                    else:
                        print(f"   • {title}")

        # Recent changes
        print("\n" + "-"*70)
        print("SIGNIFICANT RECENT CHANGES:")
        print("-"*70)

        changes_found = False
        for topic_key, history in self.history.items():
            if history and len(history) >= 2:
                latest = history[-1]
                if latest.get('change') and abs(latest['change']) >= 5:
                    title = self.assessments[topic_key]['title']
                    symbol = "↗" if latest['change'] > 0 else "↘"
                    print(f"   {symbol} {title}: {latest['change']:+d}% on {latest['date']}")
                    if latest.get('notes'):
                        print(f"      Reason: {latest['notes']}")
                    changes_found = True

        if not changes_found:
            print("   No significant changes (±5% or more) in recent updates\n")

        print("\n" + "="*70)

    def visualize(self, topic: Optional[str] = None, output_dir: str = "./visualizations"):
        """Generate visualizations for assessments."""
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib is required for visualization.")
            print("Install it with: pip install matplotlib --break-system-packages")
            return

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if topic:
            # Single topic visualization
            if topic not in self.history or not self.history[topic]:
                print(f"No history data for {topic}")
                return

            self._plot_single_timeline(topic, output_path)
        else:
            # Generate all visualizations
            print("\n" + "="*70)
            print("GENERATING VISUALIZATIONS")
            print("="*70 + "\n")

            # Current snapshot
            print("📊 Creating current snapshot...")
            self._plot_current_snapshot(output_path)

            # Individual timelines
            print("\n📈 Creating individual timelines...")
            topics_with_data = [k for k, v in self.history.items() if v]
            for t in topics_with_data:
                print(f"   - {self.assessments[t]['title']}")
                self._plot_single_timeline(t, output_path)

            # Comparison chart
            if len(topics_with_data) > 1:
                print("\n📊 Creating comparison chart...")
                self._plot_all_topics_comparison(output_path)

            print("\n✅ All visualizations generated!")
            print(f"📁 Output directory: {output_path.absolute()}")

    def _plot_single_timeline(self, topic: str, output_dir: Path):
        """Create timeline chart for a single topic."""
        history = self.history[topic]
        dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in history]
        probabilities = [entry['probability'] for entry in history]

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(dates, probabilities, marker='o', linewidth=2, markersize=8,
                color='#2E86AB', label='Probability Assessment')

        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Probability (%)', fontsize=12, fontweight='bold')

        title = self.assessments.get(topic, {}).get('title', topic)
        ax.set_title(f'Probability Assessment Timeline: {title}',
                    fontsize=14, fontweight='bold', pad=20)

        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 100)

        # Add probability zones
        ax.axhspan(0, 10, alpha=0.1, color='green', label='Remote')
        ax.axhspan(10, 30, alpha=0.1, color='yellow', label='Unlikely')
        ax.axhspan(30, 70, alpha=0.1, color='orange', label='Even Chance')
        ax.axhspan(70, 90, alpha=0.1, color='red', label='Likely')
        ax.axhspan(90, 100, alpha=0.1, color='darkred', label='Highly Likely')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45, ha='right')

        ax.legend(loc='upper left', fontsize=9)

        plt.tight_layout()

        output_file = output_dir / f"{topic}_timeline.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_current_snapshot(self, output_dir: Path):
        """Create bar chart of current probabilities."""
        topics_with_current = {k: v for k, v in self.assessments.items()
                              if v.get('current_probability') is not None}

        if not topics_with_current:
            print("No current assessments available")
            return

        titles = [v['title'] for v in topics_with_current.values()]
        probabilities = [v['current_probability'] for v in topics_with_current.values()]
        confidences = [v.get('confidence', 'Unknown') for v in topics_with_current.values()]

        colors = []
        for prob in probabilities:
            if prob < 10:
                colors.append('#2ECC71')
            elif prob < 30:
                colors.append('#F39C12')
            elif prob < 70:
                colors.append('#E67E22')
            elif prob < 90:
                colors.append('#E74C3C')
            else:
                colors.append('#C0392B')

        fig, ax = plt.subplots(figsize=(12, max(6, len(titles) * 0.8)))

        y_pos = range(len(titles))
        bars = ax.barh(y_pos, probabilities, color=colors, alpha=0.7, edgecolor='black')

        for i, (bar, prob, conf) in enumerate(zip(bars, probabilities, confidences)):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                   f'{prob}% ({conf})',
                   va='center', fontsize=10, fontweight='bold')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(titles)
        ax.set_xlabel('Probability (%)', fontsize=12, fontweight='bold')
        ax.set_title('Current Probability Assessments', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 105)

        ax.grid(True, axis='x', alpha=0.3, linestyle='--')

        ax.axvline(10, color='green', linestyle=':', alpha=0.5, linewidth=1)
        ax.axvline(30, color='yellow', linestyle=':', alpha=0.5, linewidth=1)
        ax.axvline(70, color='orange', linestyle=':', alpha=0.5, linewidth=1)
        ax.axvline(90, color='red', linestyle=':', alpha=0.5, linewidth=1)

        today = datetime.now().strftime('%Y-%m-%d')
        ax.text(0.98, 0.02, f'Updated: {today}',
               transform=ax.transAxes, ha='right', va='bottom',
               fontsize=9, style='italic', alpha=0.7)

        plt.tight_layout()

        output_file = output_dir / "current_snapshot.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_all_topics_comparison(self, output_dir: Path):
        """Create comparison chart showing all topics."""
        topics_with_data = {k: v for k, v in self.history.items() if v}

        if not topics_with_data:
            return

        n_topics = len(topics_with_data)
        fig, axes = plt.subplots(n_topics, 1, figsize=(14, 4*n_topics))

        if n_topics == 1:
            axes = [axes]

        for ax, (topic, history) in zip(axes, topics_with_data.items()):
            dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in history]
            probabilities = [entry['probability'] for entry in history]

            ax.plot(dates, probabilities, marker='o', linewidth=2, markersize=6,
                   color='#2E86AB')

            title = self.assessments.get(topic, {}).get('title', topic)
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_ylabel('Probability (%)', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_ylim(0, 100)

            ax.axhspan(0, 10, alpha=0.05, color='green')
            ax.axhspan(10, 30, alpha=0.05, color='yellow')
            ax.axhspan(30, 70, alpha=0.05, color='orange')
            ax.axhspan(70, 90, alpha=0.05, color='red')
            ax.axhspan(90, 100, alpha=0.05, color='darkred')

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.suptitle('All Assessments Comparison', fontsize=16, fontweight='bold', y=1.0)
        plt.tight_layout()

        output_file = output_dir / "all_topics_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Automated Weekly Assessment Tracker")
    parser.add_argument('command', choices=['update', 'view', 'history', 'visualize', 'report',
                                           'status', 'export', 'weekly', 'notify', 'add-topic',
                                           'edit-topic', 'remove-topic', 'list-topics', 'dashboard'],
                       help="Command to execute")
    parser.add_argument('topic', nargs='?', help="Specific topic (for view/history/update/visualize)")
    parser.add_argument('--data-dir', default='./data', help="Data directory path")
    parser.add_argument('--output-dir', default='./visualizations', help="Output directory for visualizations")
    parser.add_argument('--format', choices=['csv', 'markdown', 'pdf'], default='csv',
                       help="Export format (for export command)")
    parser.add_argument('--output', help="Output file path (for export command)")
    parser.add_argument('--email-config', help="Path to email configuration JSON file")
    parser.add_argument('--check-overdue', action='store_true',
                       help="Check for overdue assessments and send notifications")
    parser.add_argument('--port', type=int, default=5000,
                       help="Port for dashboard server (default: 5000)")
    parser.add_argument('--host', default='127.0.0.1',
                       help="Host for dashboard server (default: 127.0.0.1)")

    args = parser.parse_args()

    tracker = AssessmentTracker(data_dir=args.data_dir)

    if args.command == 'update':
        if args.topic:
            tracker.update_assessment(args.topic)
        else:
            tracker.weekly_update_workflow()

    elif args.command == 'view':
        tracker.view_current(args.topic)

    elif args.command == 'history':
        if not args.topic:
            print("Error: Please specify a topic for history view")
            print(f"Available topics: {', '.join(tracker.topics.keys())}")
            sys.exit(1)
        tracker.view_history(args.topic)

    elif args.command == 'visualize':
        tracker.visualize(args.topic, args.output_dir)

    elif args.command == 'report':
        tracker.generate_report()

    elif args.command == 'status':
        tracker.show_status()
        if args.check_overdue:
            tracker.send_desktop_notification()

    elif args.command == 'export':
        if not args.output:
            # Generate default filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if args.format == 'csv':
                output = f"assessments_export_{timestamp}.csv"
            elif args.format == 'markdown':
                output = f"assessments_report_{timestamp}.md"
            else:
                output = f"assessments_export_{timestamp}.{args.format}"
        else:
            output = args.output

        if args.format == 'csv':
            tracker.export_to_csv(output)
        elif args.format == 'markdown':
            tracker.export_to_markdown(output)
        elif args.format == 'pdf':
            print("PDF export coming soon. For now, use markdown format and convert to PDF.")

    elif args.command == 'weekly':
        # Combined weekly workflow: update + visualize + report
        print("Starting weekly workflow...\n")
        tracker.weekly_update_workflow()
        print("\n")
        tracker.generate_report()
        print("\n")
        tracker.visualize(output_dir=args.output_dir)

    elif args.command == 'notify':
        if args.email_config:
            # Load email config
            with open(args.email_config, 'r') as f:
                email_config = json.load(f)
            tracker.send_email_reminder(email_config)
        else:
            # Just desktop notification
            tracker.send_desktop_notification()
            print("✅ Desktop notification sent (if supported)")

    elif args.command == 'add-topic':
        if not args.topic:
            print("Error: Please specify a topic key (e.g., 'my_custom_topic')")
            sys.exit(1)
        tracker.add_topic(args.topic)

    elif args.command == 'edit-topic':
        if not args.topic:
            print("Error: Please specify a topic key to edit")
            print(f"Available topics: {', '.join(tracker.topics.keys())}")
            sys.exit(1)
        tracker.edit_topic(args.topic)

    elif args.command == 'remove-topic':
        if not args.topic:
            print("Error: Please specify a topic key to remove")
            print(f"Available topics: {', '.join(tracker.topics.keys())}")
            sys.exit(1)
        tracker.remove_topic(args.topic)

    elif args.command == 'list-topics':
        tracker.list_topics()

    elif args.command == 'dashboard':
        # Start the web dashboard
        import subprocess
        print(f"\nStarting web dashboard on http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop the server\n")
        subprocess.run([
            sys.executable, 'dashboard.py',
            '--host', args.host,
            '--port', str(args.port)
        ])


if __name__ == "__main__":
    main()
