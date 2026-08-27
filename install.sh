#!/bin/bash

# TODO Telegram Bot - Install Script
# Usage:
#   Interactive (recommended): wget -qO- https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh | bash
#   Or download first: curl -fsSL https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh -o install.sh && bash install.sh
#   Non-interactive: BOT_TOKEN="xxx" ADMIN_CHAT_ID="xxx" bash install.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

REPO_URL="https://github.com/datayouone02/TODO.git"
REPO_BRANCH="main"
SERVICE_NAME="todo-bot"

IS_ROOT=false
[[ $EUID -eq 0 ]] && IS_ROOT=true

ACTUAL_USER="${SUDO_USER:-${USER:-root}}"
ACTUAL_HOME=$(eval echo "~$ACTUAL_USER")
PROJECT_DIR="$ACTUAL_HOME/TODO"

print_info "Installing TODO Bot for $ACTUAL_USER at $PROJECT_DIR"

# Install all dependencies with apt
print_info "Installing system packages via apt..."
apt-get update -qq
apt-get install -y -qq curl git python3 python3-venv python3-pip

# Clone/update repo
if [[ -d "$PROJECT_DIR/.git" ]]; then
    print_info "Updating repository..."
    cd "$PROJECT_DIR"
    [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && sudo -u "$ACTUAL_USER" git pull origin "$REPO_BRANCH" || git pull origin "$REPO_BRANCH"
else
    print_info "Cloning repository..."
    [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && sudo -u "$ACTUAL_USER" git clone -b "$REPO_BRANCH" "$REPO_URL" "$PROJECT_DIR" || git clone -b "$REPO_BRANCH" "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Create venv and install deps
print_info "Setting up Python environment..."
[[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && sudo -u "$ACTUAL_USER" python3 -m venv venv || python3 -m venv venv
[[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && sudo -u "$ACTUAL_USER" "$PROJECT_DIR/venv/bin/pip" install -q -r requirements.txt || "$PROJECT_DIR/venv/bin/pip" install -q -r requirements.txt

# Permissions
[[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && chown -R "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR"
chmod +x "$PROJECT_DIR/TO-DO.py"

# Get credentials - support both interactive and non-interactive
get_credentials() {
    # If provided via environment, use them
    if [[ -n "$BOT_TOKEN" && -n "$ADMIN_CHAT_ID" ]]; then
        print_info "Using credentials from environment variables"
        return 0
    fi

    print_info "Configuring bot credentials..."

    # Function to validate bot token
    validate_token() {
        local token=$1
        response=$(curl -s "https://api.telegram.org/bot$token/getMe")
        if echo "$response" | grep -q '"ok":true'; then
            bot_name=$(echo "$response" | grep -o '"first_name":"[^"]*"' | cut -d'"' -f4)
            bot_username=$(echo "$response" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
            print_success "Bot verified: $bot_name (@$bot_username)"
            return 0
        else
            print_error "Invalid token. Response: $response"
            return 1
        fi
    }

    # Get bot token
    while true; do
        echo
        read -p "Enter your Bot Token (from @BotFather): " BOT_TOKEN
        BOT_TOKEN=$(echo "$BOT_TOKEN" | tr -d '[:space:]')

        if [[ -z "$BOT_TOKEN" ]]; then
            print_error "Token cannot be empty"
            continue
        fi

        print_info "Validating token..."
        if validate_token "$BOT_TOKEN"; then
            break
        fi
    done

    # Get admin chat ID
    while true; do
        echo
        read -p "Enter your Admin Chat ID (from @userinfobot): " ADMIN_CHAT_ID
        ADMIN_CHAT_ID=$(echo "$ADMIN_CHAT_ID" | tr -d '[:space:]')

        if [[ -z "$ADMIN_CHAT_ID" ]]; then
            print_error "Chat ID cannot be empty"
            continue
        fi

        if ! [[ "$ADMIN_CHAT_ID" =~ ^-?[0-9]+$ ]]; then
            print_error "Chat ID must be a number"
            continue
        fi

        # Test sending message
        print_info "Testing bot connection..."
        test_response=$(curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
            -d chat_id="$ADMIN_CHAT_ID" \
            -d text="🤖 TODO Bot started successfully!" \
            -d parse_mode="Markdown")

        if echo "$test_response" | grep -q '"ok":true'; then
            print_success "Test message sent to Telegram!"
            break
        else
            print_error "Failed to send test message. Check Chat ID. Response: $test_response"
        fi
    done
}

get_credentials

# Create .env with provided credentials
print_info "Saving credentials to .env..."
cat > "$PROJECT_DIR/.env" <<EOF
TOKEN=$BOT_TOKEN
ADMIN_CHAT_ID=$ADMIN_CHAT_ID
DATABASE=tasks.db
EOF
[[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && chown "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR/.env"

# systemd or start script
if command -v systemctl &> /dev/null && [[ -d /run/systemd/system ]]; then
    print_info "Setting up systemd service..."
    cat > "/etc/systemd/system/$SERVICE_NAME.service" <<EOF
[Unit]
Description=TODO Telegram Bot
After=network.target
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
[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    print_success "Systemd service installed"

    # Start the service
    print_info "Starting bot..."
    systemctl start "$SERVICE_NAME"
    sleep 2
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Bot is running!"
        echo "  Status: systemctl status $SERVICE_NAME"
        echo "  Logs:   journalctl -u $SERVICE_NAME -f"
    else
        print_error "Bot failed to start. Check logs: journalctl -u $SERVICE_NAME -n 50"
    fi
else
    print_warning "No systemd detected - creating start script"
    cat > "$PROJECT_DIR/start_bot.sh" <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python TO-DO.py
EOF
    chmod +x "$PROJECT_DIR/start_bot.sh"
    [[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && chown "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR/start_bot.sh"
    print_success "Start script created: $PROJECT_DIR/start_bot.sh"

    # Start the bot in background
    print_info "Starting bot..."
    cd "$PROJECT_DIR"
    nohup ./start_bot.sh > bot.log 2>&1 &
    BOT_PID=$!
    sleep 3
    if kill -0 $BOT_PID 2>/dev/null; then
        print_success "Bot is running in background (PID: $BOT_PID)"
        echo "  Logs: tail -f $PROJECT_DIR/bot.log"
        echo "  Stop: pkill -f TO-DO.py"
    else
        print_error "Bot failed to start. Check: cat $PROJECT_DIR/bot.log"
    fi
fi

print_success "Installation complete! 🎉"
echo
echo "Bot is now running and ready to use."
echo "Send /start to your bot in Telegram."