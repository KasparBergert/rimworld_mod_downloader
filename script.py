import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse, parse_qs


APP_ID = "294100"  # RimWorld
MODS_JSON_PATH = "mods.json"

STEAMCMD_PATH = r"C:\Users\kaspar\steamcmd\steamcmd.exe"
STEAMCMD_FOLDER = Path(STEAMCMD_PATH).parent

COMMAND_FILE = STEAMCMD_FOLDER / "rimworld_mod_downloads.txt"
DOWNLOAD_DIR = STEAMCMD_FOLDER / "steamapps" / "workshop" / "content" / APP_ID

FOLDER_NAME_KEYS = ("folderName", "folder", "directory", "name")
FOLDER_LIST_KEYS = ("folderNames", "folders", "directories")


def extract_workshop_id(steam_link: str) -> str:
    parsed = urlparse(steam_link)
    query = parse_qs(parsed.query)

    if "id" in query and query["id"]:
        return query["id"][0]

    match = re.search(r"id=(\d+)", steam_link)
    if match:
        return match.group(1)

    raise ValueError(f"Could not extract workshop ID from: {steam_link}")


def load_mods():
    path = Path(MODS_JSON_PATH)

    if not path.exists():
        raise FileNotFoundError(f"Could not find {MODS_JSON_PATH}")

    with path.open("r", encoding="utf-8") as file:
        mods = json.load(file)

    if not isinstance(mods, list):
        raise ValueError("mods.json must contain a JSON array/list.")

    return mods


def get_existing_download_folders() -> set[str]:
    if not DOWNLOAD_DIR.exists():
        return set()

    return {
        child.name.casefold()
        for child in DOWNLOAD_DIR.iterdir()
        if child.is_dir()
    }


def get_expected_folder_names(mod, workshop_id: str, title: str) -> set[str]:
    names = {workshop_id, title}

    for key in FOLDER_NAME_KEYS:
        value = mod.get(key)
        if isinstance(value, str) and value.strip():
            names.add(value.strip())

    for key in FOLDER_LIST_KEYS:
        value = mod.get(key)
        if isinstance(value, list):
            names.update(item.strip() for item in value if isinstance(item, str) and item.strip())

    return names


def get_expected_download_folders(mods) -> set[str]:
    expected_folders = set()

    for index, mod in enumerate(mods, start=1):
        steam_link = mod.get("steamLink")
        title = mod.get("title", f"Mod #{index}")

        if not steam_link:
            continue

        workshop_id = extract_workshop_id(steam_link)
        expected_folders.update(get_expected_folder_names(mod, workshop_id, title))

    return {folder_name.casefold() for folder_name in expected_folders}


def delete_stale_download_folders(mods):
    if not DOWNLOAD_DIR.exists():
        return

    expected_folders = get_expected_download_folders(mods)

    for child in DOWNLOAD_DIR.iterdir():
        if not child.is_dir():
            continue

        if child.name.casefold() in expected_folders:
            continue

        print(f"Deleting stale download folder: {child}")
        shutil.rmtree(child)


def create_steamcmd_script(mods):
    lines = []
    lines.append("login anonymous")
    existing_download_folders = get_existing_download_folders()
    queued_count = 0
    skipped_count = 0

    for index, mod in enumerate(mods, start=1):
        steam_link = mod.get("steamLink")
        title = mod.get("title", f"Mod #{index}")

        if not steam_link:
            print(f"Skipping {title}: missing steamLink")
            continue

        workshop_id = extract_workshop_id(steam_link)
        expected_folder_names = get_expected_folder_names(mod, workshop_id, title)
        matching_folder = next(
            (
                folder_name
                for folder_name in expected_folder_names
                if folder_name.casefold() in existing_download_folders
            ),
            None,
        )

        if matching_folder:
            skipped_count += 1
            print(f"Already downloaded: {title} -> {workshop_id} ({matching_folder})")
            continue

        queued_count += 1
        print(f"Queued: {title} -> {workshop_id}")
        lines.append(f"workshop_download_item {APP_ID} {workshop_id}")

    lines.append("quit")

    COMMAND_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Queue updated: {queued_count} to download, {skipped_count} already present")

    return COMMAND_FILE


def main():
    steamcmd = Path(STEAMCMD_PATH)

    if not steamcmd.exists():
        raise FileNotFoundError(f"SteamCMD not found: {steamcmd}")

    mods = load_mods()
    delete_stale_download_folders(mods)
    command_file = create_steamcmd_script(mods)

    print()
    print(f"Created SteamCMD command file:")
    print(command_file)

    print()
    print("Running SteamCMD automatically...")

    subprocess.run(
        [
            str(steamcmd),
            "+runscript",
            str(command_file),
        ],
        cwd=STEAMCMD_FOLDER,
    )

    print()
    print("Done.")
    print("Downloaded files should be here:")
    print(DOWNLOAD_DIR)


if __name__ == "__main__":
    main()
