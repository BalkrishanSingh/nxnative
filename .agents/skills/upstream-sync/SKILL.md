---
name: upstream-sync
description: Sync and summarize upstream commits for nxnative. Use when pulling upstream changes, checking upstream diffs, reviewing commits, or syncing the local nxnative fork while protecting local patches.
---

# Upstream Sync & Summary

Automates pulling upstream `nxnative` changes, preserving custom patches across merges, verifying test suites, and summarizing real-world impact in human wording.

Strictly **gates** compilation: pull and summarize upstream changes first; never compile or deploy binaries without explicit user confirmation.

---

## Workflow Steps

### Step 1: Fetch and Diff Upstream
1. Fetch latest commits from remote:
   ```bash
   git fetch origin
   ```
2. Inspect the commit list and touched files:
   ```bash
   git log --oneline main..origin/main
   git diff --stat main...origin/main
   ```
3. **Completion Criterion:** The exact commit range and file list between local `main` and `origin/main` are identified.

---

### Step 2: Merge and Guard Local Patches
1. Attempt merge from upstream:
   ```bash
   git merge origin/main
   ```
2. If merge conflicts arise or if upstream modified key files, consult the single source of truth in [Mandatory Local Patches](references/local-patches.md):
   - **Multiplayer Handheld Fix:** [`dm/host/hle_hid.c`](file:///Users/balkrishan/Development/nxnative/dm/host/hle_hid.c) (`g_tabletop_multi`, `NPAD_NO1`).
   - **Controller Stick Shake:** [`dm/host/front_mac.m`](file:///Users/balkrishan/Development/nxnative/dm/host/front_mac.m) (`DM_BTN_SHAKE` on L3 click).
   - **Legacy Shader Caches:** [`dm/gfx/nvn/nvn_mtl.m`](file:///Users/balkrishan/Development/nxnative/dm/gfx/nvn/nvn_mtl.m) (fallback for older chain hashes in `shmap_load`, `shader_load`, `pre_desc`, `pso_prebuild`).
3. Commit the merge cleanly:
   ```bash
   git commit -m "Merge upstream main (<commit>): <concise summary>"
   ```
4. **Completion Criterion:** Working tree is clean, git merge is committed, and all 3 local patches are verified present in the code.

---

### Step 3: Run Verification Suite
1. Run host test suite with default profile:
   ```bash
   cd dm/host/tests
   make GAME=0100000000010000
   ```
   *(Note: Avoid running tests with `GAME=0100D9F01D474000` because that profile sets `perf_mode boost`, which causes `t_oe` assertions to fail).*
2. **Completion Criterion:** All test binaries compile and run with 0 errors.

---

### Step 4: Deliver Plain-Language Summary
Explain what upstream changed in accessible human terms, avoiding dry commit dumps or internal jargon. Group findings by impact:
- **Display & Frame Pacing:** Screen refresh, ProMotion 120 Hz, latency, or fullscreen behavior.
- **Graphics & Metal:** Shaders, pipelines, geometry compute passes, textures, render targets.
- **Audio & Input:** Latency, audio sessions, controller applets, rumble/haptics.
- **Memory & Engine:** Allocators, heap limits, NSO/NRO loading, patches.
- **Per-Game Impact:** Specific benefits or regressions for installed titles.

**Completion Criterion:** A concise, human-worded summary is presented to the user.

---

### Step 5: Compilation Gate (Explicit Approval Required)
- **Do NOT compile** game binaries (`dmhost`) or touch `/Users/balkrishan/Applications/Games/Switch/*.app` during pull and summarize.
- Stop after presenting the summary and ask the user if they wish to rebuild and deploy.
- If the user explicitly requests to compile or deploy, follow the instructions in [Deployment and Binary Rebuild](references/deployment.md).
