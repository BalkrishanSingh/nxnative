# Castle Crashers Remastered (`010001300D14A000`)

Update 1.0.7 (v458752), SDK 9.3.1. MonoGame for the Switch: MonoGame's and the game's C# compiled to C++ by Sickhead Games' BRUTE into `main` (11.7 MB) and `sdk` (19.1 MB), on NVN. Audio through AudioRenderer, 60 fps on Mac.

On the Mac: logos, title screen, main menu, character select and stage gameplay run at 60 fps with audio, controller and keyboard input, and no red line.

## What it needs

| Setting | Where | Why |
|---|---|---|
| `sys_resource 0x0` | [`game.tsv`](game.tsv) | The NPDM declares no system resource: no virtual address memory. |
| 4 GB layout: `mem_reserve 0x100000000`, `mem_alias 0x10000000`, `mem_stack 0x10000000`, `app_pool 0xCD500000` | [`game.tsv`](game.tsv) | 256 MB front + 256 MB alias + 256 MB stack + 3.25 GB heap region. |
| `shader_quad_prim_id on` | [`game.tsv`](game.tsv) | BRUTE's 2D sprite batching submits `NVN_DRAW_PRIMITIVE_QUADS` and indexes per-sprite uniform/storage buffers via `gl_PrimitiveID`. Metal emulates quads using pairs of triangles, assigning `[[primitive_id]]` per triangle. Shifting `gl_PrimitiveID >> 1` aligns the triangle index to the quad index ([`[[primitive_id]]` when emulating quads with triangles](../../../docs/reference/rendering.md#primitive_id-when-emulating-quads-with-triangles)). |

## Shaders

- 18 shaders (2 vertex: `generic.cso`, `overlay.cso`; 16 pixel: `sprite.cso`, `font.cso`, `bloom.cso`, `blur.cso`, `glow.cso`, `heat.cso`, `outline.cso`, `water.cso`, etc.) in `ps_shaders.bin` and `vs_shaders.bin`.
- All 16 pixel shaders index the sprite batch storage buffer via `gl_PrimitiveID`.

## Input

- Controller (DualShock 4, Switch Pro, etc.) and keyboard (A to confirm / attack, B to jump / cancel).

## Found on this game

- [`[[primitive_id]]` when emulating quads with triangles](../../../docs/reference/rendering.md#primitive_id-when-emulating-quads-with-triangles).

## Open

None.
