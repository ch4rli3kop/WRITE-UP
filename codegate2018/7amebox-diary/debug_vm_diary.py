#!/usr/bin/python

import string
import random
import _7amebox_patched_debug
from hashlib import sha1

firmware = 'diary.firm'

emu = _7amebox_patched_debug.EMU()
emu.filesystem.load_file('flag')
emu.register.init_register()
emu.init_pipeline()
emu.set_mitigation(nx=True)
emu.load_firmware(firmware)
#emu.set_timeout(60)
emu.execute()
