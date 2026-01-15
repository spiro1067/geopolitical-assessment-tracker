#!/usr/bin/env python3
"""
Web Dashboard for Assessment Tracker

Provides a real-time web interface for viewing assessments, trends, and status.

Usage:
    python3 dashboard.py [--port 5000] [--host 0.0.0.0]
"""

import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory
import argparse

app = Flask(__name__)

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
