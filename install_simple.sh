#!/bin/bash

# =============================================================================
# TODO Telegram Bot - Simple Installation Script for Ubuntu (No Docker)
# =============================================================================
# This script will:
# 1. Install Python 3 and pip
# 2. Clone the repository
# 3. Set up virtual environment
# 4. Install dependencies
# 5. Configure environment variables
# 6. Create systemd service for auto-start
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_URL="https://github.com/datayouone02/Bot-test.git"
PROJECT_DIR="$HOME/todo-bot"
BOT_TOKEN="7599055445:AAF32gHj_4FDrNy1VZFnesB2--9k3rMqiuU"
SERVICE_NAME="todo-bot"

print_header() { echo -e "${BLUE}==============================================================================${NC}"; echo -e "${BLUE}$1${NC}"; echo -e "${BLUE}==============================================================================${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

print_header "TODO Telegram Bot - Simple Installation (No Docker)"

# Step 1: Update and install dependencies
print_header "Step 1: Installing System Dependencies"
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv git sqlite3
print_success "System dependencies installed"

# Step 2: Clone repository
print_header "Step 2: Cloning Repository"
if [ -d "$PROJECT_DIR" ]; then
    print_warning "Directory exists, pulling latest..."
    cd "$PROJECT_DIR" && git pull origin main
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi
print_success "Repository ready at $PROJECT_DIR"

# Step 3: Create virtual environment
print_header "Step 3: Setting Up Virtual Environment"
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Virtual environment ready with dependencies"

# Step 4: Create .env file
print_header "Step 4: Configuring Environment"
ENV_FILE="$PROJECT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%s)"
fi

cat > "$ENV_FILE" << EOF
TOKEN=$BOT_TOKEN
ADMIN_CHAT_ID=YOUR_CHAT_ID_HERE
DATABASE=tasks.db
EOF

print_success ".env created at $ENV_FILE"
print_warning "EDIT $ENV_FILE and replace YOUR_CHAT_ID_HERE with your Telegram chat ID"

# Step 5: Create systemd service
print_header "Step 5: Creating Systemd Service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=TODO Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python TO-DO.py
Restart=always
RestartSec=10
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=$PROJECT_DIR/.env

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=todo-bot

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
print_success "Systemd service created and enabled"

# Step 6: Start service
print_header "Step 6: Starting the Bot"
sudo systemctl start "$SERVICE_NAME"
sleep 2
sudo systemctl status "$SERVICE_NAME" --no-pager

print_header "Installation Complete!"
echo ""
print_info "Service commands:"
echo -e "  ${YELLOW}sudo systemctl status $SERVICE_NAME${NC}    # Check status"
echo -e "  ${YELLOW}sudo systemctl restart $SERVICE_NAME${NC}   # Restart bot"
echo -e "  ${YELLOW}sudo systemctl stop $SERVICE_NAME${NC}      # Stop bot"
echo -e "  ${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}    # View live logs"
echo ""
print_warning "IMPORTANT NEXT STEPS:"
echo -e "  1. Edit ${YELLOW}$ENV_FILE${NC}: ${YELLOW}nano $ENV_FILE${NC}"
echo -e "  2. Replace YOUR_CHAT_ID_HERE with your actual chat ID"
echo -e "  3. Restart: ${YELLOW}sudo systemctl restart $SERVICE_NAME${NC}"
echo ""
print_info "To get your chat ID:"
echo -e "  1. Message your bot on Telegram"
echo -e "  2. Send /get_id command"
echo -e "  3. Copy the ID and update .env"
echo ""
print_success "Bot is running! 🎉"