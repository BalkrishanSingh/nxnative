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

- **Resolved: crash at `main+0x30b150` (SIGSEGV, addr `0x400000008`) when address region allocation failed.** Spelunky 2's engine sets up five 4 GB-spaced heaps by calling `nn::os::AllocateAddressRegion(0x500000000)` (20 GB) up to 6 times. For each candidate region pointer `ptr`, it tests:
  ```c
  uint64_t cand = (ptr & ~0xffffffffULL) | 0x7f800000ULL;
  if (cand > ptr && cand + 0x402000000 <= ptr + 0x500000000) { /* match */ }
  ```
  The check ensures all five 4 GB heaps (each mapping 32 MB initially, ending at `cand + 0x402000000`) fit entirely inside the 20 GB reservation. This holds whenever the candidate's lower 32 bits satisfy `(uint32_t)ptr < 0x7f800000` (~2.04 GB). Because 20 GB is an exact multiple of 4 GB (`5 * 0x100000000`), every sequential 20 GB region shares the lower 32-bit offset of the first region. With `mem_reserve 0x200000000` and `mem_alias 0x100000000`, `RESERVE - DM_GAME_MEM_ALIAS = 4 GB`, placing `g_alias` on an exact 4 GB boundary. After the 62 MB node area and 32 MB alignment, Region 0 starts at offset `0x04000000` (64 MB), which immediately satisfies `< 0x7f800000` on the first attempt, freeing the other attempts and initializing all 5 heaps (`Success: 1`). See [4 GB-aligned alias region for multi-gigabyte fixed-offset heaps](../../../docs/reference/memory.md#4-gb-aligned-alias-region-for-multi-gigabyte-fixed-offset-heaps).

## Files and shaders

- RomFS: placeholder containing 2 entries; game assets and shaders are packed inside `main`'s 337 MB internal data block (`0x32aea4` to `0x154ffd50`).
- 107 shaders (93 pixel, 14 vertex) extracted and decrypted by `spel2.py`; paired with a 1-shader pixel cover (`c0ce161c53cdc793`) and compiled for Mac into `b-a02f1e0dfdde.img`.
- Prewarm seed list: 111 entries in `pso_manifest.tsv`.

## Frame rate

- 60 fps on Mac: runs steady at 60 Hz present interval.

## Found on this game

- [Modules exceeding 256 MB with an internal data block](../../../docs/reference/rewriter.md#modules-exceeding-256-mb-with-an-internal-data-block)
- [4 GB-aligned alias region for multi-gigabyte fixed-offset heaps](../../../docs/reference/memory.md#4-gb-aligned-alias-region-for-multi-gigabyte-fixed-offset-heaps)
- [Encrypted asset bundles in main](../../../docs/reference/shaders.md#encrypted-asset-bundles-in-main)
