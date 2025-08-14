
#!/usr/bin/env python3

import os

BYPASSED_FILE = "data/bypass_players.txt"
CERTAIN_FILE = "Certain_Players.txt"

def load_players(file_path, keep_order=False):
    players = [] if keep_order else set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:
                    if keep_order:
                        players.append(name)
                    else:
                        players.add(name)
    return players

def main():
    bypassed = load_players(BYPASSED_FILE)
    certain = load_players(CERTAIN_FILE, True)
    filtered = [p for p in certain if p not in bypassed]
    with open(CERTAIN_FILE, "w", encoding="utf-8") as f:
        for player in filtered:
            f.write(player + "\n")
    print(f"Filtered list saved to {CERTAIN_FILE}")
    print(f"Removed {len(certain) - len(filtered)} bypassed players.")

if __name__ == "__main__":
    main()

