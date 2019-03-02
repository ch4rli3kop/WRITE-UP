#!/usr/bin/python

import string
import random
import _7amebox_patched_debug
from hashlib import sha1

firmware = 'tiny_adventure.firm'

emu = _7amebox_patched_debug.EMU()
emu.filesystem.load_file('flag')
emu.filesystem.load_file('stage.map')
emu.register.init_register()
emu.init_pipeline()
emu.set_mitigation(nx=True)
emu.load_firmware(firmware)
emu.execute()
