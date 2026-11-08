#!/usr/bin/env python3
"""Test EOS Handle getter null-dereference and Lobby callback registration in TMNT."""
import ctypes, os, struct, subprocess, sys, unittest

class TestTMNTEOS(unittest.TestCase):
    def test_handle_inner_null(self):
        """Handle.get_InnerHandle (main+0x6d1b40) must safely handle a null Handle object without SIGSEGV."""
        test_script = '''
import ctypes, struct, sys

libc = ctypes.CDLL(None)
PROT_READ, PROT_WRITE, PROT_EXEC = 1, 2, 4
MAP_ANON, MAP_PRIVATE = 0x1000, 0x0002

libc.mmap.restype = ctypes.c_void_p
libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_longlong]
libc.mprotect.restype = ctypes.c_int
libc.mprotect.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
libc.sys_icache_invalidate.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

path = "/Users/balkrishan/Downloads/TMNT/Teenage Mutant Ninja Turtles - Shredder's Revenge.app/Contents/Resources/dm/main.patched.bin"
with open(path, "rb") as f:
    f.seek(0x6d1b40)
    code = f.read(0x20)

addr = libc.mmap(0, 4096, PROT_READ | PROT_WRITE, MAP_ANON | MAP_PRIVATE, -1, 0)
ctypes.memmove(addr, code, len(code))
libc.mprotect(addr, 4096, PROT_READ | PROT_EXEC)
libc.sys_icache_invalidate(addr, len(code))

fn = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)(addr)

# Test with null
res0 = fn(0)
assert res0 is None or res0 == 0, f"Expected 0 for null handle, got {res0}"

# Test with non-null
buf = ctypes.create_string_buffer(32)
struct.pack_into("<Q", buf, 0x10, 0x12345678)
res_valid = fn(ctypes.addressof(buf))
assert res_valid == 0x12345678, f"Expected 0x12345678, got {hex(res_valid)}"

sys.exit(0)
'''
        p = subprocess.run([sys.executable, '-c', test_script], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"Process crashed with returncode {p.returncode}. Stderr: {p.stderr}")

if __name__ == '__main__':
    unittest.main()
