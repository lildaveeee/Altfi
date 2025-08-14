
import requests
import os
import time
import re
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    WEBHOOK_URL = config.get("webhook_url")

if not WEBHOOK_URL:
    print("Error: Webhook URL not found in config.json.")
    exit()

data_file = "Certain_Players.txt"
sent_file = "data/sent_usernames.txt"
info_file = "data/suspected_players.txt"

if os.path.exists(sent_file):
    with open(sent_file, "r") as f:
        sent_usernames = set(line.strip() for line in f)
else:
    sent_usernames = set()

player_info = {}
if os.path.exists(info_file):
    with open(info_file, "r", encoding="utf-8") as f:
        content = f.read()
        blocks = re.split(r"===\s*(.*?)\s*===", content)
        for i in range(1, len(blocks), 2):
            username = blocks[i].strip()
            details = blocks[i + 1].strip().splitlines()
            info = {}
            for line in details:
                if ":" in line:
                    key, value = line.split(":", 1)
                    info[key.strip()] = value.strip().strip('"')
            player_info[username] = info
else:
    print(f"Error: {info_file} not found.")
    exit()

if not os.path.exists(data_file):
    print(f"Error: {data_file} not found.")
    exit()

with open(data_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

current_header = None
for line in lines:
    line = line.strip()
    if line.startswith("====="):
        current_header = line.strip("= ").strip()
    elif line and line not in sent_usernames:
        description = current_header
        if line in player_info:
            info = player_info[line]
            extra = []
            if "gamerScore" in info:
                extra.append(f"**Gamerscore:** {info['gamerScore']}")
            if "friendsCount" in info:
                extra.append(f"**Friends:** {info['friendsCount']}")
            if "accountTier" in info:
                extra.append(f"**Tier:** {info['accountTier']}")
            if "reasons" in info:
                extra.append(f"**Reasons:** {info['reasons']}")
            description += "\n\n" + "\n".join(extra)

        embed = {
            "title": line,
            "description": description,
            "color": 5814783
        }
        payload = {
            "embeds": [embed]
        }

        while True:
            response = requests.post(WEBHOOK_URL, json=payload)
            if response.status_code == 204:
                print(f"✅ Sent: {line}")
                sent_usernames.add(line)
                with open(sent_file, "a") as f:
                    f.write(line + "\n")
                break
            elif response.status_code == 429:
                retry_after = response.json().get("retry_after", 1)
                print(f"⏳ Rate limited. Retrying {line} after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"❌ Failed to send {line}: {response.status_code} - {response.text}")
                break

