# Teenage Mutant Ninja Turtles: Shredder's Revenge (0100FE701475A000): the rewriter's patches of this game's own builds. dm/tools/patch_nso.py loads every profile's patches.py and applies those of a module's NSO build ID;
# CUTS, OBS and FRAME_STEP as described there ("Registered patches"). Patches of Nintendo SDK module builds are in dm/tools/sdk_patches.py

CUTS = {
  # Teenage Mutant Ninja Turtles: Shredder's Revenge 1.0.9 (v589824) main: Epic Online Services in NRO (rom:/nro/EOSSDK-Switch-Shipping.nro) is refused by ro::LoadModule
  # (MOD_NRO_ONLINE). EOSManager.Initialize (main+0x89a8c0) assumes PlatformInterface.Create never returns null; dereferencing its inner handle causes a null-dereference
  # SIGSEGV at main+0x6d1b4c (addr 0x10). Returning immediately from EOSManager.Initialize bypasses online initialization and allows offline play.
  '24e483af4f3bed10685600eedff3d844': [
    (0x89a8c0, 'fd7bbea9', 'c0035fd6', 'EOSManager.Initialize: return immediately (refused online SDK; prevents null-dereference crash)'),
  ],
}

BINDING = [
    {'what': 'EOSManager.Initialize: return immediately', 'now': 'build', 'goal': 'game', 'purpose': 'runtime',
     'why': 'the game\'s MonoGame BRUTE AOT EOS initialization method in 1.0.9; refuses to run offline without a stub when ro::LoadModule refuses EOS'},
]
