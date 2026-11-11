# Spelunky 2 asset bundle and shader reader: the game embeds its virtual filesystem ('spel2:/') inside main's internal data block
# (between text_end and ro), encrypted with custom ChaCha rounds (Spel2ChaChaVersion2) and compressed with zstd.
# Assets are keyed by a NASAM mixer (xnasamx) seeded with 0 and updated with data_len per asset.
import re, struct, sys, os
from typing import Dict, List, Optional, Tuple, Union

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../tools'))
sys.path.insert(0, os.path.dirname(__file__))

def ror64(val: int, r: int) -> int:
    return ((val >> r) | (val << (64 - r))) & 0xFFFFFFFFFFFFFFFF

def xnasamx(constant: int, data: int) -> int:
    """NASAM mixer (Not Another Strange Acronym Mixer) generator used by Spelunky 2's asset bundle:
    data ^= constant; data ^= ror64(data, 25) ^ ror64(data, 47); data *= 0x9e6c63d0676a9a99;
    data ^= (data >> 23) ^ (data >> 51); data *= 0x9e6d62d06f6a9a9b; data ^= (data >> 23) ^ (data >> 51); data ^= constant"""
    data = data & 0xFFFFFFFFFFFFFFFF
    constant = constant & 0xFFFFFFFFFFFFFFFF
    data ^= constant
    data ^= ror64(data, 25) ^ ror64(data, 47)
    data = (data * 0x9E6C63D0676A9A99) & 0xFFFFFFFFFFFFFFFF
    data ^= (data >> 23) ^ (data >> 51)
    data = (data * 0x9E6D62D06F6A9A9B) & 0xFFFFFFFFFFFFFFFF
    data ^= (data >> 23) ^ (data >> 51)
    data ^= constant
    return data & 0xFFFFFFFFFFFFFFFF

def rol32(val: int, r: int) -> int:
    return (((val << r) & 0xFFFFFFFF) | (val >> (32 - r))) & 0xFFFFFFFF

def quarter_round(w: List[int], a: int, b: int, c: int, d: int) -> None:
    w[a] = (w[a] + w[b]) & 0xFFFFFFFF; w[d] = rol32(w[d] ^ w[a], 16)
    w[c] = (w[c] + w[d]) & 0xFFFFFFFF; w[b] = rol32(w[b] ^ w[c], 12)
    w[a] = (w[a] + w[b]) & 0xFFFFFFFF; w[d] = rol32(w[d] ^ w[a], 8)
    w[c] = (w[c] + w[d]) & 0xFFFFFFFF; w[b] = rol32(w[b] ^ w[c], 7)

def round_pair(w: List[int]) -> None:
    quarter_round(w, 0, 4, 8, 12); quarter_round(w, 1, 5, 9, 13); quarter_round(w, 2, 6, 10, 14); quarter_round(w, 3, 7, 11, 15)
    quarter_round(w, 0, 5, 10, 15); quarter_round(w, 1, 6, 11, 12); quarter_round(w, 2, 7, 8, 13); quarter_round(w, 3, 4, 9, 14)

def two_rounds(b: bytes) -> bytes:
    w = list(struct.unpack('<16I', b)); round_pair(w); round_pair(w); return struct.pack('<16I', *w)

def quad_rounds(b: bytes) -> bytes:
    w = list(struct.unpack('<16I', b)); round_pair(w); round_pair(w); round_pair(w); round_pair(w); return struct.pack('<16I', *w)

def add_bytes_as_quads(b1: bytes, b2: bytes) -> bytes:
    return struct.pack('<8Q', *[((a + b) & 0xFFFFFFFFFFFFFFFF) for a, b in zip(struct.unpack('<8Q', b1), struct.unpack('<8Q', b2))])

def xor_bytes(b1: Union[bytes, bytearray], b2: Union[bytes, bytearray]) -> bytes:
    return bytes(x ^ y for x, y in zip(b1, b2))

def mix_in(h: bytes, s: bytes) -> bytes:
    out = bytearray(h); pos = 0
    while pos < len(s):
        amount = min(len(out), len(s) - pos); partial = s[pos:pos + amount]
        for idx, byte in enumerate(reversed(partial)): out[idx] ^= byte
        out = bytearray(quad_rounds(bytes(out))); pos += amount
    return bytes(out)

def keyed_hashing(filepath: bytes, key: bytes) -> bytes:
    out = bytearray()
    for idx in range(0, len(filepath), 64):
        amount = min(idx + 64, len(filepath)); partial = filepath[idx:amount]
        out.extend(xor_bytes(partial, bytes(reversed(key[:len(partial)]))))
    return bytes(out)

