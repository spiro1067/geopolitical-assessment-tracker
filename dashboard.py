#!/usr/bin/env python3
"""
Web Dashboard for Assessment Tracker

Provides a real-time web interface for viewing assessments, trends, and status.

Usage:
    python3 dashboard.py [--port 5000] [--host 0.0.0.0]
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, flash
import argparse
import sys
import os

# Add parent directory to path to import tracker module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = 'assessment-tracker-secret-key-change-in-production'

# Configuration
DATA_DIR = Path("./data")
VISUALIZATIONS_DIR = Path("./visualizations")


def load_data():
    """Load assessment data from JSON files."""
    assessments = {}
    history = {}
    topics = {}

    # Load topics
    topics_file = DATA_DIR / "topics.json"
    if topics_file.exists():
        with open(topics_file, 'r') as f:
            topics = json.load(f)

    # Load current assessments
    db_file = DATA_DIR / "assessments.json"
    if db_file.exists():
        with open(db_file, 'r') as f:
            assessments = json.load(f)

    # Load history
    history_file = DATA_DIR / "history.json"
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)

    return topics, assessments, history


def calculate_status():
    """Calculate overall status and statistics."""
    topics, assessments, history = load_data()

    total_topics = len(topics)
    assessed_count = sum(1 for a in assessments.values() if a.get('current_probability') is not None)

    # Calculate overdue and due soon
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
                    'days_overdue': abs(days_diff)
                })
            elif days_diff <= 3:
                due_soon.append({
                    'key': key,
                    'title': assessment['title'],
                    'days_until': days_diff
                })
        elif assessment.get('current_probability') is None:
            overdue.append({
                'key': key,
                'title': assessment['title'],
                'days_overdue': None
            })

    return {
        'total_topics': total_topics,
        'assessed_count': assessed_count,
        'overdue_count': len(overdue),
        'due_soon_count': len(due_soon),
        'overdue': overdue,
        'due_soon': due_soon
    }


def get_risk_level(probability):
    """Get risk level descriptor and color."""
    if probability is None:
        return {'level': 'Not Assessed', 'color': 'gray', 'class': 'not-assessed'}
    elif probability < 10:
        return {'level': 'Remote', 'color': '#2ECC71', 'class': 'remote'}
    elif probability < 30:
        return {'level': 'Unlikely', 'color': '#F39C12', 'class': 'unlikely'}
    elif probability < 70:
        return {'level': 'Even Chance', 'color': '#E67E22', 'class': 'even-chance'}
    elif probability < 90:
        return {'level': 'Likely', 'color': '#E74C3C', 'class': 'likely'}
    else:
        return {'level': 'Highly Likely', 'color': '#C0392B', 'class': 'highly-likely'}


@app.route('/')
def index():
    """Main dashboard view."""
    topics, assessments, history = load_data()
    status = calculate_status()

    # Prepare assessment cards
    assessment_cards = []
    for key, topic in topics.items():
        assessment = assessments.get(key, {})
        topic_history = history.get(key, [])

        prob = assessment.get('current_probability')
        risk = get_risk_level(prob)

        # Get trend (recent changes)
        trend = None
        if len(topic_history) >= 2:
            latest_change = topic_history[-1].get('change')
            if latest_change is not None:
                trend = 'up' if latest_change > 0 else 'down' if latest_change < 0 else 'stable'

        assessment_cards.append({
            'key': key,
            'title': topic['title'],
            'question': topic['question'],
            'horizon': topic['horizon'],
            'probability': prob,
            'descriptor': assessment.get('current_descriptor', 'Not Assessed'),
            'confidence': assessment.get('confidence', 'N/A'),
            'last_updated': assessment.get('last_updated', 'Never'),
            'next_review': assessment.get('next_review', 'Not scheduled'),
            'risk_level': risk['level'],
            'risk_color': risk['color'],
            'risk_class': risk['class'],
            'trend': trend,
            'history_count': len(topic_history)
        })

    # Sort by probability (descending), with unassessed at the end
    assessment_cards.sort(key=lambda x: (x['probability'] is None, -(x['probability'] or 0)))

    return render_template('dashboard.html',
                         assessments=assessment_cards,
                         status=status,
                         current_date=datetime.now().strftime('%Y-%m-%d %H:%M'))


@app.route('/topic/<topic_key>')
def topic_detail(topic_key):
    """Detailed view for a specific topic."""
    topics, assessments, history = load_data()

    if topic_key not in topics:
        return "Topic not found", 404

    topic = topics[topic_key]
    assessment = assessments.get(topic_key, {})
    topic_history = history.get(topic_key, [])

    prob = assessment.get('current_probability')
    risk = get_risk_level(prob)

    return render_template('topic_detail.html',
                         key=topic_key,
                         topic=topic,
                         assessment=assessment,
                         history=topic_history,
                         risk=risk,
                         current_date=datetime.now().strftime('%Y-%m-%d %H:%M'))


@app.route('/api/assessments')
def api_assessments():
    """API endpoint for all assessments."""
    topics, assessments, history = load_data()

    result = []
    for key, topic in topics.items():
        assessment = assessments.get(key, {})
        topic_history = history.get(key, [])

        result.append({
            'key': key,
            'title': topic['title'],
            'probability': assessment.get('current_probability'),
            'descriptor': assessment.get('current_descriptor'),
            'confidence': assessment.get('confidence'),
            'last_updated': assessment.get('last_updated'),
            'history': topic_history
        })

    return jsonify(result)


@app.route('/api/topic/<topic_key>')
def api_topic(topic_key):
    """API endpoint for specific topic."""
    topics, assessments, history = load_data()

    if topic_key not in topics:
        return jsonify({'error': 'Topic not found'}), 404

    topic = topics[topic_key]
    assessment = assessments.get(topic_key, {})
    topic_history = history.get(topic_key, [])

    return jsonify({
        'key': topic_key,
        'topic': topic,
        'assessment': assessment,
        'history': topic_history
    })


@app.route('/api/status')
def api_status():
    """API endpoint for status information."""
    return jsonify(calculate_status())


@app.route('/visualizations/<path:filename>')
def serve_visualization(filename):
    """Serve visualization images."""
    return send_from_directory(VISUALIZATIONS_DIR, filename)


def save_data(assessments, history):
    """Save assessments and history to JSON files."""
    db_file = DATA_DIR / "assessments.json"
    history_file = DATA_DIR / "history.json"

    with open(db_file, 'w') as f:
        json.dump(assessments, f, indent=2)

    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)


def get_probability_descriptor(probability):
    """Get descriptor for probability value."""
    if probability < 10:
        return "Remote"
    elif probability < 30:
        return "Unlikely"
    elif probability < 70:
        return "Even Chance"
    elif probability < 90:
        return "Likely"
    else:
        return "Highly Likely"


def calculate_next_review(horizon):
    """Calculate next review date based on time horizon."""
    today = datetime.now().date()

    # For 3-month horizons: weekly reviews
    if '3 month' in horizon.lower():
        return (today + timedelta(days=7)).strftime("%Y-%m-%d")
    # For 6-month horizons: bi-weekly reviews
    else:
        return (today + timedelta(days=14)).strftime("%Y-%m-%d")


@app.route('/update/<topic_key>', methods=['GET', 'POST'])
def update_assessment(topic_key):
    """Update assessment form and handler."""
    topics, assessments, history = load_data()

    if topic_key not in topics:
        flash('Topic not found', 'error')
        return redirect(url_for('index'))

    topic = topics[topic_key]
    assessment = assessments.get(topic_key, {})

    if request.method == 'POST':
        # Get form data
        probability = int(request.form.get('probability'))
        confidence = request.form.get('confidence')
        notes = request.form.get('notes', '').strip()

        # Get drivers (filter out empty ones)
        drivers = []
        for i in range(1, 4):
            driver = request.form.get(f'driver{i}', '').strip()
            if driver:
                drivers.append(driver)

        # Get uncertainties (filter out empty ones)
        uncertainties = []
        for i in range(1, 4):
            uncertainty = request.form.get(f'uncertainty{i}', '').strip()
            if uncertainty:
                uncertainties.append(uncertainty)

        # Calculate change from previous
        previous_prob = assessment.get('current_probability')
        change = (probability - previous_prob) if previous_prob is not None else None

        # Update assessment
        today = datetime.now().strftime("%Y-%m-%d")
        descriptor = get_probability_descriptor(probability)

        assessments[topic_key] = {
            **assessment,  # Keep existing fields like title, question, etc.
            'current_probability': probability,
            'current_descriptor': descriptor,
            'confidence': confidence,
            'key_drivers': drivers,
            'key_uncertainties': uncertainties,
            'last_updated': today,
            'next_review': calculate_next_review(topic['horizon']),
            'notes': notes
        }

        # Add to history
        if topic_key not in history:
            history[topic_key] = []

        history[topic_key].append({
            'date': today,
            'probability': probability,
            'descriptor': descriptor,
            'confidence': confidence,
            'change': change,
            'drivers': drivers,
            'uncertainties': uncertainties,
            'notes': notes
        })

        # Save data
        save_data(assessments, history)

        flash(f'Assessment for "{topic["title"]}" updated successfully!', 'success')
        return redirect(url_for('index'))

    # GET request - show form
    return render_template('update_assessment.html',
                         key=topic_key,
                         topic=topic,
                         assessment=assessment)


@app.route('/add-topic', methods=['GET', 'POST'])
def add_topic():
    """Add new topic form and handler."""
    if request.method == 'POST':
        topics, assessments, history = load_data()

        # Get form data
        topic_key = request.form.get('topic_key', '').strip().lower()
        title = request.form.get('title', '').strip()
        question = request.form.get('question', '').strip()
        horizon = request.form.get('horizon', '').strip()

        # Validate topic key
        if not topic_key or not topic_key.replace('_', '').isalnum():
            flash('Invalid topic key. Use only lowercase letters, numbers, and underscores.', 'error')
            return render_template('add_topic.html')

        if topic_key in topics:
            flash(f'Topic "{topic_key}" already exists!', 'error')
            return render_template('add_topic.html')

        # Get indicators (filter out empty ones)
        indicators = []
        for i in range(1, 6):
            indicator = request.form.get(f'indicator{i}', '').strip()
            if indicator:
                indicators.append(indicator)

        if not indicators:
            flash('At least one indicator is required.', 'error')
            return render_template('add_topic.html')

        # Add topic to topics.json
        topics[topic_key] = {
            'title': title,
            'question': question,
            'horizon': horizon,
            'key_indicators': indicators
        }

        # Initialize assessment
        assessments[topic_key] = {
            'title': title,
            'question': question,
            'horizon': horizon,
            'current_probability': None,
            'current_descriptor': None,
            'confidence': None,
            'key_drivers': [],
            'key_uncertainties': [],
            'indicator_status': {ind: 'Unknown' for ind in indicators},
            'last_updated': None,
            'next_review': None,
            'notes': ''
        }

        # Initialize history
        history[topic_key] = []

        # Save topics
        topics_file = DATA_DIR / "topics.json"
        with open(topics_file, 'w') as f:
            json.dump(topics, f, indent=2)

        # Save assessments and history
        save_data(assessments, history)

        flash(f'Topic "{title}" created successfully!', 'success')
        return redirect(url_for('index'))

    # GET request - show form
    return render_template('add_topic.html')


def main():
    """Run the dashboard server."""
    parser = argparse.ArgumentParser(description="Run Assessment Tracker Dashboard")
    parser.add_argument('--port', type=int, default=5000, help="Port to run on (default: 5000)")
    parser.add_argument('--host', default='127.0.0.1', help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")

    args = parser.parse_args()

    print("\n" + "="*70)
    print("ASSESSMENT TRACKER DASHBOARD")
    print("="*70)
    print(f"Starting server on http://{args.host}:{args.port}")
    print(f"Press Ctrl+C to stop the server")
    print("="*70 + "\n")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
