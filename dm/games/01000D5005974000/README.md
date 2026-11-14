# N++ (`01000D5005974000`)

Update 1.0.7 (v458752, `main` build `21111086aaf48867511bf264a770945f`) over base game (v0), SDK **4.5.0** (`nnSdk-4_5_0`, `NintendoSDK_OpenGL-4_5_0`, `NintendoSDK_NVN-4_5_0`). Metanet Software platformer on C++, SDL, and desktop OpenGL 3.2 through EGL (`dm/gfx/gl/hle_gl.m`).

RomFS holds 4,727 files (0.55 GB): levels, palettes (`.tga`), sounds (`.wav`), music (`.ogg`), fonts (`.fnt`), and loose GLSL shaders (`NPP/Shaders/glsl/*.vert` and `*.frag`).

Modules: `main` and `sdk`. `subsdk0` (`NintendoSDK_OpenGL`) is not loaded: the host's GL layer answers `main`'s EGL imports directly on Metal.

Status: playable on the Mac with full 60 FPS gameplay, sound, and OpenGL-on-Metal rendering (UBOs, samplers, MRT). Zero dropped draws across frame loops. Mac app size: 0.67 GB (RomFS 0.55 GB). iOS IPA: not built yet.

## What it needs

| Setting | Where | Why |
|---|---|---|
| `modules main sdk` | [`game.tsv`](game.tsv) | `main` takes nothing from NVIDIA's GL driver: the host's GL layer answers EGL imports, keeping `subsdk0` unloaded |
| `sys_resource 0x0`; `mem_reserve 0x100000000`, `mem_alias 0x10000000`, `mem_stack 0x10000000`, `app_pool 0xCD500000`, `mem_used 0x4c00000` | [`game.tsv`](game.tsv) | the NPDM declares no system resource; `nninitStartup` allocates a heap of 3.13 GB from the pool |
| `shader_note N++ has no NVN shaders (its GLSL shaders go through the GL layer)` | [`game.tsv`](game.tsv) | no NVN shaders: GLSL shaders in RomFS go through `gl_shaders.py` and `hle_gl.m` |

## How to drive it on the Mac

Pack for Mac:
```bash
python3 scripts/build_ipa_from_nsp.py <NSP folder> -k <prod.keys> --platform mac
```

Run with window and audio:
```bash
DM_WINDOW=1 DM_AUDIO=1 <command printed by build script>
```

Controls follow standard Switch gamepad mappings (Left stick / D-pad for movement, A / B for jump).

## Rendering (OpenGL)

- **Shaders:** 90 loose GLSL sources in `NPP/Shaders/glsl/` (45 `.vert` and 45 `.frag`, `#version 330 core`), translating to 76 unique Metal vertex and fragment functions in `gl_shaders.metallib`.
- **Uniform Buffer Objects (UBOs):** 28 vertex shaders use uniform block `uniform OrthoBlock { mat4 m; } ortho;` bound to `GL_UNIFORM_BUFFER` (0x8a11), backed by host Metal buffers bound at buffer index 1.
- **Multiple Render Targets (MRT):** Render passes configure multiple color attachments (`outColour0`, `outColour1`) cleared via `glClearBufferfv` and bound to dual color outputs.
- **Samplers:** Engine uses dedicated sampler objects (`glGenSamplers`, `glBindSampler`, `glSamplerParameteri`) bound to active texture units.

## Sound

Audio renderer opens at 48 kHz with 200 voices, 8 submixes, and 1 final mix, paced cleanly by the output sink.

## Found on this game

- [GL uniform buffer objects, sampler objects and multiple render targets](../../../docs/reference/rendering.md#gl-uniform-buffer-objects-sampler-objects-and-multiple-render-targets)

## Open

- iOS on-device validation.
