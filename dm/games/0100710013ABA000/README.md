# Spelunky (`0100710013ABA000`)

Update 1.0.5 (v327680; base game v0), SDK 11.4.0. Custom 2D engine by Mossmouth and BlitWorks, FMOD audio via `AudioOut` (`OpenAudioOut`), on NVN. Modules `main` and `sdk` only. Brought up on the Mac; plays at steady 60 fps with sound.

On the Mac: Mossmouth and BlitWorks logos, title screen, menu, adventure mode gameplay at 60 fps with audio, 0 red lines.

## What it needs

The provisional profile's guesses held: no key needed changing.

| Setting | Where | Why |
|---|---|---|
| `sys_resource 0x0` | [`game.tsv`](game.tsv) | The NPDM declares no system resource (`IsVirtualAddressMemoryEnabled` is false). Linear heap allocation without virtual address regions |
| 4 GB layout: `mem_reserve 0x100000000`, `mem_alias 0x10000000`, `mem_stack 0x10000000`, `app_pool 0xCD500000` | `game.tsv` | 256 MB front + 256 MB alias + 256 MB stack + 3.25 GB heap region |
| `nvnDeviceApplyDeferredFinalizes` no-op | `dm/gfx/nvn/hle_nvn.c` | Called on device initialization by SDK 11.4 NVN runtime; safe no-op on Metal |
| `shader_groups /Data/=data` | `game.tsv` | Shaders in `Data/Shaders/NX/*.nvn` |

## Shaders

- **Current:** 34 shaders (17 vertex, 17 pixel) stored as standalone `.nvn` packages under `Data/Shaders/NX/` in RomFS.
- Extracted and translated by standard `shader_split.py` without requiring custom decrypters (unlike Spelunky 2's ChaCha20 assets).
- 100% compiled to MSL and bundled into the Metallib cache.

## Input

- Gamepad and keyboard supported.

## Found on this game

- **`nvnDeviceApplyDeferredFinalizes`:** NVN device finalization hook implemented as a semantic no-op on Metal: [nvnDeviceApplyDeferredFinalizes](../../../docs/reference/rendering.md#nvndeviceapplydeferredfinalizes).
