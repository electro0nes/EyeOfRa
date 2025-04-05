# main.py
import yaml
import sys
from watcher import fetch_and_process
from dotenv import load_dotenv
import os

load_dotenv()
with open("config.yaml") as f:
    config = yaml.safe_load(f)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

use_discord = 'nodiscord' not in sys.argv
webhook = DISCORD_WEBHOOK if use_discord else None

for platform, data in config.items():
    fetch_and_process(platform, data['url'], webhook)
