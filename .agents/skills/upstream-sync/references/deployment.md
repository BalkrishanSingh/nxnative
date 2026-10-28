# Deployment and Binary Rebuild

Execute these steps **only** when the user explicitly requests to compile, rebuild, or deploy updated host binaries.

---

## Installed Games & Bundle Locations

| Game Name | Title ID | App Bundle Path |
| :--- | :--- | :--- |
| **Super Mario Odyssey** | `0100000000010000` | `/Users/balkrishan/Applications/Games/Switch/Super Mario Odyssey.app` |
| **Super Mario Bros. Wonder** | `010015100B514000` | `/Users/balkrishan/Applications/Games/Switch/Super Mario Bros. Wonder.app` |
| **Metroid Dread** | `010093801237C000` | `/Users/balkrishan/Applications/Games/Switch/Metroid Dread.app` |
| **Unicorn Overlord** | `010069401ADB8000` | `/Users/balkrishan/Applications/Games/Switch/Unicorn Overlord.app` |
| **Rhythm Heaven Groove** | `0100D9F01D474000` | `/Users/balkrishan/Applications/Games/Switch/Rhythm Heaven Groove.app` |

---

## Build, Deploy, and Sign Procedure

Run from `dm/host/`:

```bash
cd dm/host

GAMES=(
  "0100000000010000:/Users/balkrishan/Applications/Games/Switch/Super Mario Odyssey.app"
  "010015100B514000:/Users/balkrishan/Applications/Games/Switch/Super Mario Bros. Wonder.app"
  "010093801237C000:/Users/balkrishan/Applications/Games/Switch/Metroid Dread.app"
  "010069401ADB8000:/Users/balkrishan/Applications/Games/Switch/Unicorn Overlord.app"
  "0100D9F01D474000:/Users/balkrishan/Applications/Games/Switch/Rhythm Heaven Groove.app"
)

for ENTRY in "${GAMES[@]}"; do
  TID="${ENTRY%%:*}"
  APP="${ENTRY##*:}"
  
  # 1. Compile per-game binary
  make -B GAME="$TID" dmhost
  
  # 2. Deploy binary into .app bundle
  cp dmhost "$APP/Contents/MacOS/dmhost"
  
  # 3. Ad-hoc codesign
  codesign --force --sign - "$APP/Contents/MacOS/dmhost"
  codesign -v "$APP/Contents/MacOS/dmhost"
done
```

---

## Critical Invariants

1. **Save Data Safety:** Never touch or modify directories under `~/Library/Application Support/nxnative/<TitleID>/save/`.
2. **Codesigning:** macOS gatekeeper blocks unsigned binaries; always sign with `codesign --force --sign -`.
3. **Backup Integrity:** Maintain existing `dmhost.bak` files if present; do not overwrite backups with broken builds.
