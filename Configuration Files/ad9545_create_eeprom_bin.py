# -*- coding: utf-8 -*-
"""
This program creates a bin file starting from a cso configuration file
It writes 21 registers from address 0x2000 instead of only 20. In this way, when
the AD9545 uploads its memory into the EEPROM, it creates the EEPROM image correctly
(this deals with the EEPROM workaround)
The registers at address 0x2200 have the 0x2204 location unused. The program
was modified to allow for 8 contiguous registers at this location (previously the 
program was set for only 7, missing the register at 0x2207 location)

@author: NWeeks
"""
import sys, struct
import xml.etree.ElementTree as ET

from bitarray import bitarray as BitArray

class crc(object):
  __slots__ = ('val', 'polynomial', 'output')
  def __init__(self):
    self.val        = BitArray(0, 32)
    self.polynomial = 0x02608edb
    self.output     = False
    pass
  
  def update(self, val): # Updates MSB to LSB of a specific byte
    xor = (self.val[31] ^ val)
    if (xor):
      self.val[0:31] = (self.val[0:31] ^ self.polynomial)
    self.val[1:31]  = self.val[0:30]
    self.val[0]     = xor
    if (self.output):
      return hex(self.val.value)

file_output = True
root        = './'
fn          = '12kHz_LED.cso' # Replace with a proper cso file


# Populate list of default register data
default_addr = []
default_data = []
raw = [x.strip('\n').strip('\r').split(' ')[0] for x in open('./defaults.txt', 'r+').readlines() if x.startswith('0x')]
for ln in raw:
  addr, value = [int(x, 16) for x in ln.split(',')]
  default_addr.append(addr)
  default_data.append((addr, value))
  pass

# Read specified input configuration file
raw     = [x.strip('\n').strip('\r') for x in open(root + fn,'r').readlines()]
address = []
data    = []
ext     = fn.split('.')[-1].lower()
if (ext == 'cso'):
  vals = [ET.fromstring(x.strip(' ')) for x in raw if x.strip(' ').startswith('<Register Address')]
  for val in vals:
    addr = int(val.attrib['Address'], 16)
    value = int(val.attrib['Value'], 16)
#    value, addr = list(map(int, val.attrib.values(), [16, 16]))
    address.append(addr)
    data.append((addr, value))
else:
  try:
    start = raw.index('<registers>') + 2
    stop  = raw.index('</registers>')  
  except ValueError:
    try:
      start = raw.index('Address,Data') + 1
    except ValueError:
      start = 0
    stop  = len(raw)
  for i in range(start, stop, 1):
    temp = raw[i].split(',')
    address.append(int(temp[0].strip('\t'), 16))
    data.append((int(temp[0].strip('\t'), 16), int(temp[1].strip('\t'), 16)))
    pass
  pass

opcode_lib={0x80:[(0xf,0,True)],
            0x90:[(0x2000,1,True),(0xf,0,True),(0x2000,1,False),(0xf,0,True)],
            0x91:[(0x2000,2,True),(0xf,0,True),(0x2000,2,False),(0xf,0,True)], 
            0x92:[(0x2100,1,True),(0x2200,1,True),(0xf,0,True),(0x2100,1,False),(0x2200,1,False),(0xf,0,True)],
            0x93:[(0x2100,1,True),(0xf,0,True),(0x2100,1,False),(0xf,0,True)],
            0x94:[(0x2200,1,True),(0xf,0,True),(0x2200,1,False),(0xf,0,True)],
            0xa0:[(0x2000,3,True),(0xf,0,True),(0x2000,3,False),(0xf,0,True)],
            0xa1:[(0x2101,3,True),(0xf,0,True),(0x2101,3,False),(0xf,0,True)],
            0xa2:[(0x2201,3,True),(0xf,0,True),(0x2201,32,False),(0xf,0,True)]}

