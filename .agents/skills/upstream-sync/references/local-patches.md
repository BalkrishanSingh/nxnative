# Mandatory Local Patches

These three custom patches must be preserved across any upstream merges or rebased branches. If merge conflicts occur in these files, resolve them using the reference patterns below.

---

## 1. Handheld Multiplayer Support (`dm/host/hle_hid.c`)

- **Purpose:** Enables 2-player multiplayer on games that boot in Handheld mode (e.g. *Rhythm Heaven Groove*). When games call `ShowControllerSupport` requiring $\ge 2$ players, Player 1 must switch from `NPAD_HANDHELD` to `NPAD_NO1` so both Player 1 and Player 2 can pair and participate.
- **Key Symbols:** `g_tabletop_multi`, `NPAD_NO1`, `style_changed(0)`.
- **Implementation:**
  ```c
  static _Atomic int g_tabletop_multi;

  static int player_of(uint32_t id) {
      if (id == connected_id()) return 0;
      if (id == NPAD_NO1 && atomic_load(&g_tabletop_multi)) return 0;
      return id > 0 && id < DM_PLAYERS && reported((int)id) ? (int)id : -1;
  }
  ```
  In `SetSupportedNpadIdType`:
  ```c
  if (one_player()) atomic_store(&g_tabletop_multi, 0);
  ```
  In both `h_hid_ShowCtrl` and `h_hid_ShowCtrl0`:
  ```c
  if (arg && arg[0] >= 2) { atomic_store(&g_tabletop_multi, 1); style_changed(0); }
  uint32_t sel = atomic_load(&g_tabletop_multi) ? NPAD_NO1 : connected_id();
  if (info) { info[0] = count; info[1] = (int32_t)sel; }
  ```

---

## 2. Controller Stick Shake Mapping (`dm/host/front_mac.m`)

- **Purpose:** Maps the L3 thumbstick click (`leftThumbstickButton`) to `(DM_BTN_LS | DM_BTN_SHAKE)`. This allows motion-shake actions (like Cappy capture/shake in *Super Mario Odyssey*) to trigger directly from standard controllers without requiring an Apple/DualSense gyroscope.
- **Implementation:**
  ```objc
  K(g.leftThumbstickButton, (DM_BTN_LS | DM_BTN_SHAKE));
  ```

---

## 3. Legacy Shader Cache Compatibility (`dm/gfx/nvn/nvn_mtl.m`)

- **Purpose:** Upstream frequently bumps the translation chain hash (`DMSH_CHAIN`, e.g. `beaff5e82328`). Prebuilt `.metallib` caches bundled with installed apps use older chain directories (`b-dec5ee141a9f`, `b-d374e783beec`, `b-5cddc47253ab`). This fallback allows `dmhost` to load existing precompiled shader libraries and pipeline archives without forcing costly offline re-translation.
- **Implementation Points:**
  1. **`shmap_load()` Directory Fallback:** If `b-<DMSH_CHAIN>` is missing, scan `base_msl` for any directory starting with `b-` and use it.
  2. **`c1_full.tsv` / `cb_extent.tsv` Header Check:** Accept either `want` (current chain), `want2` (directory chain), or stamp substring match:
     ```objc
     const char *dir_chain = [g_msl_dir.lastPathComponent UTF8String];
     if (strncmp(dir_chain, "b-", 2) == 0) dir_chain += 2;
     NSString *want2 = [NSString stringWithFormat:@"# chain b-%s inputs %@ ", dir_chain, st_inputs ?: @"-"];
     int ok = head && (([head hasPrefix:want] || [head hasPrefix:want2]) || (st_inputs && [head containsString:[NSString stringWithFormat:@"inputs %@ ", st_inputs]]));
     ```
  3. **`shader_load()` JSON Chain Check:**
     Verify `j[@"chain"]` exists rather than strictly asserting `[j[@"chain"] isEqual:@DMSH_CHAIN]`.
  4. **`pre_desc()` Descriptor Fallback:**
     Verify `vj[@"chain"] && fj[@"chain"]` rather than strict equality.
  5. **`pso_prebuild()` Stamp Match:**
     Compare `pairs_line` against `have_stamp`:
     ```objc
     NSArray *want_lines = [want componentsSeparatedByString:@"\n"];
     NSString *pairs_line = want_lines.count > 2 ? want_lines[2] : nil;
     if (([have_stamp isEqualToString:want] || (have_stamp && pairs_line && [have_stamp containsString:pairs_line])) && !other) {
         g_pre_running = 0; return -1;
     }
     ```
