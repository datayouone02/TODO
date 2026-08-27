#!/bin/bash

# TODO Telegram Bot - One-line install script
# Usage: apt-get update && apt-get install -y curl && curl -fsSL https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh | bash
# Or as root: curl -fsSL https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh | bash

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

# Create .env with credentials
print_info "Creating .env with your credentials..."
cat > "$PROJECT_DIR/.env" <<EOF
TOKEN=7534593312:AAEvjSrbcclTkqVm3aFt7aUNDzPahuSwxt0
ADMIN_CHAT_ID=8432235716
DATABASE=tasks.db
EOF
[[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && chown "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR/.env"
print_success "Credentials written to .env"

# Permissions
[[ "$IS_ROOT" == "true" && "$ACTUAL_USER" != "root" ]] && chown -R "$ACTUAL_USER:$ACTUAL_USER" "$PROJECT_DIR"
chmod +x "$PROJECT_DIR/TO-DO.py"

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
    print_success "Installed! Run: systemctl start $SERVICE_NAME"
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
    print_success "Installed! Run: cd $PROJECT_DIR && ./start_bot.sh"
fi

print_warning "Edit $PROJECT_DIR/.env with TOKEN and ADMIN_CHAT_ID before starting!"