# TODO Telegram Bot

A feature-rich Telegram bot for managing tasks with expiration dates, tags, and statistics.

## Features

- ✅ Add tasks with product links, buyer names, tags, and expiration dates
- 📅 View tasks for today, tomorrow, or any specific date
- 🔍 Search tasks by any field
- 📊 Statistics dashboard (total, today, tomorrow, missed, upcoming)
- ✏️ Edit tasks (product link, buyer name, expiration date)
- 🗑️ Delete tasks with confirmation
- ✅ Mark tasks as done
- 🏷️ Pre-defined tag categories for subscriptions/services

## Quick Install on Ubuntu (One Command)

### Option 1: Docker (Recommended) 🐳
```bash
curl -fsSL https://raw.githubusercontent.com/datayouone02/Bot-test/main/install.sh | bash
```

### Option 2: Simple (No Docker) 🐍
```bash
curl -fsSL https://raw.githubusercontent.com/datayouone02/Bot-test/main/install_simple.sh | bash
```

## Manual Installation

### Using Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/datayouone02/Bot-test.git
cd Bot-test

# 2. Configure environment
cp .env.example .env
nano .env  # Add your TOKEN and ADMIN_CHAT_ID

# 3. Start with Docker Compose
docker compose up -d

# 4. View logs
docker compose logs -f
```

### Without Docker

```bash
# 1. Clone and enter directory
git clone https://github.com/datayouone02/Bot-test.git
cd Bot-test

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Add your TOKEN and ADMIN_CHAT_ID

# 5. Run the bot
python TO-DO.py
```

## Configuration

Create a `.env` file with:

```env
TOKEN=your_bot_token_from_botfather
ADMIN_CHAT_ID=your_telegram_chat_id
DATABASE=tasks.db
```

### Getting Your Chat ID

1. Start a chat with your bot on Telegram
2. Send `/get_id` command
3. Copy the returned chat ID to `.env`

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
| `/get_db` | Download database (admin only) |

## Project Structure

```
.
├── TO-DO.py           # Main bot entry point
├── add_task.py        # Task creation flow
├── services.py        # Task display and management
├── database.py        # Database operations
├── settings.py        # Configuration
├── migrate_admin.py   # Admin migration utility
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker image definition
├── docker-compose.yml # Docker Compose configuration
├── install.sh         # Docker-based installer
├── install_simple.sh  # Non-Docker installer
├── .env.example       # Environment template
└── README.md          # This file
```

## Systemd Service (Production)

The simple installer creates a systemd service for auto-start:

```bash
# Check status
sudo systemctl status todo-bot

# View logs
sudo journalctl -u todo-bot -f

# Restart
sudo systemctl restart todo-bot
```

## Docker Commands

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart
docker compose restart

# View logs
docker compose logs -f

# Rebuild and start
docker compose up -d --build
```

## Database

The bot uses SQLite (`tasks.db`) with the following schema:

```sql
CREATE TABLE tasks (
    chat_id INTEGER,
    product_link TEXT,
    buyer_name TEXT,
    tags TEXT,
    additional_info TEXT,
    expiration_date DATE
);
```

## Pre-defined Tags

The bot includes tags for popular services:
- Streaming: Netflix, Prime Video, Osn+, Shahid VIP, Spotify, Crunchyroll
- Duration: 1 month, 2 months, 3 months, 6 months, 1 year, 2 years
- Screens: 1-5 screens
- Payment: Flexy, BaridiMob, CCP
- Other: Extra, Cookies, Crack, Officiel, VPN, Isra, Asma, Page, Asma Bl, Eleven, King

## License

MIT License