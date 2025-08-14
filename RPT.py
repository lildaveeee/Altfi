
#!/usr/bin/env python3
import requests
import json
import os

with open("config.json", "r") as file:
    config = json.load(file)

TOKEN = config["long_life_token"]
SERVICE_ID = config["service_id"]

BASE_URL = f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/file_server"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def list_files(path):
    resp = requests.get(
        f"{BASE_URL}/list",
        headers=HEADERS,
        params={"dir": path}
    )
    try:
        data = resp.json()
    except ValueError:
        print(f"[ERROR] Non-JSON response listing {path}")
        return []

    if data.get("status") != "success":
        msg = data.get("message", "Unknown error")
        print(f"[ERROR] API list failed for '{path}': {msg}")
        return []

    return data["data"].get("entries", [])


def download_rpt_file(remote_path, local_path):
    resp = requests.get(
        f"{BASE_URL}/download",
        headers=HEADERS,
        params={"file": remote_path}
    )
    if resp.status_code != 200:
        print(f"[ERROR] Initial download request failed for {remote_path}")
        return

    try:
        info = resp.json()
    except ValueError:
        print(f"[ERROR] Invalid JSON from download endpoint for {remote_path}")
        return

    if info.get("status") != "success":
        msg = info.get("message", "Unknown error")
        print(f"[ERROR] Download API error for {remote_path}: {msg}")
        return

    token_url = info.get("data", {}).get("token", {}).get("url")
    if not token_url:
        print(f"[ERROR] No token URL for {remote_path}")
        return

    file_resp = requests.get(token_url)
    if file_resp.status_code != 200:
        print(f"[ERROR] Failed to download file from token URL: {remote_path}")
        return

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with open(local_path, "w", encoding="utf-8") as f:
        f.write(file_resp.text)
    print(f"[DOWNLOADED] {remote_path} → {local_path}")


def traverse_and_download(remote_dir, local_base):
    entries = list_files(remote_dir)
    for entry in entries:
        entry_type = entry.get("type")
        entry_path = entry.get("path")
        entry_name = entry.get("name")

        if entry_type == "dir":
            next_remote = entry_path if entry_path.endswith("/") else entry_path + "/"
            traverse_and_download(next_remote, local_base)

        elif entry_type == "file" and entry_name.lower().endswith(".rpt"):
            local_path = os.path.join(local_base, entry_name)
            download_rpt_file(entry_path, local_path)


def main():
    root_remote = "/games/ni3872975_1/ftproot/"
    local_download_folder = "RPT"

    os.makedirs(local_download_folder, exist_ok=True)

    print(f"Starting .rpt download into '{local_download_folder}/' …")
    traverse_and_download(root_remote, local_download_folder)
    print("All .rpt files have been downloaded to the RPT folder.")


if __name__ == "__main__":
    main()
