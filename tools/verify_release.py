#!/usr/bin/env python3
"""Verify the built FS overlay KIP embeds the validated 23.5.0 offset table.

Also checks the emuMMC fs_ver encoding stays inside Atmosphere's FS_VER range.
"""
import re
import struct
import sys
from pathlib import Path

KIP = Path(r"F:\nx_fscodecvt\fs_codecvt_dual_unpacked.kip")
HEKATE_PATCHES = Path(r"F:\hekate\bootloader\hos\pkg2_patches.inl")
ATMO_VERSIONS = Path(r"F:\Atmosphere\emummc\source\FS\FS_versions.h")

# Validated 23.5.0 entry: codecvt[6], sanitize[3], dir_hook/reject/ascii/scan.
WANT = [0x114560, 0x1146B0, 0x114880, 0x1148C0, 0x114910, 0x114920,
        0x10B7C4, 0x10BA70, 0x10C5C4,
        0xEA080, 0xEA100, 0xEA084, 0xEA0C8]


def check_overlay():
    d = KIP.read_bytes()
    _, _, comp_t, _ = struct.unpack_from("<IIII", d, 0x20)
    _, _, comp_ro, _ = struct.unpack_from("<IIII", d, 0x20 + 0x10)
    ro_start = 0x100 + comp_t
    ro = d[ro_start:ro_start + comp_ro]

    pat = b"".join(struct.pack("<I", v) for v in WANT)
    hits, i = [], ro.find(pat)
    while i >= 0:
        hits.append(i)
        i = ro.find(pat, i + 4)

    print(f"overlay KIP: {len(d)} B, rodata 0x{ro_start:X}..0x{ro_start + comp_ro:X}")
    if not hits:
        print("  !! 23.5.0 table NOT found -- overlay would not hook 23.5.0")
        return False
    print(f"  23.5.0 table at rodata+0x{hits[0]:X} (KIP file 0x{ro_start + hits[0]:X})")
    return True


def check_fsver():
    names = [ln.strip() for ln in ATMO_VERSIONS.read_text(encoding="utf-8", errors="ignore").splitlines()
             if ln.strip().startswith("FS_VER_")]
    valid_max = len(names) - 2          # FS_VER_MAX itself excluded
    rows = [ln.strip() for ln in HEKATE_PATCHES.read_text(encoding="utf-8", errors="ignore").splitlines()
            if ln.strip().startswith('{ "FS", "')]

    def enc(i):
        return i - 1 - (2 if i > 17 else 0) if i else 0

    print(f"\nemuMMC fs_ver: Atmosphere valid range 0..{valid_max}, hekate has {len(rows)} FS entries")
    ok = True
    for idx, line in enumerate(rows):
        m = re.search(r"//\s*(.*)$", line)
        label = m.group(1) if m else ""
        if "23.5.0" not in label:
            continue
        v = enc(idx)
        good = 0 <= v <= valid_max
        print(f"  {'OK ' if good else 'OOB'} idx {idx} -> fs_ver {v}  ({label})")
        ok &= good
    return ok


a = check_overlay()
b = check_fsver()
print()
sys.exit(0 if a and b else 1)
