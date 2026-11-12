# IPL Version.
# Kept identical to upstream on purpose.
#
# hekate packs its version as four single-byte ASCII digits
# (loader/loader.c: MJ+'0' | (MN+'0')<<8 | (HF+'0')<<16 | RL<<24), so a hotfix
# of 10 or more is NOT representable -- it would encode as a punctuation byte.
# The fork therefore does not try to out-rank upstream by version number; the
# update is propagated by replacing all copies of the payload on the SD card
# (payload.bin, bootloader/update.bin, atmosphere/reboot_payload.bin).
BLVERSION_MAJOR := 6
BLVERSION_MINOR := 5
BLVERSION_HOTFX := 5
BLVERSION_REL   := 0

# Nyx Version.
NYXVERSION_MAJOR := 1
NYXVERSION_MINOR := 9
NYXVERSION_HOTFX := 5
NYXVERSION_REL   := 0
