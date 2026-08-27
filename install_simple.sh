#!/bin/bash

# Simple TODO Bot Installer - No sudo required
# Run with: ./install_simple.sh

set -e

REPO_URL="https://github.com/datayouone02/TODO.git"
PROJECT_DIR="$HOME/TODO"

echo "🚀 TODO Bot Simple Installer"
echo "=============================="
echo

# Clone or update repository
if [[ -d "$PROJECT_DIR/.git" ]]; then
    echo "📦 Repository exists, pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin master
else
    echo "📦 Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Create .env from template
if [[ ! -f ".env" ]]; then
    echo "⚙️  Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your bot token and admin chat ID:"
    echo "    nano .env"
else
    echo "✅ .env file already exists"
fi

echo
echo "✅ Installation complete!"
echo
echo "Next steps:"
echo "  1. Edit .env with your credentials:"
echo "     nano .env"
echo
echo "  2. Run the bot:"
echo "     source venv/bin/activate"
echo "     python TO-DO.py"
echo
echo "  3. Or run in background:"
echo "     nohup python TO-DO.py > bot.log 2>&1 &"
echo
echo "To stop background process:"
echo "     pkill -f TO-DO.py"