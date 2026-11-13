# Tetris® Effect: Connected (`0100DE501433A000`)

Update 2.0.2.1 (v1245184, `main` build `95c56ff872c4f6d85ef97724dcd0b6e9`) over the base game (v0), SDK 13.3.2. Monstars / Resonair / Stage Games on Unreal Engine 4 (`SDK MW+EpicGames+UnrealEngine-4_26` era) with IoStore container, NVN, Wwise, and `.mp4` movies. Modules `main`, `subsdk0` (movie module `NintendoSDK_movie`) and `sdk`. 60 fps.

Status: playable on the Mac. Extended gameplay reached over 59,700 frames (17+ minutes of continuous play) at a solid 60 fps (p50 frame time 16.67 ms) with zero red lines, smooth audio and controller input, and clean exit.

## What it needs

One rewriter stub in [`patches.py`](patches.py).

| Setting | Where | Why |
|---|---|---|
| `depth_mode zero` | [`game.tsv`](game.tsv) | the game sets near = 0 at startup (`[nvn] depth mode near=0`) |
| `FMallocBinned3` constructor call cut, engine region given what the alias region has room for | the rewriter's engine-wide rules (`dm/tools/ue_malloc.py`, `dm/tools/ue_region.py`) | Unreal Engine 4.26/4.27 binned allocator |
| RedpointEOS online subsystem null-check before virtual dispatch | [`patches.py`](patches.py) `STUBS` | `main+0xb64aa8` looks up `IOnlineSubsystem::Get(TEXT("RedpointEOS"))` and dereferences the pointer without null-checking; on the offline host the subsystem is NULL, causing a SIGSEGV at `main+0xb64b7c` (`ldr x8, [x20]`). A stub checks `cbz x20`, branching to cleanup when NULL and executing virtual dispatch when non-null |
| 64 GB alias region: `mem_reserve 0x1028000000`, `mem_alias 0x1000000000`, `mem_stack 0x10000000`, `app_pool 0xCD500000` | [`game.tsv`](game.tsv) | the layout for Unreal Engine 4 bring-up |
| `sys_resource 0x5000000` | [`game.tsv`](game.tsv) | the NPDM declares 80 MB of system resource |
| `shader_groups ShaderArchive-Global-=global ShaderArchive-=game` | [`game.tsv`](game.tsv) | engine global shaders and material shaders |

## Versions

- **Current: update 2.0.2.1 (v1245184) over base (v0).** Extracted with the base game into `extract/v1245184`. The update overlays the base RomFS container packages and ships the 2.0.2.1 executable modules (`main`, `subsdk0`, `sdk`).

## How to drive it on the Mac

Pack the game with:
```bash
scripts/build_ipa_from_nsp.py <NSP folder> -k <prod.keys> --platform mac
```

Run with window and audio:
```bash
DM_WINDOW=1 DM_AUDIO=1 <command printed by build script>
```

For scripted input or regression testing, pass `DM_KEYS`:
```bash
DM_KEYS="2.0:a,4.0:a,6.0:plus" <command>
```
Controls follow standard Switch gamepad mappings: A / B for confirm and cancel, D-pad / left stick for menu and tetromino movement, L / R for rotation, and Plus for pause/menu.

## Memory

On the Mac, resident memory reached ~3.8–4.15 GB with 2.0 GB GPU allocated, alias mapped up to +0.50 GB, and Unreal heap up to 1.01 GB in use.

## Files and shaders

- `TetrisEffect/Content/Paks/TetrisEffect-Switch.pak` and IoStore container `.ucas` / `.utoc` hold cooked packages and assets. 63 `.mp4` video files live loose in the RomFS.
- Shaders: 11,923 unique (704 compute, 35 geometry, 8,782 pixel, 2,402 vertex). The 2,402 single-stage vertex shaders pair with pixel shader cover `1a449f90aff7f220`.

## Sound

Audio renderer opens at 32 kHz with 64 voices, resampled to 48 kHz on the host (`DeviceSink` inputs 2).

## Open

- iOS testing and packaging remains to be validated on device.
