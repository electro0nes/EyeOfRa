# 🕵️‍♂️ Program-Watcher

A bug bounty **program change monitoring tool** that keeps an eye on platforms like **HackerOne**, **Bugcrowd**, **YesWeHack**, and **Intigriti**.  
Built with ❤️ by [electro0ne (Moein Erfanian)](https://github.com/moeinerfanian).

## 🔍 What It Does

Program-Watcher monitors public bug bounty platforms and **alerts you via Discord** when:

- 🖕 A new program is added
- ❌ A program is removed
- 🟢 New in-scope assets are added
- 🔴 In-scope assets are removed
- ⚫️ New out-of-scope entries are added
- ⚪️ Out-of-scope entries are removed
- 🔄 Scopes are changed or updated
- 📌 Metadata like payout/response time changes
- 💰 New bounty tables are introduced

## ⚙️ Features

- 🔔 Real-time notifications via Discord embeds
- 📂 Secure PostgreSQL storage
- 🐳 Docker/Docker Compose integration
- ✨ Pretty diffs of metadata and scope changes
- 🚰 Designed for bug bounty hunters who care about scope and reward changes

## 📦 Platforms Supported

- HackerOne
- Bugcrowd *(WIP)*
- Intigriti *(WIP)*
- YesWeHack *(WIP)*

## 🚀 Installation

```bash
git clone https://github.com/moeinerfanian/Program-Watcher.git
cd Program-Watcher
```

### 🐳 Run with Docker Compose

Make sure Docker is installed, then:

```bash
docker-compose up -d
```

This will set up:
- PostgreSQL database
- Python script environment

### 🧪 Local Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure `config.yaml` and `.env` file with your **Discord Webhook** and database settings.

3. Run the watcher:

```bash
python main.py nodiscord # for run first time 
```

## 📥 Configuration

- `config.yaml`: Platform sources (JSON endpoints, fetch interval)
- 🧰 DB Table Setup: 
Before running, exec into your PostgreSQL container and create the table:

```sql
CREATE TABLE programs (
    platform TEXT,
    handle TEXT,
    name TEXT,
    data JSONB,
    PRIMARY KEY (platform, handle)
);
```
You can do this like:

```bash
docker-compose exec db psql -U postgres -d bugbounty
```

## 📤 Notifications Example

Each alert will look like this in Discord:

```
[HACKERONE] New Inscope
electro0ne
New Scope Added:
• `*.electro0ne.com` (WILDCARD) → critical
```

## 👨‍💻 Author

Made with ❤️ by [electro0ne (Moein Erfanian)](https://github.com/moeinerfanian)  
🚾 Bug Bounty Hunter & Automation Enthusiast

## 📜 License

MIT — feel free to use and contribute.

