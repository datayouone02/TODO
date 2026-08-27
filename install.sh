#!/bin/bash

# TODO Telegram Bot - Ubuntu Installation Script
# Run with: sudo ./install.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/datayouone02/TODO.git"
REPO_BRANCH="main"
PROJECT_DIR="$HOME/TODO"
SERVICE_NAME="todo-bot"
PYTHON_VERSION="3.8"

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

get_actual_user() {
    if [[ -n "$SUDO_USER" ]]; then
        echo "$SUDO_USER"
    else
        echo "$USER"
    fi
}

ACTUAL_USER=$(get_actual_user)
ACTUAL_HOME=$(eval echo "~$ACTUAL_USER")
PROJECT_DIR="$ACTUAL_HOME/TODO"

print_info "Starting TODO Bot installation for user: $ACTUAL_USER"
print_info "Project directory: $PROJECT_DIR"

# Check if running as root
check_root

# Update package list
print_info "Updating package list..."
apt-get update -qq

# Install Python and dependencies
print_info "Installing Python $PYTHON_VERSION and required packages..."
apt-get install -y -qq python3 python3-venv python3-pip git

# Check Python version
PYTHON_INSTALLED_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_info "Python version installed: $PYTHON_INSTALLED_VERSION"

# Clone or update repository
if [[ -d "$PROJECT_DIR/.git" ]]; then
    print_info "Repository exists, pulling latest changes..."
    cd "$PROJECT_DIR"
    sudo -u "$ACTUAL_USER" git pull origin master
else
    print_info "Cloning repository..."
    sudo -u "$ACTUAL_USER" git clone -b "$REPO_BRANCH" "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Create virtual environment
print_info "Creating virtual environment..."
sudo -u "$ACTUAL_USER" python3 -m venv venv

# Install Python dependencies
print_info "Installing Python dependencies..."
sudo -u "$ACTUAL_USER" "$PROJECT_DIR/venv/bin/pip" install --upgrade pip -q
sudo -u "$ACTUAL_USER" "$PROJECT_DIR/venv/bin/pip" install -r requirements.txt -q

# Create .env file if it doesn't exist
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    print_warning "No .env file found. Creating from template..."
    sudo -u "$ACTUAL_USER" cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    print_warning "Please edit $PROJECT_DIR/.env with your bot token and admin chat ID"
    print_warning "Use: nano $PROJECT_DIR/.env"
else
    print_info ".env file already exists"
fi

# Set permissions
print_info "Setting file permissions..."
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR"
chmod +x "$PROJECT_DIR/TO-DO.py"

# Create systemd service
print_info "Creating systemd service..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" <<EOF
[Unit]
Description=TODO Telegram Bot
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=10
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/TO-DO.py
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
print_info "Configuring systemd service..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

print_success "Installation complete!"
echo
print_info "Next steps:"
echo "  1. Edit the .env file with your credentials:"
echo "     nano $PROJECT_DIR/.env"
echo
echo "  2. Start the bot:"
echo "     sudo systemctl start $SERVICE_NAME"
echo
echo "  3. Check status:"
echo "     sudo systemctl status $SERVICE_NAME"
echo
echo "  4. View logs:"
echo "     sudo journalctl -u $SERVICE_NAME -f"
echo
print_warning "Remember to add your TOKEN and ADMIN_CHAT_ID to .env before starting!"