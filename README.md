# TODO Telegram Bot

A powerful Telegram bot for managing tasks with expiration dates, tags, and search capabilities.

## Features

- ✅ Add tasks with product links, buyer names, tags, and expiration dates
- 📅 View tasks for today, tomorrow, or any specific date
- 🔍 Search tasks by keywords
- ⏰ Track missed/overdue tasks
- 📊 View task statistics
- ✏️ Edit task details (product link, buyer name, expiration date)
- 🗑️ Delete tasks with confirmation
- 💾 Backup and restore database
- 🔐 Admin-only access control

## Requirements

- Python 3.8+
- Ubuntu/Debian (for install script)
- Telegram Bot Token
- Admin Chat ID

## Quick Install on Ubuntu

### One-line install (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh | sudo bash
```

### For minimal environments (Docker, containers) without curl/sudo

```bash
# Install required tools first
apt-get update && apt-get install -y curl git python3 python3-venv python3-pip

# Then run the install script (works as root without sudo)
curl -fsSL https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh | bash
```

### Manual install

```bash
# Clone the repository (main branch)
git clone -b main https://github.com/datayouone02/TODO.git
cd TODO

# Make install script executable and run it
chmod +x install.sh
sudo ./install.sh
```

The install script will:
1. Install Python 3 and pip if not present
2. Create a virtual environment
3. Install dependencies
4. Set up the bot as a systemd service
5. Configure auto-start on boot

## Manual Installation

### 1. Clone the Repository

```bash
git clone -b main https://github.com/datayouone02/TODO.git
cd TODO
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your values
nano .env
```

Required variables:
```env
TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_admin_chat_id
DATABASE=tasks.db
```

### 5. Run the Bot

```bash
python TO-DO.py
```

## Getting Telegram Credentials

### Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the token provided

### Admin Chat ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your Chat ID (numeric)

## Systemd Service (Auto-start on Boot)

The install script sets up a systemd service. Manual setup:

```bash
# Create service file
sudo tee /etc/systemd/system/todo-bot.service > /dev/null <<EOF
[Unit]
Description=TODO Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/TODO
Environment=PATH=/home/$USER/TODO/venv/bin
ExecStart=/home/$USER/TODO/venv/bin/python TO-DO.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable todo-bot
sudo systemctl start todo-bot
```

### Service Management

```bash
# Check status
sudo systemctl status todo-bot

# View logs
sudo journalctl -u todo-bot -f

# Restart
sudo systemctl restart todo-bot

# Stop
sudo systemctl stop todo-bot
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/add` | Add a new task |
| `/show_all` | View all tasks |
| `/show_today` | View today's tasks |
| `/show_tomorrow` | View tomorrow's tasks |
| `/show_by_day` | View tasks for specific date |
| `/show_missed` | View overdue tasks |
| `/search` | Search tasks |
| `/stats` | View statistics |
| `/get_id` | Get your chat ID |
| `/get_db` | Download database (admin) |
| `/use_this_db` | Replace database (admin) |

## Adding Tasks

1. Send `/add`
2. Enter product link
3. Enter buyer's name
4. Select tags (multiple pages available)
5. Choose to add additional info
6. Select expiration date (presets or manual entry)

## Database Management

The bot uses SQLite (`tasks.db`). You can:
- Download backup: `/get_db` (admin only)
- Restore from backup: Reply to a `.db` file with `/use_this_db` (admin only)

## Project Structure

```
TODO/
├── TO-DO.py           # Main bot entry point
├── database.py        # Database operations
├── settings.py        # Configuration & utilities
├── services.py        # Task display & management logic
├── add_task.py        # Task creation flow
├── migrate_admin.py   # Admin migration utility
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
├── install.sh         # Ubuntu install script
└── README.md          # This file
```

## Troubleshooting

### Bot not responding
```bash
# Check service status
sudo systemctl status todo-bot

# Check logs
sudo journalctl -u todo-bot -n 50
```

### Database errors
```bash
# Check database file exists
ls -la tasks.db

# Check permissions
chmod 644 tasks.db
```

### Port conflicts
The bot uses long polling (no webhook), so no ports needed.

## License

MIT License - feel free to use and modify.

## Support

For issues, create a GitHub issue or contact the admin.