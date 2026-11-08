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

- **Resolved: crash at `main+0x30b150` (SIGSEGV, addr `0x400000008`) when address region allocation failed.** Spelunky 2's engine sets up five 4 GB-spaced heaps by calling `nn::os::AllocateAddressRegion(0x500000000)` (20 GB), requiring `(uint32_t)ptr < 0x7f800000`. With `mem_reserve 0x200000000` (8 GB) and `mem_alias 0x100000000` (4 GB), `RESERVE - DM_GAME_MEM_ALIAS = 4 GB` aligns `g_alias` on an exact 4 GB boundary, placing Region 0 at offset `0x04000000 < 0x7f800000` so the first region attempt initializes all 5 heaps (`Success: 1`). See [4 GB-aligned alias region for multi-gigabyte fixed-offset heaps](../../../docs/reference/memory.md#4-gb-aligned-alias-region-for-multi-gigabyte-fixed-offset-heaps).

## Files and shaders

- RomFS: placeholder containing 2 entries; game assets and shaders are packed inside `main`'s 337 MB internal data block (`0x32aea4` to `0x154ffd50`).
- 107 shaders (93 pixel, 14 vertex) extracted and decrypted by `spel2.py`; paired with a 1-shader pixel cover (`c0ce161c53cdc793`) and compiled for Mac into `b-a02f1e0dfdde.img`.
- Prewarm seed list: 146 entries in `pso_manifest.tsv` (113 seed lines from title/boot, plus 33 gameplay pipeline lines recorded from play sessions).

## Frame rate

- 60 fps on Mac: runs steady at 60 Hz present interval.

## Found on this game

- [Modules exceeding 256 MB with an internal data block](../../../docs/reference/rewriter.md#modules-exceeding-256-mb-with-an-internal-data-block)
- [4 GB-aligned alias region for multi-gigabyte fixed-offset heaps](../../../docs/reference/memory.md#4-gb-aligned-alias-region-for-multi-gigabyte-fixed-offset-heaps)
- [Encrypted asset bundles in main](../../../docs/reference/shaders.md#encrypted-asset-bundles-in-main)
