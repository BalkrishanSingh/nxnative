# Tetris® Effect: Connected (0100DE501433A000): patches of this game's own builds, keyed by NSO build ID.
# dm/tools/patch_nso.py loads every profile's patches.py and applies those of a module's NSO build ID;
# STUBS as described there ("Stubs").
from nso_asm import B, BLR, LDRX, MOVX, NOP

# The method at main+0xb64aa8 looks up the "RedpointEOS" online subsystem (IOnlineSubsystem::Get(FName(TEXT("RedpointEOS"))))
# and attempts virtual dispatch (+0x178) on the returned subsystem pointer (x20) to register an online event listener delegate.
# In nxnative's offline host, the RedpointEOS plugin does not initialize and Get() returns NULL (x20 = 0).
# The game's code does not null-check x20 before virtual dispatch at main+0xb64b7c (ldr x8, [x20]), causing a SIGSEGV.
# Instead of bypassing the entire registration function, we insert a root-cause null-check stub: if x20 is non-null,
# the virtual dispatch executes normally; if x20 is NULL, it skips the call and jumps safely to the delegate cleanup at main+0xb64b8c.
def redpoint_eos_nullcheck(ctx):
    here, emit = ctx.here, ctx.emit
    site_off = 0xb64b7c
    ctx.site(site_off, '880240f908bd40f9e00314aa00013fd6')
    start = here()
    skip_target = start + 4 * 5
    # cbz x20, skip_target
    emit(0xb4000000 | ((((skip_target - start) >> 2) & 0x7ffff) << 5) | 20)
    emit(LDRX(8, 20, 0))                                          # ldr x8, [x20]
    emit(LDRX(8, 8, 0x178 // 8))                                  # ldr x8, [x8, #0x178]
    emit(MOVX(0, 20))                                             # mov x0, x20
    emit(BLR(8))                                                  # blr x8
    assert here() == skip_target
    emit(B(here(), 0xb64b8c))                                     # b 0xb64b8c
    ctx.put(site_off, [B(site_off, start), NOP, NOP, NOP],
            'RedpointEOS online subsystem null-check before virtual dispatch')


STUBS = {
    '95c56ff872c4f6d85ef97724dcd0b6e9': redpoint_eos_nullcheck,
}

# How general each patch is and could be (dm/tools/docs_patches.py "Binding", listed in docs/agents/game-patches.md):
BINDING = [
    {'what': 'RedpointEOS online delegate registration: null-check before virtual call', 'now': 'build', 'goal': 'game', 'purpose': 'runtime',
     'why': "the game's own un-nullchecked dereference of the RedpointEOS online subsystem; on the offline host the subsystem is NULL"},
]
