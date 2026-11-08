"""shader_split: Spelunky 2 asset bundle reader: NASAM generator test vectors (xnasamx),
file path hashing (hash_filepath_v2), ChaCha encryption roundtrip (decrypt_v2),
and bundle parsing (spel2_shaders). No game files needed."""
import os, struct, sys, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'dm/gfx/tools'))
_had = os.environ.get('DM_GAME'); os.environ['DM_GAME'] = '010015100B514000'
import shader_split as ss
import spel2
if _had is None: del os.environ['DM_GAME']
else: os.environ['DM_GAME'] = _had

class Spelunky2Crypto(unittest.TestCase):
    def test_nasam_xnasamx_vectors(self):
        r1 = spel2.xnasamx(0, 20)
        self.assertEqual(r1, 12792988793366353668)
        r2 = spel2.xnasamx(r1, 32)
        self.assertEqual(r2, 3725411152094604090)

    def test_non_spel2_image_returns_empty(self):
        self.assertEqual(spel2.spel2_shaders(b'NO_SPELUNKY_HERE' * 100, 'main'), [])

    def test_synthetic_bundle_extraction(self):
        zstd = ss.zstd_mod()
        ctl_magic = ss.CTL_MAGIC
        gfx_magic = ss.GFX_MAGIC
        code_body = gfx_magic + b'\0' * 0x40
        ctl_body = ctl_magic + b'\0' * 0x880
        raw_shader = struct.pack('<I', len(code_body)) + code_body + struct.pack('<I', len(ctl_body)) + ctl_body
        comp_shader = zstd.compress(raw_shader)

        path = b'spel2:/Data/ShadersNX/Synthetic_VS_vv.nvn'
        data_len1 = len(comp_shader) + 1
        data_len2 = 200

        # Derive bundle key across both assets
        key0 = spel2.xnasamx(0, data_len1)
        final_key = spel2.xnasamx(key0, data_len2)

        h1 = spel2.hash_filepath_v2(final_key, path)
        enc_payload = spel2.decrypt_v2(final_key, path, comp_shader)

        header_pad = b'\0' * 0x100000
        entry1 = struct.pack('<II', data_len1, len(h1)) + h1 + b'\x01' + enc_payload
        entry2 = struct.pack('<II', data_len2, 32) + b'X' * 32 + b'\x00' + b'\0' * (data_len2 - 1)
        strings = path + b'\0'
        img = header_pad + entry1 + entry2 + b'\0' * 100 + strings

        real_stage = ss.glslc_stage
        real_check = ss.check
        ss.glslc_stage = lambda ctl, code: 'vs'
        ss.check = lambda label, st, ctl, code: None
        try:
            shaders = spel2.spel2_shaders(img, 'main')
            self.assertEqual(len(shaders), 1)
            label, st, ctl, code = shaders[0]
            self.assertEqual(st, 'vs')
            self.assertEqual(label, 'main#SPEL2:' + path.decode('latin1'))
            self.assertEqual(code, code_body)
            self.assertEqual(ctl, ctl_body)
        finally:
            ss.glslc_stage = real_stage
            ss.check = real_check

if __name__ == '__main__':
    unittest.main()