#Sans channel specific initialization and ending op-code
sequence = [
[3,   0x20, 0x00],   # EEPROM Scratchpad Regs
[26,  0x00, 0x01],   # Mpins and IRQ
[9,   0x00, 0x02],   # SysClk
[0x80], # IO Update
[0x91], # Cal sysclk
[28,  0x80, 0x02], # Sysclk comp
[7,   0x00, 0x03], # References General
[20,  0x00, 0x04], # RefA config
[20,  0x20, 0x04], # RefAA config
[20,  0x40, 0x04], # RefB config
[20,  0x60, 0x04], # RefBB config
[17,  0x00, 0x08], # Source Profile 0
[17,  0x20, 0x08], # Source Profile 1
[17,  0x40, 0x08], # Source Profile 2
[17,  0x60, 0x08], # Source Profile 3
[17,  0x80, 0x08], # Source Profile 4
[17,  0xa0, 0x08], # Source Profile 5
[17,  0xc0, 0x08], # Source Profile 6
[17,  0xe0, 0x08], # Source Profile 7
[23,  0x00, 0x0c], # DPLL LF base coefs
[43,  0x00, 0x10], # DPLL0 general settings
[3,   0x80, 0x10], # APLL0 config and output drivers
[28,  0xc0, 0x10], # Dist 0 General
[53,  0x00, 0x11], # Dist Channels
[23,  0x00, 0x12], # Translation Profile 0-0
[23,  0x20, 0x12], # Translation Profile 0-1
[23,  0x40, 0x12], # Translation Profile 0-2
[23,  0x60, 0x12], # Translation Profile 0-3
[23,  0x80, 0x12], # Translation Profile 0-4
[23,  0xa0, 0x12], # Translation Profile 0-5
[43,  0x00, 0x14], # DPLL1 general settings
[3,   0x80, 0x14], # APLL1 General
[28,  0xc0, 0x14], # Dist 1 General
[35,  0x00, 0x15], # Dist Channels
[23,  0x00, 0x16], # Translation Profile 1-0
[23,  0x20, 0x16], # Translation Profile 1-1
[23,  0x40, 0x16], # Translation Profile 1-2
[23,  0x60, 0x16], # Translation Profile 1-3
[23,  0x80, 0x16], # Translation Profile 1-4
[23,  0xa0, 0x16], # Translation Profile 1-5
[21,  0x00, 0x20], # Operational Controls - Common !!!One byte added for the workaround
[7,   0x00, 0x21], # Operational Controls - Channel 0
[7,   0x00, 0x22], # Operational Controls - Channel 1 !!!!One byte added to make registers contiguous
[30,  0x00, 0x28], # AUXNCO 0
[30,  0x40, 0x28], # AUXNCO 1
[6,   0x00, 0x29], # Temperature Sensor
[23,  0x00, 0x2a], # AUXTDCs
[0x80], # IO Update
[0x92], # Cal All Aplls
[0xff]
]

# Create list to house EEPROM data sequence
burn = []

# Add Header sequence here [consists of data from R0x0003, R0x0004, R0x0005, R0x0006, R0x000C, R0x000D]
for each in [0x3, 0x4, 0x5, 0x6, 0xc, 0xd]:
  index = address.index(each)
  burn.append(data[index][1])
  pass

#collect data from dut to include in the burn sequence
for i in range(len(sequence)):
  burn += sequence[i]
  if sequence[i][0] < 0x80:
    # In this case we need to append register data
    for j in range(sequence[i][0] + 1):
      reg = (sequence[i][2] << 8) + sequence[i][1]
      try:
        index = address.index(reg + j)
        burn.append(data[index][1])
      except ValueError:
        try:
          index = default_addr.index(reg + j)
          burn.append(default_data[index][1])
          sys.stdout.write("Missing data for Register: " + hex(reg + j) + '.\r\n Using Default Data.\r\n')
        except ValueError:
          sys.stdout.write("Requested Register: " + hex(reg + j) + ' does not exist.\r\n Using Data = 0x00.\r\n')
          burn.append(0)
      pass
    pass
  pass

# Add CRC checksum here
checksum = crc()
for each in burn:
  temp = BitArray(each, 8)
  for i in range(7,-1,-1):
    checksum.update(temp[i])
  pass
burn.append(int(checksum.val[24:31].value))
burn.append(int(checksum.val[16:23].value))
burn.append(int(checksum.val[8:15].value))
burn.append(int(checksum.val[0:7].value))

# Add null op-codes 
for i in range(0, ((256 - len(burn)) % 256), 1):
  burn.append(0xff)
  pass

# conditionally output .bin file
if file_output:
  _str = b''
  for i in range(0, len(burn), 1):
    _str += struct.pack("B", burn[i])
#  _str = ''.join(chr(x) for x in burn)
  f = open(root + fn.split('.')[0] + '.bin', 'wb')
  f.writelines([_str])
  f.close()
  pass

print("Checksum is: {0}".format(hex(checksum.val.value)))