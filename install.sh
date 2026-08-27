#!/bin/bash

# TODO Telegram Bot - Ubuntu Installation Script
# Run with: sudo ./install.sh  (or as root directly: ./install.sh)
# One-liner: curl -fsSL https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh | bash
#           (or with sudo if not root: curl -fsSL ... | sudo bash)

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

# Detect if running as root
IS_ROOT=false
if [[ $EUID -eq 0 ]]; then
    IS_ROOT=true
fi

# Get the actual user (non-root user who invoked sudo, or current user)
get_actual_user() {
    if [[ -n "$SUDO_USER" ]]; then
        echo "$SUDO_USER"
    elif [[ "$IS_ROOT" == "true" && -n "$USER" && "$USER" != "root" ]]; then
        echo "$USER"
    else
        echo "root"
    fi
}

ACTUAL_USER=$(get_actual_user)
ACTUAL_HOME=$(eval echo "~$ACTUAL_USER")
PROJECT_DIR="$ACTUAL_HOME/TODO"

print_info "Starting TODO Bot installation for user: $ACTUAL_USER"
print_info "Project directory: $PROJECT_DIR"
print_info "Running as root: $IS_ROOT"

# Install required system packages (curl, sudo if missing)
print_info "Installing required system packages..."
apt-get update -qq

# Install curl if missing (needed for one-liner)
if ! command -v curl &> /dev/null; then
    print_info "Installing curl..."
    apt-get install -y -qq curl
fi

# Install sudo if missing (needed for running commands as actual user)
if ! command -v sudo &> /dev/null; then
    print_info "Installing sudo..."
    apt-get install -y -qq sudo
fi

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
    if [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]]; then
        sudo -u "$ACTUAL_USER" git pull origin "$REPO_BRANCH"
    else
        git pull origin "$REPO_BRANCH"
    fi
else
    print_info "Cloning repository..."
    if [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]]; then
        sudo -u "$ACTUAL_USER" git clone -b "$REPO_BRANCH" "$REPO_URL" "$PROJECT_DIR"
    else
        git clone -b "$REPO_BRANCH" "$REPO_URL" "$PROJECT_DIR"
    fi
fi

cd "$PROJECT_DIR"

# Create virtual environment
print_info "Creating virtual environment..."
if [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]]; then
    sudo -u "$ACTUAL_USER" python3 -m venv venv
else
    python3 -m venv venv
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
if [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]]; then
    sudo -u "$ACTUAL_USER" "$PROJECT_DIR/venv/bin/pip" install --upgrade pip -q
    sudo -u "$ACTUAL_USER" "$PROJECT_DIR/venv/bin/pip" install -r requirements.txt -q
else
    "$PROJECT_DIR/venv/bin/pip" install --upgrade pip -q
    "$PROJECT_DIR/venv/bin/pip" install -r requirements.txt -q
fi

# Create .env file if it doesn't exist
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    print_warning "No .env file found. Creating from template..."
    if [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]]; then
        sudo -u "$ACTUAL_USER" cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    else
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    fi
    print_warning "Please edit $PROJECT_DIR/.env with your bot token and admin chat ID"
    print_warning "Use: nano $PROJECT_DIR/.env"
else
    print_info ".env file already exists"
fi

# Set permissions
print_info "Setting file permissions..."
if [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]]; then
    chown -R "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR"
fi
chmod +x "$PROJECT_DIR/TO-DO.py"

# Check if systemd is available
USE_SYSTEMD=false
if command -v systemctl &> /dev/null && [[ -d /run/systemd/system ]]; then
    USE_SYSTEMD=true
fi

if [[ "$USE_SYSTEMD" == "true" ]]; then
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

# Security settings (only apply if not running as root in container)
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
    echo "     systemctl start $SERVICE_NAME"
    echo
    echo "  3. Check status:"
    echo "     systemctl status $SERVICE_NAME"
    echo
    echo "  4. View logs:"
    echo "     journalctl -u $SERVICE_NAME -f"
    echo
else
    # No systemd - create a simple start script
    print_warning "systemd not available (container/minimal environment). Creating start script instead."

    cat > "$PROJECT_DIR/start_bot.sh" <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python TO-DO.py
EOF
    chmod +x "$PROJECT_DIR/start_bot.sh"

    if [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]]; then
        chown "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR/start_bot.sh"
    fi

    print_success "Installation complete!"
    echo
    print_info "Next steps:"
    echo "  1. Edit the .env file with your credentials:"
    echo "     nano $PROJECT_DIR/.env"
    echo
    echo "  2. Run the bot directly:"
    echo "     cd $PROJECT_DIR && ./start_bot.sh"
    echo
    echo "  3. Or run in background:"
    echo "     cd $PROJECT_DIR && nohup ./start_bot.sh > bot.log 2>&1 &"
    echo
    echo "  4. To stop background process:"
    echo "     pkill -f TO-DO.py"
    echo
fi

print_warning "Remember to add your TOKEN and ADMIN_CHAT_ID to .env before starting!"