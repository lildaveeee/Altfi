
import ast

INPUT_FILE = "data/suspected_players.txt"
OUTPUT_FILE = "Certain_Players.txt"

def parse_players(filename):
    players = []
    current = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("===") and line.endswith("==="):
                if current:
                    players.append(current)
                username = line.strip("=").strip()
                current = {"username": username}
            elif current and ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if key == "gamerScore":
                    current["gamerScore"] = int(val)
                elif key == "friendsCount":
                    current["friendsCount"] = int(val)
                elif key == "accountTier":
                    current["accountTier"] = val.strip('"')
                elif key == "reasons":
                    current["reasons"] = ast.literal_eval(val)
    if current:
        players.append(current)
    return players

def categorize(players):
    high_prob = []
    few_silver = []
    low_silver = []
    zero_gs = []
    assigned = set()

    for p in players:
        user = p["username"]
        reasons = p.get("reasons", [])
        score = p.get("gamerScore", -1)

        if user not in assigned and len(reasons) >= 3:
            high_prob.append(user)
            assigned.add(user)

        elif user not in assigned and set(reasons) == {"few friends", "silver tier"}:
            few_silver.append(user)
            assigned.add(user)

        elif user not in assigned and set(reasons) == {"low gamerscore", "silver tier"}:
            low_silver.append(user)
            assigned.add(user)

        elif user not in assigned and score == 0:
            zero_gs.append(user)
            assigned.add(user)

    return high_prob, few_silver, low_silver, zero_gs

def write_output(filename, high_prob, few_silver, low_silver, zero_gs):
    with open(filename, "w") as f:
        f.write("===== High Probability (3+ reasons) =====\n")
        for u in high_prob:
            f.write(f"{u}\n")

        f.write("\n===== Few Friends & Silver Tier (2 reasons) =====\n")
        for u in few_silver:
            f.write(f"{u}\n")

        f.write("\n===== Low Gamerscore & Silver Tier (2 reasons) =====\n")
        for u in low_silver:
            f.write(f"{u}\n")

        f.write("\n===== Zero Gamerscore =====\n")
        for u in zero_gs:
            f.write(f"{u}\n")

def main():
    players = parse_players(INPUT_FILE)
    high_prob, few_silver, low_silver, zero_gs = categorize(players)
    write_output(OUTPUT_FILE, high_prob, few_silver, low_silver, zero_gs)
    print(f"Categorized players written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
