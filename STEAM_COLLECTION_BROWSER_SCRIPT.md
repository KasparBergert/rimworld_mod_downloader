# Steam Collection Browser Script

Use this browser-console script on a Steam Workshop collection page to generate `mods.json` entries for this downloader.

Example collection page:

```text
https://steamcommunity.com/sharedfiles/filedetails/?id=3746129660
```

This script is intended for Steam Workshop collections: pages that contain multiple workshop items/mods. It is not meant for a single mod page.

## How To Use

1. Open the Steam Workshop collection page in your browser.
2. Scroll far enough that all collection items are visible.
3. Open browser developer tools.
4. Open the Console tab.
5. Paste and run the script below.
6. Replace the contents of `mods.json` with the JSON array printed by the script.

## Script

```javascript
(() => {
  const currentPageId = new URL(location.href).searchParams.get("id");
  const seen = new Set();

  function normalizeText(value) {
    return value?.replace(/\s+/g, " ").trim() || "";
  }

  function getWorkshopId(href) {
    try {
      const url = new URL(href, location.origin);
      return url.searchParams.get("id");
    } catch {
      return null;
    }
  }

  function getTitle(anchor) {
    const container = anchor.closest(
      [
        ".collectionItem",
        ".workshopItem",
        ".workshopItemCollection",
        ".workshopItemPreviewHolder",
        ".itemChoice"
      ].join(",")
    );

    return (
      normalizeText(container?.querySelector(".workshopItemTitle")?.textContent) ||
      normalizeText(anchor.querySelector(".workshopItemTitle")?.textContent) ||
      normalizeText(anchor.getAttribute("title")) ||
      normalizeText(anchor.querySelector("img")?.getAttribute("alt")) ||
      normalizeText(anchor.textContent)
    );
  }

  const mods = Array.from(
    document.querySelectorAll('a[href*="/sharedfiles/filedetails/?id="]')
  )
    .map(anchor => {
      const id = getWorkshopId(anchor.href);

      if (!id || id === currentPageId || seen.has(id)) {
        return null;
      }

      seen.add(id);

      return {
        steamLink: `https://steamcommunity.com/sharedfiles/filedetails/?id=${id}`,
        title: getTitle(anchor) || `Workshop item ${id}`
      };
    })
    .filter(Boolean);

  const output = JSON.stringify(mods, null, 2);

  console.log(`[Steam collection extractor] Found ${mods.length} workshop items.`);
  console.log(output);
  console.table(mods);

  if (!mods.length) {
    console.warn(
      "[Steam collection extractor] No collection items found. Make sure you are on a Steam Workshop collection page and that the items have loaded."
    );
    return;
  }

  navigator.clipboard?.writeText(output)
    .then(() => {
      console.log("[Steam collection extractor] JSON copied to clipboard.");
    })
    .catch(() => {
      console.warn("[Steam collection extractor] Could not copy automatically. Copy the JSON from the console output.");
    });
})();
```

## Output Format

The output is a JSON array compatible with this repository's `mods.json`:

```json
[
  {
    "steamLink": "https://steamcommunity.com/sharedfiles/filedetails/?id=2009463077",
    "title": "Harmony"
  }
]
```

After replacing `mods.json`, run:

```powershell
python .\script.py
```