def derive_round_key(key: int, filepath: bytes, modifier: int) -> bytes:
    init_quads = [key, len(filepath), 0, 0, 0, 0, 0, 0]
    h = mix_in(two_rounds(struct.pack('<8Q', *init_quads)), filepath)
    tmp = add_bytes_as_quads(h, quad_rounds(h))
    quads = list(struct.unpack('<8Q', tmp))
    quads[0] ^= (modifier & 0xFFFFFFFFFFFFFFFF)
    return quad_rounds(struct.pack('<8Q', *quads))

def hash_filepath_v2(key: int, filepath: bytes) -> bytes:
    k = derive_round_key(key, filepath, len(filepath))
    return keyed_hashing(filepath, k)

def decrypt_v2(key: int, filepath: bytes, data: bytes) -> bytes:
    k = derive_round_key(key, filepath, key + len(data))
    out = bytearray(); pos = 0; blocks = len(data) // 64
    if blocks > 0:
        out.extend(xor_bytes(data[:blocks * 64], bytes(reversed(k)) * blocks))
        pos = blocks * 64
    rem = len(data) - pos
    if rem > 0:
        out.extend(xor_bytes(data[pos:], bytes(reversed(k[:rem]))))
    return bytes(out)

PATH_LEN_MIN = 10
PATH_LEN_MAX = 256
DATA_LEN_MAX = 0x10000000

def find_bundle_start(img: bytes) -> Optional[int]:
    """Find the start of the embedded asset bundle by locating sequential bundle entries:
    data_len (u32), filepath_len (u32), filepath_hash (filepath_len bytes), is_encrypted (u8)"""
    limit = min(len(img) - 16, 0x1000000)
    for o in range(0x100000, limit, 4):
        dlen, flen = struct.unpack_from('<II', img, o)
        if PATH_LEN_MIN <= flen <= PATH_LEN_MAX and PATH_LEN_MIN <= dlen <= DATA_LEN_MAX:
            if o + 8 + flen < len(img) and img[o + 8 + flen] in (0, 1):
                next_o = o + 8 + flen + dlen
                if next_o < len(img) - 8:
                    dlen2, flen2 = struct.unpack_from('<II', img, next_o)
                    if PATH_LEN_MIN <= flen2 <= PATH_LEN_MAX and PATH_LEN_MIN <= dlen2 <= DATA_LEN_MAX and img[next_o + 8 + flen2] in (0, 1):
                        return o
    return None

def spel2_shaders(img: bytes, label: str) -> List[Tuple[str, str, bytes, bytes]]:
    """Extract and decrypt shaders embedded in Spelunky 2's asset bundle inside main"""
    if b'spel2:/Data/ShadersNX/' not in img: return []
    start = find_bundle_start(img)
    if start is None: return []

    import shader_split as ss
    zstd = ss.zstd_mod()

    o = start; keygen = 0; assets_by_hash: Dict[bytes, Tuple[int, int, int]] = {}
    while o < len(img) - 8:
        data_len, filepath_len = struct.unpack_from('<II', img, o)
        if data_len == 0 or filepath_len == 0 or data_len > 0x10000000: break
        asset_len = data_len - 1
        fp_hash = bytes(img[o + 8:o + 8 + filepath_len])
        is_encrypted = img[o + 8 + filepath_len]
        asset_offset = o + 8 + filepath_len + 1
        keygen = xnasamx(keygen, asset_len + 1)
        assets_by_hash[fp_hash] = (asset_offset, asset_len, is_encrypted)
        o = asset_offset + asset_len

    shader_paths = sorted(set(re.findall(rb'spel2:/Data/ShadersNX/[a-zA-Z0-9_]+\.nvn', img)))
    out = []
    for sp in shader_paths:
        h = hash_filepath_v2(keygen, sp)
        if h not in assets_by_hash: continue
        off, length, enc = assets_by_hash[h]
        enc_data = img[off:off + length]
        dec_data = decrypt_v2(keygen, sp, enc_data) if enc else enc_data
        raw = zstd.decompress(dec_data)
        code_len = struct.unpack_from('<I', raw, 0)[0]
        code = raw[4:4 + code_len]
        ctl_len_val = struct.unpack_from('<I', raw, 4 + code_len)[0]
        ctl = raw[8 + code_len:8 + code_len + ctl_len_val]
        st = ss.glslc_stage(ctl, code)
        if not st: continue
        err = ss.check(sp.decode('latin1'), st, ctl, code)
        if err: ss.red(f'{sp.decode("latin1")}: {err}')
        out.append((f'{label}#SPEL2:{sp.decode("latin1")}', st, ctl, code))
    return out
