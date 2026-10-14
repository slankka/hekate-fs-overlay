# hekate-fs-overlay — fs-patched (hekate v6.5.4)

**Release assets:** `hekate-fs-overlay-v6.5.4-fs-patched.zip` (full) · `hekate-fs-overlay-v6.5.4-fs-patched-minimal.zip` (minimal) · `hekate-fs-overlay-v6.5.4-fs-patched.bin` (standalone payload)

Unofficial fork of [CTCaer/hekate](https://github.com/CTCaer/hekate) that adds an
`fsoverlay=` boot key for **prepending an FS Overlay KIP** to the FS process image.
Not maintained or endorsed by the upstream Hekate project.

---

## What's New

- **Rebased onto hekate v6.5.4 / Nyx v1.9.4** (previous release was on v6.5.3 / Nyx 1.9.3).
- **Carries upstream's HOS 23.0.0 support** — the 23.0.0 master KEK seeds (T210 and
  T210B01) and the accompanying pkg2 patches. This is the only functional change
  inherited from upstream.
- **The FS Overlay patch itself is unchanged** from the previous (v6.5.3) release: `hos_config.c`, `pkg2.c`,
  `pkg2.h` and the boot-entry template are byte-identical to the previous release.
  `hos.c` / `hos.h` differ only where upstream added its 23.0.0 entries.

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
- The loader must be **this fork** — stock Hekate has no `fsoverlay=` key.
- **Not supported with `stock=1`.**

> **This is not a standalone Initial Process KIP.** Do **not** load the overlay with
> the `kip1=` key — that is the stock mechanism and cannot merge an FS overlay.

## Installation

### Full package

A complete Hekate v6.5.4 file set. Every component this fork does **not** modify is
the **byte-identical upstream v6.5.4 binary**:

```text
payload.bin                                       SD-root injection file (= update.bin)
hekate_fs_overlay_v6.5.4-fs-patched.bin           this fork's payload (same image)
atmosphere/reboot_payload.bin                     used when rebooting to payload
bootloader/update.bin                             chain-loaded on every boot
bootloader/fsoverlays/                            place FS Overlay KIPs here
bootloader/ini/  bootloader/payloads/             empty, for your own entries
bootloader/res/icon_*.bmp                         upstream v6.5.4
bootloader/sys/emummc.kipm                        relocatable build (required)
bootloader/sys/libsys_lp0.bso                     upstream v6.5.4
bootloader/sys/libsys_minerva.bso                 upstream v6.5.4
bootloader/sys/nyx.bin                            upstream Nyx v1.9.4
bootloader/sys/res.pak  bootloader/sys/thk.bin    upstream v6.5.4
bootloader/sys/l4t/                               upstream v6.5.4 (6 files)
INSTALL.md
```

Copy the contents to the **root of your SD card**, keeping the directory structure.

> The upstream `hekate_ctcaer_6.5.4.bin` is **deliberately absent**. It is the
> **unpatched** payload and does **not** support `fsoverlay=`; injecting it would boot
> a Hekate that silently ignores your overlay. Use
> `hekate_fs_overlay_v6.5.4-fs-patched.bin` instead.

### Minimal package

Only the binaries this fork actually changes:

```text
payload.bin
atmosphere/reboot_payload.bin
bootloader/update.bin
bootloader/sys/emummc.kipm
INSTALL.md
```

