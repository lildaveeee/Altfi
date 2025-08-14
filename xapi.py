
#!/usr/bin/env python3

import requests
import time
import json
import os

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

CONFIG_FILE = 'config.json'
if not os.path.isfile(CONFIG_FILE):
    raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")

with open(CONFIG_FILE, 'r', encoding='utf-8') as cfg:
    config = json.load(cfg)
    api_key = config.get('api_key', '').strip()

    if not api_key:
        raise ValueError("api_key not found in config.json")

HEADERS = {
    'X-Authorization': api_key,
    'Content-Type': 'application/json'
}

INPUT_FILE           = os.path.join(DATA_DIR, 'player_data.txt')
OUTPUT_FULL          = os.path.join(DATA_DIR, 'full_output.txt')
OUTPUT_SUSPECTS      = os.path.join(DATA_DIR, 'suspected_players.txt')
PROCESSED_FILE       = os.path.join(DATA_DIR, 'processed_players.txt')

GAMERSCORE_THRESHOLD = 1000
FRIENDS_THRESHOLD    = 5
REQUEST_DELAY        = 1.5


class StopScanning(Exception):
    pass


def get_profile_data(gamertag):
    url = f'https://xbl.io/api/v2/search/{gamertag}'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)

        if resp.status_code == 400:
            print(f"  ❌ HTTP 400 Bad Request when fetching {gamertag}. Stopping scan.")
            raise StopScanning()

        if resp.status_code != 200:
            print(f"  ✖ Failed to fetch {gamertag} (HTTP {resp.status_code})")
            return None

        data = resp.json()
        people = data.get('people', [])
        if not people:
            print(f"  ⚠ No user found for {gamertag}")
            return None

        return people[0]

    except requests.exceptions.RequestException as e:
        print(f"  ⚠ Error fetching {gamertag}: {e}")
        return None


def load_set_from_file(path):
    if not os.path.isfile(path):
        return set()
    with open(path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())


def main():
    processed_tags = load_set_from_file(PROCESSED_FILE)
    existing_suspects = set()
    if os.path.isfile(OUTPUT_SUSPECTS):
        with open(OUTPUT_SUSPECTS, 'r', encoding='utf-8') as sf:
            for line in sf:
                line = line.strip()
                if line.startswith('=== ') and line.endswith(' ==='):
                    tag = line[len('=== '):-len(' ===')]
                    existing_suspects.add(tag)

    if not os.path.isfile(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        gamertags = [line.strip() for line in f if line.strip()]

    full_f = open(OUTPUT_FULL, 'w', encoding='utf-8')
    sus_f  = open(OUTPUT_SUSPECTS, 'a', encoding='utf-8')
    proc_f = open(PROCESSED_FILE, 'a', encoding='utf-8')

    try:
        for tag in gamertags:
            if tag in processed_tags:
                print(f"Skipping {tag}, already scanned.")
                continue

            print(f"Checking {tag}…")
            profile = get_profile_data(tag)

            if not profile:
                time.sleep(REQUEST_DELAY)
                continue

            proc_f.write(tag + "\n")
            processed_tags.add(tag)

            full_f.write(f"=== {tag} ===\n")
            for key, val in profile.items():
                full_f.write(f"{key}:{json.dumps(val)}\n")
            full_f.write("\n")

            try:
                score = int(profile.get('gamerScore', '0'))
            except ValueError:
                score = 0

            detail        = profile.get('detail') or {}
            followers     = detail.get('followerCount', 0) or 0
            following     = detail.get('followingCount', 0) or 0
            friends_count = followers + following

            account_tier = detail.get('accountTier', '') or ''
            tier_lower   = account_tier.lower()

            print(f"  → {tag}: {score} GS, {friends_count} friends, tier={account_tier or 'N/A'}")

            reasons = []
            if score < GAMERSCORE_THRESHOLD:
                reasons.append('low gamerscore')
            if friends_count < FRIENDS_THRESHOLD:
                reasons.append('few friends')
            if tier_lower == 'silver':
                reasons.append('silver tier')

            if reasons and tag not in existing_suspects:
                sus_f.write(f"=== {tag} ===\n")
                sus_f.write(f"gamerScore:{json.dumps(score)}\n")
                sus_f.write(f"friendsCount:{json.dumps(friends_count)}\n")
                sus_f.write(f"accountTier:{json.dumps(account_tier)}\n")
                sus_f.write(f"reasons:{json.dumps(reasons)}\n\n")
                existing_suspects.add(tag)

            time.sleep(REQUEST_DELAY)

    except StopScanning:
        print("🚫 Scanning aborted due to API error (HTTP 400).")

    finally:
        full_f.close()
        sus_f.close()
        proc_f.close()
        print(f"\nDone. Full profiles in '{OUTPUT_FULL}'.")
        print(f"Suspected players appended to '{OUTPUT_SUSPECTS}' (no duplicates).")
        print(f"All scanned tags logged in '{PROCESSED_FILE}' and will be skipped on subsequent runs.")


if __name__ == '__main__':
    main()
