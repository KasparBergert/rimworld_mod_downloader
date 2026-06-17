# RimWorld Mod Downloader

Small Python utility for downloading a curated list of RimWorld Steam Workshop mods through SteamCMD.

The repository contains:

- `script.py`: builds and runs a SteamCMD command file for RimWorld workshop downloads.
- `mods.json`: the mod list to download.

## What It Does

The script reads `mods.json`, extracts each Steam Workshop item ID from `steamLink`, and downloads missing mods with SteamCMD using RimWorld's Steam app ID, `294100`.

Before downloading, it checks the SteamCMD workshop download folder and skips mods that already appear to be present. It also removes stale folders from the RimWorld workshop download directory when they are not listed in `mods.json`.

Downloaded mods are written under the SteamCMD workshop directory:

```text
<steamcmd folder>\steamapps\workshop\content\294100
```

## Dependencies

- Windows
- Python 3.9 or newer
- SteamCMD installed locally
- Internet access for SteamCMD workshop downloads
- No Python package dependencies. The script uses only the Python standard library.

The current script expects SteamCMD at:

```text
C:\Users\kaspar\steamcmd\steamcmd.exe
```

If your SteamCMD installation is somewhere else, update `STEAMCMD_PATH` in `script.py`.

## Usage

1. Install SteamCMD.

2. Update `STEAMCMD_PATH` in `script.py` if needed:

   ```python
   STEAMCMD_PATH = r"C:\Users\kaspar\steamcmd\steamcmd.exe"
   ```

3. Edit `mods.json` with the mods you want to download.

   To generate entries from a Steam Workshop collection page, see `STEAM_COLLECTION_BROWSER_SCRIPT.md`.

4. Run the script from this repository:

   ```powershell
   python .\script.py
   ```

The script creates a SteamCMD command file named `rimworld_mod_downloads.txt` inside the SteamCMD folder, then runs SteamCMD automatically.

## Mod List Format

`mods.json` must be a JSON array. Each item should include a Steam Workshop link and a title:

```json
[
  {
    "steamLink": "https://steamcommunity.com/sharedfiles/filedetails/?id=2009463077",
    "title": "Harmony"
  }
]
```

Optional folder name fields can help the script detect already-downloaded mods when the folder name is not just the workshop ID:

```json
{
  "steamLink": "https://steamcommunity.com/sharedfiles/filedetails/?id=2009463077",
  "title": "Harmony",
  "folderName": "Harmony"
}
```

Supported single-folder keys:

- `folderName`
- `folder`
- `directory`
- `name`

Supported multi-folder keys:

- `folderNames`
- `folders`
- `directories`

## Important Notes

- The script downloads anonymously with SteamCMD using `login anonymous`.
- The stale-folder cleanup only looks inside SteamCMD's RimWorld workshop download directory.
- Any folder in that directory that does not match an expected workshop ID, title, or configured folder name from `mods.json` is deleted.
- Keep a backup or review `mods.json` before running the script if the download directory contains mods you want to keep.
