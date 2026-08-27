# TODO Telegram Bot

A powerful Telegram bot for managing tasks with expiration dates, tags, and search capabilities.

## One-Line Install (Ubuntu/Debian/Docker)

```bash
apt-get update && apt-get install -y curl git python3 python3-venv python3-pip && curl -fsSL https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh | bash
```

## How It Works

The install script will:
1. **Install all dependencies** via apt (curl, git, python3, venv, pip)
2. **Clone the repository** from GitHub
3. **Create virtual environment** and install Python packages
4. **Prompt for Bot Token** - validates it with Telegram API
5. **Prompt for Admin Chat ID** - sends test message to verify
6. **Start the bot** automatically (systemd or background)

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

## Getting Credentials

- **Bot Token**: Message [@BotFather](https://t.me/BotFather) → `/newbot`
- **Chat ID**: Message [@userinfobot](https://t.me/userinfobot)

---

**Repository**: https://github.com/datayouone02/TODO