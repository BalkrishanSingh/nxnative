# Spelunky 2 (`01007EC013ABC000`)

Update 1.28.0 (v524288) over the base game, SDK 13.3.0. Custom C++ engine (BlitWorks / Mossmouth), NVN, FMOD audio. Modules `main` and `sdk`. Plays on the Mac at 60 fps: reaches the frame loop, initializes NVN graphics, mounts RomFS `spel2:` and save directory, and renders frames.

## What it needs

| Setting | Where | Why |
|---|---|---|
| Split point for modules over 256 MB with middle data blocks | `dm/tools/patch_nso.py` | `main` is 346 MB with a 337 MB data block between code sections; setting `SPLIT = BACK_MIN` reaches all sites without overlapping patch areas |
| Spelunky 2 asset bundle reader and decrypter | `dm/gfx/tools/spel2.py`, `dm/gfx/tools/shader_split.py` | shaders are encrypted with ChaCha (`Spel2ChaChaVersion2`) and compressed with zstd in `main`'s internal data block, keyed by a NASAM mixer |
| Node area cut 1 GB → 62 MB and 2 MB region alignment | `dm/tools/sdk_patches.py` SDK-wide rules | the SDK-wide function-matched cuts (implementation 3 of 8 for node area, implementation 3 of 4 for alignment) |
| `mem_reserve 0x200000000` (8 GB), `mem_alias 0x100000000` (4 GB) | [`game.tsv`](game.tsv) | guarantees `g_alias` begins on a 4 GB boundary, so the first 20 GB address region matches `(uint32_t)ptr < 0x7f800000`; see [Memory](#memory) |
| `depth_mode zero` | `game.tsv` | the game calls `nvnDeviceSetDepthMode` with near = 0 |
| `sys_resource 0x200000` | `game.tsv` | the NPDM declares 2 MB of system resource |
| `mem_used 0x16e00000` | `game.tsv` | covers the loaded modules' size for `SetHeapSize` |

## Memory

- **Resolved: crash at `main+0x30b150` (SIGSEGV, addr `0x400000008`) when address region allocation failed.** Spelunky 2's custom engine sets up five 4 GB-spaced heaps via `nn::os::AllocateAddressRegion(0x500000000)` (20 GB), requiring Region 0 to satisfy `(uint32_t)ptr < 0x7f800000`. Handled by 4 GB alignment of `g_alias`; see [4 GB-aligned alias region for multi-gigabyte fixed-offset heaps](../../../docs/reference/memory.md#4-gb-aligned-alias-region-for-multi-gigabyte-fixed-offset-heaps).

## Files and shaders

- RomFS: placeholder containing 2 entries; game assets and shaders are packed inside `main`'s 337 MB internal data block (`0x32aea4` to `0x154ffd50`).
- 107 shaders (93 pixel, 14 vertex) extracted and decrypted by `spel2.py`; paired with a 1-shader pixel cover (`c0ce161c53cdc793`) and compiled for Mac into `b-a02f1e0dfdde.img`.
- Prewarm seed list: 146 entries in `pso_manifest.tsv` (113 seed lines from title/boot, plus 33 gameplay pipeline lines recorded from play sessions).

## Frame rate

- 60 fps on Mac: runs steady at 60 Hz present interval.

## On the Mac

- Start with `python3 scripts/build_ipa_from_nsp.py /path/to/Spelunky2` or run directly via `DM_GAME=01007EC013ABC000 ./01007EC013ABC000_build/Spelunky2.app/Contents/MacOS/Spelunky2`.
- Controls: Arrow keys / WASD for movement, Z / Space for jump, X for whip/action, C for bomb, Shift for run/enter doors. Connected controllers work via standard macOS HID.
- Tested: Boot to title, profile setup, menu navigation, character selection, adventure mode entry into World 1 (Mines) 1-1 through 1-4 at continuous 60 fps.

## Open

- iOS device testing: Mac gameplay verified at 60 fps; iOS IPA build not yet sideloaded or tested on physical iPhone/iPad hardware.
- Full game playthrough: Validated through World 1 Mines; later areas (Jungle, Volcana, Olmec, Tide Pool, Temple, Neo Babylon, Sunken City, Cosmic Ocean) pending further play sessions.

## Found on this game

- [Modules exceeding 256 MB with an internal data block](../../../docs/reference/rewriter.md#modules-exceeding-256-mb-with-an-internal-data-block)
- [4 GB-aligned alias region for multi-gigabyte fixed-offset heaps](../../../docs/reference/memory.md#4-gb-aligned-alias-region-for-multi-gigabyte-fixed-offset-heaps)
- [Encrypted asset bundles in main](../../../docs/reference/shaders.md#encrypted-asset-bundles-in-main)
