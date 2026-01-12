#!/bin/bash
# GitHub Upload Script for Assessment Tracker
# 
# Prerequisites:
# 1. Install Git: https://git-scm.com/download/mac (or run: brew install git)
# 2. Create empty repo on GitHub named: geopolitical-assessment-tracker
# 3. Replace YOUR-USERNAME below with your actual GitHub username

echo "🚀 GitHub Upload Script for Assessment Tracker"
echo "================================================"
echo ""

# Configuration
GITHUB_USERNAME="spiro1067"  # ⚠️ CHANGE THIS!
REPO_NAME="geopolitical-assessment-tracker"

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed!"
    echo "Install Git from: https://git-scm.com/download/mac"
    echo "Or run: brew install git"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Check if we're in the right directory
if [ ! -f "tracker.py" ]; then
    echo "❌ Error: Not in assessment-tracker directory"
    echo "Please run this script from inside the assessment-tracker folder"
    echo "Example: cd ~/Downloads/assessment-tracker && bash setup_github.sh"
    exit 1
fi

echo "✅ In correct directory"
echo ""

# Check if GitHub username has been changed
if [ "$GITHUB_USERNAME" = "YOUR-USERNAME" ]; then
    echo "❌ Error: Please edit this script and change YOUR-USERNAME to your GitHub username"
    echo "Edit line 11 in this file"
    exit 1
fi

echo "📝 Setting up Git repository..."
echo ""

# Initialize Git if not already
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Create .gitignore to exclude unnecessary files
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Data files (optional - remove if you want to track your data)
# data/assessments.json
# data/history.json

# Visualizations (regenerated each time)
# visualizations/*.png

# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
EOF

echo "✅ Created .gitignore"

# Add all files
git add .
echo "✅ Added files to Git"

# Initial commit
git commit -m "Initial commit: Automated Weekly Assessment Tracker

Features:
- Weekly probability assessment tracking
- Historical logging with change detection
- Automated visualization generation
- Pre-configured for 6 standard geopolitical questions
- Demo data included for testing"

echo "✅ Created initial commit"
echo ""

# Set up remote
REMOTE_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
git remote add origin "$REMOTE_URL" 2>/dev/null || git remote set-url origin "$REMOTE_URL"

echo "✅ Connected to GitHub remote: $REMOTE_URL"
echo ""

# Check if main branch exists, create if not
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main
    echo "✅ Renamed branch to 'main'"
fi

echo "🚀 Ready to push to GitHub!"
echo ""
echo "⚠️  IMPORTANT: Before running the next command, make sure:"
echo "   1. You've created an empty repository named '$REPO_NAME' on GitHub"
echo "   2. The repository is at: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo ""
echo "To push to GitHub, run:"
echo "   git push -u origin main"
echo ""
echo "If this is your first time, Git will ask for your GitHub credentials."
echo "You may need to use a Personal Access Token instead of password."
echo "See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
