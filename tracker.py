#!/usr/bin/env python3
"""
Automated Weekly Assessment Tracker

Maintains ongoing probability assessments for standard geopolitical questions,
tracks changes over time, and generates visualizations of probability evolution.

Usage:
    python3 tracker.py update         # Weekly update workflow
    python3 tracker.py view [topic]   # View current assessments
    python3 tracker.py history [topic] # View historical changes
    python3 tracker.py visualize      # Generate probability timeline charts
    python3 tracker.py report         # Generate weekly summary report
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

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
        self.load_data()
    
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
            self.history = {key: [] for key in STANDARD_QUESTIONS.keys()}
    
    def _initialize_assessments(self) -> Dict:
        """Initialize assessment database with standard questions."""
        assessments = {}
        for key, config in STANDARD_QUESTIONS.items():
            assessments[key] = {
                "title": config["title"],
                "question": config["question"],
                "horizon": config["horizon"],
                "current_probability": None,
                "current_descriptor": None,
                "confidence": None,
                "key_drivers": [],
                "key_uncertainties": [],
                "indicator_status": {ind: "Unknown" for ind in config["key_indicators"]},
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
        config = STANDARD_QUESTIONS[topic]
        
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
        for indicator in config['key_indicators']:
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
        print(f"ASSESSMENT HISTORY: {STANDARD_QUESTIONS[topic]['title']}")
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
            title = STANDARD_QUESTIONS[key]['title']
            print(f"   {i}. {title}")
        
        print("\n" + "-"*70)
        
        for key in topics_to_review:
            proceed = input(f"\nUpdate {STANDARD_QUESTIONS[key]['title']}? (y/n/skip all): ").strip().lower()
            
            if proceed == 'skip all':
                print("Skipping remaining assessments.")
                break
            elif proceed == 'y':
                self.update_assessment(key)
            else:
                print(f"Skipped {STANDARD_QUESTIONS[key]['title']}")
        
        print("\n✅ Weekly update workflow complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Automated Weekly Assessment Tracker")
    parser.add_argument('command', choices=['update', 'view', 'history', 'visualize', 'report'],
                       help="Command to execute")
    parser.add_argument('topic', nargs='?', help="Specific topic (for view/history/update)")
    parser.add_argument('--data-dir', default='./data', help="Data directory path")
    
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
            print(f"Available topics: {', '.join(STANDARD_QUESTIONS.keys())}")
            sys.exit(1)
        tracker.view_history(args.topic)
    
    elif args.command == 'visualize':
        print("Visualization feature coming in next iteration...")
        print("For now, use 'history' command to view changes over time")
    
    elif args.command == 'report':
        print("Report generation feature coming in next iteration...")
        print("For now, use 'view' command to see current assessments")


if __name__ == "__main__":
    main()
