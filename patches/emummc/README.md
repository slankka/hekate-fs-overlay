# Relocatable emuMMC KIPM patch

Hekate FS Overlay prepends an overlay image before the existing FS process.
When emuMMC is enabled, that also moves the injected emuMMC image away from
the beginning of the process RX mapping. The accompanying patch makes emuMMC
derive its runtime base from its own `_start` symbol so it remains valid after
that relocation.

The patch also replaces the legacy Python 2.7 conversion step with a validated
Python 3 converter and adds a reproducible `kipm` build target.

## Upstream base

- Project: [Atmosphere-NX/Atmosphere](https://github.com/Atmosphere-NX/Atmosphere)
- Tag: `1.11.2`
- Commit: `5388824be146a89619e8d641acd64599cf1c5f62`

The patch changes only these emuMMC files:

```text
emummc/Makefile
emummc/build.sh
emummc/source/main.c
emummc/tools/kip1converter.py
```

## Apply and build

From a clean checkout of Atmosphere `1.11.2`:

```sh
git apply /path/to/atmosphere-1.11.2-fs-overlay.patch
cd emummc
./build.sh
```

Requirements are devkitPro with devkitA64 and libnx, `hactool`, GNU Make, and
Python 3. The build produces `emummc/emummc.kipm`.

Install the resulting file at:

```text
bootloader/sys/emummc.kipm
```

This KIPM is required by the current `fsoverlay=` implementation even for
sysMMC boots because its FS-compatible kernel capabilities are copied into the
merged KIP. It is an injection blob consumed by Hekate and must not be loaded
with the `kip1=` configuration key.

## License

The patched emuMMC source remains under its upstream GNU GPL version 2 license.
Upstream copyright and attribution notices are retained by the patch.
