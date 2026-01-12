#!/usr/bin/env python3
"""
Visualization module for Assessment Tracker

Generates charts and visual representations of probability assessments over time.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

# Use Agg backend for headless environments
import matplotlib
matplotlib.use('Agg')


class AssessmentVisualizer:
    """Creates visualizations for assessment history."""
    
    def __init__(self, data_dir: str = "./data", output_dir: str = "./visualizations"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load history
        history_file = self.data_dir / "history.json"
        if not history_file.exists():
            print("Error: No history data found. Run updates first.")
            sys.exit(1)
        
        with open(history_file, 'r') as f:
            self.history = json.load(f)
        
        # Load current assessments
        db_file = self.data_dir / "assessments.json"
        if db_file.exists():
            with open(db_file, 'r') as f:
                self.assessments = json.load(f)
        else:
            self.assessments = {}
    
    def plot_single_timeline(self, topic: str, save: bool = True):
        """Create timeline chart for a single topic."""
        if topic not in self.history or not self.history[topic]:
            print(f"No history data for {topic}")
            return
        
        history = self.history[topic]
        dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in history]
        probabilities = [entry['probability'] for entry in history]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot probability line
        ax.plot(dates, probabilities, marker='o', linewidth=2, markersize=8, 
                color='#2E86AB', label='Probability Assessment')
        
        # Add confidence bands (if available)
        # TODO: Could add high/low confidence bands based on confidence level
        
        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Probability (%)', fontsize=12, fontweight='bold')
        
        title = self.assessments.get(topic, {}).get('title', topic)
        ax.set_title(f'Probability Assessment Timeline: {title}', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 100)
        
        # Add probability zones
        ax.axhspan(0, 10, alpha=0.1, color='green', label='Remote')
        ax.axhspan(10, 30, alpha=0.1, color='yellow', label='Unlikely')
        ax.axhspan(30, 70, alpha=0.1, color='orange', label='Even Chance')
        ax.axhspan(70, 90, alpha=0.1, color='red', label='Likely')
        ax.axhspan(90, 100, alpha=0.1, color='darkred', label='Highly Likely')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45, ha='right')
        
        # Add legend
        ax.legend(loc='upper left', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / f"{topic}_timeline.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Saved timeline chart: {output_file}")
            plt.close()
        else:
            plt.show()
    
    def plot_all_topics_comparison(self, save: bool = True):
        """Create comparison chart showing all topics."""
        # Filter topics with history
        topics_with_data = {k: v for k, v in self.history.items() if v}
        
        if not topics_with_data:
            print("No history data available for any topic")
            return
        
        # Create figure with subplots
        n_topics = len(topics_with_data)
        fig, axes = plt.subplots(n_topics, 1, figsize=(14, 4*n_topics))
        
        if n_topics == 1:
            axes = [axes]
        
        for ax, (topic, history) in zip(axes, topics_with_data.items()):
            dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in history]
            probabilities = [entry['probability'] for entry in history]
            
            # Plot
            ax.plot(dates, probabilities, marker='o', linewidth=2, markersize=6, 
                   color='#2E86AB')
            
            # Formatting
            title = self.assessments.get(topic, {}).get('title', topic)
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_ylabel('Probability (%)', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_ylim(0, 100)
            
            # Add probability zones (lighter for comparison view)
            ax.axhspan(0, 10, alpha=0.05, color='green')
            ax.axhspan(10, 30, alpha=0.05, color='yellow')
            ax.axhspan(30, 70, alpha=0.05, color='orange')
            ax.axhspan(70, 90, alpha=0.05, color='red')
            ax.axhspan(90, 100, alpha=0.05, color='darkred')
            
            # Format dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.suptitle('All Assessments Comparison', fontsize=16, fontweight='bold', y=1.0)
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / "all_topics_comparison.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Saved comparison chart: {output_file}")
            plt.close()
        else:
            plt.show()
    
    def plot_current_snapshot(self, save: bool = True):
        """Create bar chart of current probabilities."""
        # Get topics with current assessments
        topics_with_current = {k: v for k, v in self.assessments.items() 
                              if v.get('current_probability') is not None}
        
        if not topics_with_current:
            print("No current assessments available")
            return
        
        # Prepare data
        titles = [v['title'] for v in topics_with_current.values()]
        probabilities = [v['current_probability'] for v in topics_with_current.values()]
        confidences = [v.get('confidence', 'Unknown') for v in topics_with_current.values()]
        
        # Color by probability level
        colors = []
        for prob in probabilities:
            if prob < 10:
                colors.append('#2ECC71')  # Green - Remote
            elif prob < 30:
                colors.append('#F39C12')  # Yellow - Unlikely
            elif prob < 70:
                colors.append('#E67E22')  # Orange - Even Chance
            elif prob < 90:
                colors.append('#E74C3C')  # Red - Likely
            else:
                colors.append('#C0392B')  # Dark Red - Highly Likely
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, max(6, len(titles) * 0.8)))
        
        # Horizontal bar chart
        y_pos = range(len(titles))
        bars = ax.barh(y_pos, probabilities, color=colors, alpha=0.7, edgecolor='black')
        
        # Add probability values on bars
        for i, (bar, prob, conf) in enumerate(zip(bars, probabilities, confidences)):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2, 
                   f'{prob}% ({conf})', 
                   va='center', fontsize=10, fontweight='bold')
        
        # Formatting
        ax.set_yticks(y_pos)
        ax.set_yticklabels(titles)
        ax.set_xlabel('Probability (%)', fontsize=12, fontweight='bold')
        ax.set_title('Current Probability Assessments', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 105)
        
        # Grid
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        # Add vertical lines for zones
        ax.axvline(10, color='green', linestyle=':', alpha=0.5, linewidth=1)
        ax.axvline(30, color='yellow', linestyle=':', alpha=0.5, linewidth=1)
        ax.axvline(70, color='orange', linestyle=':', alpha=0.5, linewidth=1)
        ax.axvline(90, color='red', linestyle=':', alpha=0.5, linewidth=1)
        
        # Date stamp
        today = datetime.now().strftime('%Y-%m-%d')
        ax.text(0.98, 0.02, f'Updated: {today}', 
               transform=ax.transAxes, ha='right', va='bottom',
               fontsize=9, style='italic', alpha=0.7)
        
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / "current_snapshot.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Saved snapshot chart: {output_file}")
            plt.close()
        else:
            plt.show()
    
    def generate_all_visualizations(self):
        """Generate all visualization types."""
        print("\n" + "="*70)
        print("GENERATING VISUALIZATIONS")
        print("="*70 + "\n")
        
        # Current snapshot
        print("📊 Creating current snapshot...")
        self.plot_current_snapshot(save=True)
        
        # Individual timelines
        print("\n📈 Creating individual timelines...")
        topics_with_data = [k for k, v in self.history.items() if v]
        for topic in topics_with_data:
            print(f"   - {topic}")
            self.plot_single_timeline(topic, save=True)
        
        # Comparison chart
        if len(topics_with_data) > 1:
            print("\n📊 Creating comparison chart...")
            self.plot_all_topics_comparison(save=True)
        
        print("\n✅ All visualizations generated!")
        print(f"📁 Output directory: {self.output_dir.absolute()}")


def main():
    """Main entry point for visualization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate assessment visualizations")
    parser.add_argument('--data-dir', default='./data', help="Data directory")
    parser.add_argument('--output-dir', default='./visualizations', help="Output directory")
    parser.add_argument('--topic', help="Generate visualization for specific topic only")
    
    args = parser.parse_args()
    
    visualizer = AssessmentVisualizer(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    
    if args.topic:
        visualizer.plot_single_timeline(args.topic, save=True)
    else:
        visualizer.generate_all_visualizations()


if __name__ == "__main__":
    main()
