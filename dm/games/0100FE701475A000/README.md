# Teenage Mutant Ninja Turtles: Shredder's Revenge (`0100FE701475A000`)

Update 1.0.9 (v589824), SDK 13.3.2. Tribute Games / Dotemu, MonoGame for the Switch: Tribute Games' C# code compiled to C++ by Sickhead's BRUTE into `main` (49 MB of code, 95 MB with data and bss) with a Boehm collector; Wwise sound (`Content/Audio/*.bnk` / `.pck`) through the audio renderer; NVN. Modules `main`, `subsdk0`, `subsdk1` and `sdk`.

## Status on the Mac

- Tribute Games and Dotemu logos, the opening anime intro movie, the title screen ("PRESS ANY BUTTON"), the main menu (Story, Arcade, Survival), character select, and Chapter 1 (April O'Neil, Leonardo, Michelangelo, Donatello, Raphael, Splinter, Casey Jones, Karai, Usagi).
- Rock-solid 60.0 fps (frame time p50 16.67 ms, GPU 1.2–2.5 ms).
- Gamepad input works out of the box with the standard action layout.

## What it needs

The 4 GB memory layout matches standard 64-bit titles.

| Setting | Where | Why |
|---|---|---|
| 4 GB layout: `mem_reserve 0x100000000`, `mem_alias 0x10000000`, `mem_stack 0x10000000`, `app_pool 0xCD500000` | [`game.tsv`](game.tsv) | 256 MB in front + 256 MB alias region + 256 MB stack region + 3.25 GB heap region |
| `mem_used 0xac00000` (172 MB) | [`game.tsv`](game.tsv) | the rewritten modules are larger than the default 64 MB of used memory (168 MB + 4 MB), so the heap request plus the modules would exceed the application pool |
| `pad_layout simple` | [`game.tsv`](game.tsv) | 2D arcade beat-'em-up layout |
| `zip_store .zxnb:.pbn:.bnk:.pck:.metallib` | [`game.tsv`](game.tsv) | raw deflate compressed content and Wwise audio packages |
| `patches.py` cut `0x89a8c0` (`ret`) | [`patches.py`](patches.py) | return immediately from `EOSManager.Initialize` (bypasses refused online SDK, prevents null-dereference crash) |

## Online services

- **Refused EOS module:** The game ships `rom:/nro/EOSSDK-Switch-Shipping.nro` for Epic Online Services cross-play. As with all online SDKs, `ro::LoadModule` refuses to load it (`MOD_NRO_ONLINE`), returning null / zero.
- **Null-dereference crash:** TMNT's MonoGame BRUTE C# wrapper `Epic.OnlineServices.Platform.PlatformInterface.Create` returns `null` when the underlying handle is `IntPtr.Zero`. `Paris.Engine.EOS.EOSManager.Initialize` immediately calls `s_platformInterface.GetAuthInterface()`, reading `*(ptr + 0x10)` of a null pointer causing an unhandled SIGSEGV at `main+0x6d1b4c`.
- **The fix:** `patches.py` replaces the function entry instruction `stp x29, x30, [sp, #-0x20]!` at `main+0x89a8c0` with `ret` (`c0035fd6`). Bypassing `EOSManager.Initialize` allows the game to cleanly run offline with no side effects.

## Files and shaders

- Shaders are stored in `Content/Shaders/*.zxnb` as MonoGame MGFX version 10 effects compressed with raw deflate streams (`zlib.decompress(d, -15)`).
- **Current:** 88 shaders (44 pixel, 44 vertex) across 25 effect files, read by `shader_split.py` (`mgfx_effect`). Every binding decodes cleanly.
- The prewarm list ([`pso_manifest.tsv`](pso_manifest.tsv)) records pipelines used across title, menus, character select, and Chapter 1.

## Add-on content (DLC)

- DLC 1: *Dimension Shellshock* (`0100FE701475B001`) — adds Survival Mode, Karai, and Usagi Yojimbo.
- DLC 2: *Radical Reptiles* (`0100FE701475B002`) — adds Mondo Gecko and Mona Lisa.
- Both DLCs are detected through the standard `aoc` service (`aoc::CountAddOnContent`, `aoc::ListAddOnContent`).

## Found on this game

General host and tool changes first needed here:

- **MGFX version 10 effects and `.zxnb` deflate streams** (`mgfx_effect` and `scan_file_in` in `shader_split.py`): [MGFX version 10 effects (.zxnb deflate streams)](../../../docs/reference/shaders.md#mgfx-version-10-effects-zxnb-deflate-streams).
- **Online SDKs in NROs**: [Online SDKs in NROs are never loaded](../../../docs/reference/services.md#online-sdks-in-nros-are-never-loaded).

## Open

- Online multiplayer is disabled because the host intentionally does not load online SDKs. Local co-op works.
