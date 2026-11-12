# hekate-fs-overlay — fs-patched (hekate v6.5.5)

**Release assets:** `hekate-fs-overlay-v6.5.5-fs-patched.zip` (full) · `hekate-fs-overlay-v6.5.5-fs-patched-minimal.zip` (minimal) · `hekate-fs-overlay-v6.5.5-fs-patched.bin` (standalone payload) · `hekate-fs-overlay-v6.5.5-fs-patched-ram8GB.bin` (8 GB DRAM variant)

Unofficial fork of [CTCaer/hekate](https://github.com/CTCaer/hekate) that adds an
`fsoverlay=` boot key for **prepending an FS Overlay KIP** to the FS process image.
Not maintained or endorsed by the upstream Hekate project.

---

## What's New

- **Rebased onto hekate v6.5.5 / Nyx v1.9.5** (previous release was on v6.5.4 / Nyx 1.9.4).
- **Carries upstream's HOS 23.5.0 support**, which is the entire functional delta of
  this rebase:
  - `pkg1` build-timestamp table gains `"20260930"` (23.5.0+), so 23.5.0 package1 is
    now identifiable;
  - new `_fs_nogc_2350` / `_fs_nogc_2350_exfat` FS patch sets plus the two new FS
    SHA-256 IDs (`01ED6B87…` FAT32, `7B902837…` exFAT);
  - Nyx fuse table gains `case 25: "23.5.0+"`.
- **The FS Overlay patch itself is unchanged.** `hos_config.c`, `pkg2.h`,
  `patches/emummc/*` and `res/hekate_ipl_template.ini` are byte-identical to the
  previous (v6.5.4) release; `pkg2.c` / `hos.c` differ only where upstream added its
  23.5.0 entries. The `fsoverlay=` mechanism carries **no FS version logic**, so it
  works on 23.5.0 automatically.

### Upstream 23.5.0 nogc offsets, independently confirmed

The offsets upstream added were re-derived here from the actual 23.5.0 `FS.kip1`
(extracted from `BootImagePackageExFAT 010000000000081b`) and match byte-for-byte.
Note hekate uses **`.text`-relative** offsets, while Atmosphere's fusee table uses
**file** offsets (`.text` + 0x100):

| Purpose | hekate (text-rel) | fusee (file) | bytes at site |
|---|---|---|---|
| NOINIT (exFAT) | `0x191450` | `0x191550` | `fd 7b bd a9 f5 0b 00 f9` |
| SDMMC3 #1 | `0x1BE7CD` | `0x1BE8CD` | `40 80 52 61 01 ae 72 02` |
| SDMMC3 #2 | `0x1BE7E5` | `0x1BE8E5` | `40 80 52 60 01 ae 72 08` |
| NOINIT (FAT32) | `0x186250` | — | `fd 7b bd a9 f5 0b 00 f9` |
| SDMMC3 #1 (FAT32) | `0x1B35CD` | — | `40 80 52 61 01 ae 72 02` |
| SDMMC3 #2 (FAT32) | `0x1B35E5` | — | `40 80 52 60 01 ae 72 08` |

The FAT32 pair also confirms upstream's post-release fix (`184584a9` → merged as
`8e1392df`), which corrected the first FAT32 SDMMC3 offset from `0x1BE7CD`
(exFAT's) to `0x1B35CD`.

## What it does

`fsoverlay=` merges an unpacked FS-title-ID KIP into the existing FS process,
producing this layout:

```text
FS overlay  ->  emuMMC (when enabled)  ->  original FS
```

The overlay is prepended **after** the normal kip1 patches and emuMMC injection,
so it must be an unpacked FS-title-ID KIP with a page-aligned memory extent.

## Requirements

- **`bootloader/sys/emummc.kipm` is mandatory** — required even for sysMMC boots,
  because its FS-compatible kernel capabilities are copied into the merged KIP.
  It must be the **relocatable** build (derives its base from `_start`); the stock
  Atmosphere emuMMC assumes the standalone layout and will not fit after the overlay
  shifts it. The matching source patch is in
  [`patches/emummc`](https://github.com/slankka/hekate-fs-overlay/tree/master/patches/emummc).

## Installation

### Package contents

The **full** package is a complete Hekate v6.5.5 file set: every component this fork
does not modify is the **byte-identical upstream v6.5.5 binary**, plus

```text
payload.bin                                        SD-root injection file (= update.bin)
hekate_fs_overlay_v6.5.5-fs-patched.bin            this fork's payload (same image)
atmosphere/reboot_payload.bin                      used when rebooting to payload
bootloader/update.bin                              chain-loaded on every boot
bootloader/fsoverlays/fs_codecvt_dual_unpacked.kip FS Overlay KIP
bootloader/sys/emummc.kipm                         relocatable build (required)
INSTALL.md
```

The upstream `hekate_ctcaer_6.5.5.bin` is **deliberately absent** — it is the
unpatched payload and silently ignores `fsoverlay=`.

The **minimal** package contains only the binaries this fork changes:

```text
payload.bin
hekate_fs_overlay_v6.5.5-fs-patched.bin
atmosphere/reboot_payload.bin
bootloader/update.bin
bootloader/sys/emummc.kipm
INSTALL.md
```

Use it if you already run upstream Hekate v6.5.5. It ships **no** `nyx.bin` /
`libsys_*.bso` / `res.pak` / `thk.bin` / `l4t/*` (unmodified, keep upstream's) and
**no** FS Overlay KIP (get `fs_codecvt_dual_unpacked.kip` from the nx-fs-utf8 release
and put it in `bootloader/fsoverlays/`).

### `bootloader/hekate_ipl.ini`

```ini
[CFW - FS UTF-8]
pkg3=atmosphere/package3
fsoverlay=bootloader/fsoverlays/fs_codecvt_dual_unpacked.kip
emummcforce=1
```

The `fsoverlay=` path **must match the actual file name** in `bootloader/fsoverlays/`.

`fsoverlay=` is mutually exclusive with `stock=1`.

---

## Overwrite all payload copies

> [!IMPORTANT]
> Hekate chain-loads `bootloader/update.bin` on every boot, and only replaces it
> when the running payload is **strictly newer**. This fork reports the **same
> version number as upstream (6.5.5)**, so it cannot win that comparison — a stale
> copy on the SD card would silently keep running and your `fsoverlay=` entry would
> be ignored.
>
> Overwrite **all** of these with this build's payload (they are the same image):
>
> - `bootloader/update.bin`
> - `atmosphere/reboot_payload.bin`
> - `payload.bin` (SD-root injection)
> - your PC / USB injector payload, if you boot via USB

> [!NOTE]
> Why not just bump the hotfix number? hekate packs its version as four single-byte
> ASCII digits (`loader/loader.c`: `MJ+'0' | (MN+'0')<<8 | (HF+'0')<<16 | RL<<24`),
> so a hotfix ≥ 10 is not representable — it encodes as a punctuation byte and both
> the anti-downgrade comparison and Nyx's version display break. The fork therefore
> stays on upstream's number and relies on the checklist above.

Keep your existing `bootloader/nyx.ini` (it stores the RTC `timeoffset`). This release
intentionally does **not** ship `hekate_ipl.ini`, so your configuration is untouched.

### 8 GB DRAM consoles

`hekate-fs-overlay-v6.5.5-fs-patched-ram8GB.bin` is the same payload with
`rsvd_flags = RSVD_FLAG_DRAM_8GB` (a single byte at `0x122`). Load it as the **first**
payload (RCM / `payload.bin`); it propagates the RAM configuration into
`bootloader/update.bin` on its own, so the other copies do not need the variant.
Never use it on a stock 4 GB console.

---

## Checksums

```
File:    hekate-fs-overlay-v6.5.5-fs-patched.zip
Size:    1,162,330 bytes
SHA-256: 19c893fa1879951541b75a393ecdbe787af9862f94b173826a582ff197df9df7

File:    hekate-fs-overlay-v6.5.5-fs-patched-minimal.zip
Size:    452,462 bytes
SHA-256: 9dfdfd9ed0ee17f1b2966bd399bc88313cb980c0851bc06b3b9f5057a7b4b561

File:    hekate-fs-overlay-v6.5.5-fs-patched.bin
Size:    111,688 bytes
SHA-256: 003727a024dd422c11fc3b854be52e49b7227f1ff7fb85911c3185beef4684c6

File:    hekate-fs-overlay-v6.5.5-fs-patched-ram8GB.bin
Size:    111,688 bytes
SHA-256: 605d7f398cb7c29c0ca9fa36fc30e80f2dd537479755c7632abb9ab4a4d750fc
```

Bundled within both packages:

```
File:    bootloader/sys/emummc.kipm
Size:    368,768 bytes
SHA-256: 0a9f9704f357146658e883b039257a046f21fdb366777d6e055ae0732e1f5ca8

File:    bootloader/fsoverlays/fs_codecvt_dual_unpacked.kip   (full package only)
Size:    11,316 bytes
SHA-256: 5dd489666df37c59de51463cb84334350da6c6b8c4fd52992a77cc21df133972
```

---

## Verify

Boot a title that reads a CJK path, or use the `test_program` homebrew client from
[nx-fs-utf8](https://github.com/slankka/nx-fs-utf8/releases): it creates and reads
`sdmc:/ROM/中文目录/往返测试.txt` and confirms both Chinese names appear through
directory enumeration.

If something is wrong, simply remove the `fsoverlay=` line — the stock FS image is
untouched.

---

## Notes & known limitations

- **Payload is not byte-reproducible with upstream.** The fork's payload is built
  locally with devkitARM r66 / GCC 15.1.0, whereas upstream ships GCC 11.2.0
  binaries. This affects code layout only, not behaviour: the same source built with
  the local toolchain reproduces upstream's unmodified components byte-for-byte,
  confirming the fork's patch is the only functional delta.
- **Unmodified components are shipped as upstream binaries**, not local rebuilds, so
  `nyx.bin` / `libsys_lp0.bso` / `libsys_minerva.bso` / `res.pak` / `thk.bin` / `l4t/*`
  are the exact CTCaer-tested v6.5.5 images.
- The FS Overlay KIP bundled in the full package is `fs_codecvt_dual_unpacked.kip`
  from nx-fs-utf8. The overlay is a separate project with its own release cadence and
  support matrix; see its release notes.
- ⚠️ **emuMMC + HOS 23.5.0 emits an out-of-range FS version ID.** This is upstream
  behaviour, not introduced by this fork. hekate encodes the matched FS entry index
  into `emu_cfg.fs_ver` (`bootloader/hos/pkg2.c`: `idx - 1 - (idx > 17 ? 2 : 0)`).
  With 78 FS entries, 23.5.0 maps to 73/74, while Atmosphere's `FS_VER_MAX` is 73
  (`emummc/source/FS/FS_versions.h`). `get_fs_offsets()` then hits
  `fatal_abort(Fatal_UnknownVersion)`. **This only affects the emuMMC KIPM path**
  (i.e. `emummcforce=1`); the `fsoverlay=` feature itself does not read `fs_ver`.
  Until Atmosphere adds `FS_VER_23_5_0` / `FS_VER_23_5_0_EXFAT`, use `fsoverlay=`
  on **sysMMC**, or run 23.5.0 emuMMC without `emummcforce`.

## Attribution & License

Upstream Hekate is by CTCaer, under GNU GPL v2. The relocatable emuMMC patch remains
under GPL v2 with upstream copyright notices retained. HOS 23.5.0 pkg1 IDs, nogc
patches and FS SHA-256 IDs come from upstream v6.5.5.
