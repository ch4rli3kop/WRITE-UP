#!/usr/bin/python

import string
import random
import _7amebox_patched
from hashlib import sha1

firmware = 'mic_check.firm'

emu = _7amebox_patched.EMU()
emu.filesystem.load_file('flag')
emu.register.init_register()
emu.init_pipeline()
emu.load_firmware(firmware)
emu.disass()

