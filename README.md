# TODO Telegram Bot

A powerful Telegram bot for managing tasks with expiration dates, tags, and search capabilities.

## One-Line Install (Ubuntu/Debian/Docker)

```bash
apt-get update && apt-get install -y curl git python3 python3-venv python3-pip && curl -fsSL https://raw.githubusercontent.com/datayouone02/TODO/main/install.sh | bash
```

## After Installation

1. Edit `.env` with your credentials:
   ```bash
   nano ~/TODO/.env
   ```
   Add your:
   - `TOKEN` (from @BotFather)
   - `ADMIN_CHAT_ID` (from @userinfobot)

2. Start the bot:
   ```bash
   # If systemd available (standard Ubuntu)
   systemctl start todo-bot
   
   # If no systemd (Docker/minimal)
   cd ~/TODO && ./start_bot.sh
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

## Getting Credentials

- **Bot Token**: Message [@BotFather](https://t.me/BotFather) → `/newbot`
- **Chat ID**: Message [@userinfobot](https://t.me/userinfobot)

---

**Repository**: https://github.com/datayouone02/TODO