Use this if you already run upstream Hekate v6.5.4 and only need the overlay support.
Do **not** ship the upstream `nyx.bin` / `libsys_*.bso` / `res.pak` / `thk.bin` / `l4t/*`
in this package — they are unmodified and must come from upstream. It also does **not**
contain an FS Overlay KIP; get one from
[nx-fs-utf8 releases](https://github.com/slankka/nx-fs-utf8/releases) and put it in
`bootloader/fsoverlays/`.

### `bootloader/hekate_ipl.ini`

```ini
[CFW - FS UTF-8]
pkg3=atmosphere/package3
fsoverlay=bootloader/fsoverlays/fs_codecvt_dual_unpacked.kip
emummcforce=1
```

The `fsoverlay=` path **must match the actual file name** in `bootloader/fsoverlays/`.

---

## Overwrite all payload copies

> [!IMPORTANT]
> Hekate chain-loads `bootloader/update.bin` on every boot. If the Hekate already
> installed on your SD card reports a **higher** version, Hekate's anti-downgrade
> logic rewrites `update.bin` / `reboot_payload.bin` back to itself, and this build
> never takes effect — your `fsoverlay=` entry is silently ignored.
>
> So overwrite **all** of these with this build's payload (they are the same image):
>
> - `bootloader/update.bin`
> - `atmosphere/reboot_payload.bin`
> - `payload.bin` (SD-root injection)
> - your PC / USB injector payload, if you boot via USB

> [!NOTE]
> The fork reports the **same version number as upstream** (6.5.4), so Hekate cannot
> distinguish this build from stock by version alone. If any copy is left as a
> different build, behaviour depends on that stale copy — hence the checklist above.

Keep your existing `bootloader/nyx.ini` (it stores the RTC `timeoffset`). This release
intentionally does **not** ship `hekate_ipl.ini`, so your configuration is untouched.

---

## Verify

Boot a title that reads a CJK path, or use the `test_program` homebrew client from
[nx-fs-utf8](https://github.com/slankka/nx-fs-utf8/releases): it creates and reads
`sdmc:/ROM/中文目录/往返测试.txt` and confirms both Chinese names appear through
directory enumeration.

If something is wrong, simply remove the `fsoverlay=` line — the stock FS image is
untouched.

---

## Checksums

```
File:    hekate-fs-overlay-v6.5.4-fs-patched.zip
Size:    1,163,430 bytes
SHA-256: 665f04bd4a36bf1660cd87edb9045261549d76f36110753f91c2bbff2a7a82be

File:    hekate-fs-overlay-v6.5.4-fs-patched-minimal.zip
Size:    357,598 bytes
SHA-256: a83e8b832ed136d887304724b08d5b0e22f2da6ec5f4a538e8c8fd602a8561b2

File:    hekate-fs-overlay-v6.5.4-fs-patched.bin
Size:    111,592 bytes
SHA-256: fc2fbf806580f286aa7a54810606521478cfae3f75bc758e3a13547981a1abea
```

Bundled within both packages:

```
File:    bootloader/sys/emummc.kipm
Size:    368,768 bytes
SHA-256: c0f96732b5e011da14658186cb10277e1f0dad150168b3fdcb5f556345cccee5
```

---

## Notes & known limitations

- **Payload is not byte-reproducible here.** The fork's payload is built locally with
  devkitARM r66 / GCC 15.1.0, whereas upstream v6.5.4 ships GCC 11.2.0 binaries. This
  affects code layout only, not behaviour: the same source built with the local
  toolchain reproduces upstream's unmodified components byte-for-byte, confirming the
  fork's patch is the only functional delta.
- **Unmodified components are shipped as upstream binaries**, not local rebuilds, so
  `nyx.bin` / `libsys_lp0.bso` / `libsys_minerva.bso` / `res.pak` / `thk.bin` / `l4t/*`
  are the exact CTCaer-tested v6.5.4 images.
- The FS Overlay KIP bundled in the full package is `fs_codecvt_dual_unpacked.kip`
  v3.2.0 from nx-fs-utf8
  (`c438eb09d6ed9a921f7db834a020143811224369a4195f56d3b8a3114a0d445f`). The overlay is a
  separate project with its own release cadence and support matrix; see its release
  notes.

## Attribution & License

Upstream Hekate is by CTCaer, under GNU GPL v2. The relocatable emuMMC patch remains
under GPL v2 with upstream copyright notices retained. HOS 23.0.0 KEK seeds and pkg2
patches come from upstream v6.5.4.
