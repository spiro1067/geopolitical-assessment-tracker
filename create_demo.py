#!/usr/bin/env python3
"""
Demo script to populate the tracker with sample data.

This creates realistic example data so you can see how the tracker works
without manually entering data.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Sample historical data
demo_data = {
    "iranian_collapse": [
        {
            "date": (datetime.now() - timedelta(days=21)).strftime("%Y-%m-%d"),
            "probability": 12,
            "descriptor": "Unlikely",
            "confidence": "Medium",
            "change": None,
            "drivers": [
                "Economic sanctions impact intensifying",
                "Limited elite defection signals"
            ],
            "uncertainties": [
                "Supreme Leader health status unknown",
                "IRGC internal cohesion unclear"
            ],
            "notes": "Initial assessment based on current economic pressure"
        },
        {
            "date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
            "probability": 15,
            "descriptor": "Unlikely",
            "confidence": "Medium",
            "change": 3,
            "drivers": [
                "New EU sanctions package announced",
                "Reports of elite discontent emerging",
                "Protest activity increasing in major cities"
            ],
            "uncertainties": [
                "IRGC loyalty threshold unknown",
                "Regional support (Russia/China) sustainability"
            ],
            "notes": "Slight uptick due to new sanctions and protest indicators"
        },
        {
            "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "probability": 18,
            "descriptor": "Unlikely",
            "confidence": "Medium",
            "change": 3,
            "drivers": [
                "Currency collapse accelerating",
                "Elite defection reports confirmed",
                "Protest movement showing organization"
            ],
            "uncertainties": [
                "Military willingness to use force",
                "International response to crackdown"
            ],
            "notes": "Economic deterioration faster than expected"
        },
        {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "probability": 20,
            "descriptor": "Unlikely",
            "confidence": "Medium",
            "change": 2,
            "drivers": [
                "Major currency devaluation (30%)",
                "Senior IRGC commander defected",
                "Regional isolation deepening"
            ],
            "uncertainties": [
                "Popular uprising threshold",
                "External intervention likelihood"
            ],
            "notes": "Trend continuing upward, watching for inflection point"
        }
    ],
    "ukraine_agreement": [
        {
            "date": (datetime.now() - timedelta(days=21)).strftime("%Y-%m-%d"),
            "probability": 25,
            "descriptor": "Unlikely",
            "confidence": "Low",
            "change": None,
            "drivers": [
                "Both sides showing war fatigue",
                "Western support questions emerging"
            ],
            "uncertainties": [
                "Trump administration policy direction",
                "Russian territorial demands",
                "Ukrainian domestic politics"
            ],
            "notes": "Initial baseline - highly uncertain situation"
        },
        {
            "date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
            "probability": 22,
            "descriptor": "Unlikely",
            "confidence": "Low",
            "change": -3,
            "drivers": [
                "Ukrainian counteroffensive stalling",
                "Russian defensive lines holding"
            ],
            "uncertainties": [
                "Winter offensive potential",
                "Western ammunition supply"
            ],
            "notes": "Battlefield stalemate reduces negotiation pressure"
        },
        {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "probability": 20,
            "descriptor": "Unlikely",
            "confidence": "Medium",
            "change": -2,
            "drivers": [
                "Zelensky rejected territorial concessions",
                "US signals continued support",
                "Russian domestic stability maintained"
            ],
            "uncertainties": [
                "European resolve through winter",
                "2026 election impacts (US, Russia)"
            ],
            "notes": "Both sides appear committed to military solution for now"
        }
    ],
    "taiwan_invasion": [
        {
            "date": (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"),
            "probability": 8,
            "descriptor": "Remote/Highly Unlikely",
            "confidence": "Medium",
            "change": None,
            "drivers": [
                "Economic costs prohibitive",
                "PLA readiness questionable"
            ],
            "uncertainties": [
                "Xi decision-making under pressure",
                "US commitment credibility"
            ],
            "notes": "Baseline assessment for 6-month horizon"
        },
        {
            "date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
            "probability": 12,
            "descriptor": "Unlikely",
            "confidence": "Medium",
            "change": 4,
            "drivers": [
                "PLA exercises intensifying around Taiwan",
                "Nationalist rhetoric increasing in state media",
                "US political dysfunction raising questions"
            ],
            "uncertainties": [
                "Taiwan election results impact",
                "US carrier group deployment"
            ],
            "notes": "Concerning signals from PLA activities"
        },
        {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "probability": 15,
            "descriptor": "Unlikely",
            "confidence": "Medium",
            "change": 3,
            "drivers": [
                "Record PLA incursions into ADIZ",
                "CCP plenum emphasized reunification timeline",
                "Semiconductor export controls tightening"
            ],
            "uncertainties": [
                "Winter weather window closing",
                "Trump administration Taiwan policy"
            ],
            "notes": "Trend line concerning but still unlikely in 6-month window"
        }
    ]
}

def create_demo_data():
    """Create demo data for the tracker."""
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # Create history file
    history_file = data_dir / "history.json"
    
    # Initialize with all topics
    history = {
        "iranian_collapse": demo_data.get("iranian_collapse", []),
        "venezuela_civil_war": [],
        "ukraine_agreement": demo_data.get("ukraine_agreement", []),
        "taiwan_invasion": demo_data.get("taiwan_invasion", []),
        "food_security_crisis": [],
        "greenland_control": []
    }
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print("✅ Created demo history data")
    print(f"   - {len(demo_data['iranian_collapse'])} entries for Iranian Collapse")
    print(f"   - {len(demo_data['ukraine_agreement'])} entries for Ukraine Agreement")
    print(f"   - {len(demo_data['taiwan_invasion'])} entries for Taiwan Invasion")
    
    # Create current assessments from latest history
    assessments = {}
    
    # Iranian collapse
    latest = demo_data["iranian_collapse"][-1]
    assessments["iranian_collapse"] = {
        "title": "Iranian Government Collapse",
        "question": "What is the likelihood of a collapse of the Iranian government in the next 3 months?",
        "horizon": "3 months",
        "current_probability": latest["probability"],
        "current_descriptor": latest["descriptor"],
        "confidence": latest["confidence"],
        "key_drivers": latest["drivers"],
        "key_uncertainties": latest["uncertainties"],
        "indicator_status": {
            "Supreme Leader health/succession signals": "🟡 Watch",
            "IRGC elite cohesion": "🟡 Watch",
            "Protest frequency and size": "🟡 Watch",
            "Economic conditions (sanctions impact, inflation)": "🔴 Critical",
            "Regional isolation vs support": "🟢 Stable"
        },
        "last_updated": latest["date"],
        "next_review": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "notes": latest["notes"]
    }
    
    # Ukraine agreement
    latest = demo_data["ukraine_agreement"][-1]
    assessments["ukraine_agreement"] = {
        "title": "Russia-Ukraine Political Agreement",
        "question": "What is the likelihood of a durable political agreement in the Russian-Ukraine war in the next 3 months?",
        "horizon": "3 months",
        "current_probability": latest["probability"],
        "current_descriptor": latest["descriptor"],
        "confidence": latest["confidence"],
        "key_drivers": latest["drivers"],
        "key_uncertainties": latest["uncertainties"],
        "indicator_status": {
            "Battlefield momentum": "🟢 Stable",
            "Western military/financial support": "🟢 Stable",
            "Russian domestic politics": "🟢 Stable",
            "Ukrainian position (maximalist vs realist)": "🔴 Critical",
            "Third-party mediation efforts": "🟡 Watch"
        },
        "last_updated": latest["date"],
        "next_review": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "notes": latest["notes"]
    }
    
    # Taiwan invasion
    latest = demo_data["taiwan_invasion"][-1]
    assessments["taiwan_invasion"] = {
        "title": "Taiwan Invasion",
        "question": "What is the likelihood of an invasion of Taiwan by China in the next 6 months?",
        "horizon": "6 months",
        "current_probability": latest["probability"],
        "current_descriptor": latest["descriptor"],
        "confidence": latest["confidence"],
        "key_drivers": latest["drivers"],
        "key_uncertainties": latest["uncertainties"],
        "indicator_status": {
            "PLA readiness signals": "🔴 Critical",
            "US commitment credibility": "🟡 Watch",
            "CCP internal politics": "🟡 Watch",
            "Taiwan domestic politics": "🟢 Stable",
            "Economic costs assessment": "🟢 Stable"
        },
        "last_updated": latest["date"],
        "next_review": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "notes": latest["notes"]
    }
    
    # Add empty entries for other topics
    for key in ["venezuela_civil_war", "food_security_crisis", "greenland_control"]:
        config = {
            "venezuela_civil_war": {
                "title": "Venezuela Civil War",
                "question": "What is the likelihood of civil war in Venezuela in the next 3 months?",
                "horizon": "3 months"
            },
            "food_security_crisis": {
                "title": "Global Food Security Crisis",
                "question": "What is the likelihood of two major agricultural regions facing harvest reduction due to extreme weather within 6 months?",
                "horizon": "6 months"
            },
            "greenland_control": {
                "title": "US Control of Greenland",
                "question": "What is the likelihood of the United States obtaining de facto political control of Greenland in the next 6 months?",
                "horizon": "6 months"
            }
        }[key]
        
        assessments[key] = {
            "title": config["title"],
            "question": config["question"],
            "horizon": config["horizon"],
            "current_probability": None,
            "current_descriptor": None,
            "confidence": None,
            "key_drivers": [],
            "key_uncertainties": [],
            "indicator_status": {},
            "last_updated": None,
            "next_review": None,
            "notes": ""
        }
    
    # Save assessments
    assessments_file = data_dir / "assessments.json"
    with open(assessments_file, 'w') as f:
        json.dump(assessments, f, indent=2)
    
    print("\n✅ Created current assessments")
    print(f"   - 3 topics with full data")
    print(f"   - 3 topics awaiting first assessment")
    
    print("\n📊 Try these commands:")
    print("   python3 tracker.py view")
    print("   python3 tracker.py history iranian_collapse")
    print("   python3 visualize.py")
    print("\n🎯 Demo data ready!")

if __name__ == "__main__":
    create_demo_data()
