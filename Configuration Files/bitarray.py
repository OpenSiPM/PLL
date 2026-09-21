# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 09:57:14 2019

@author: NWeeks
"""

class bitarray(object):
  def __init__(self, val, bits=None):
    setattr(self, '_index', 0)
    if (type(val) is list):
      setattr(self, '_width', (len(val) - 1))
      setattr(self, '_list', val)
    elif (type(val) is bitarray):
      setattr(self, '_width', val._width)
      setattr(self, '_list', val._list)
    else:
      tmp = bin(val)[2:].zfill(0 if (bits is None) else (bits - 1))
      setattr(self, '_width', (len(tmp)))
      tmp = [int(x, 2) for x in bin(val)[2:].zfill(self.width)]
      tmp.reverse()
      setattr(self, '_list', tmp)
    pass
  
  @property
  def value(self):
    tmp = 0
    for i in range(self._width, -1,-1):
      tmp <<= 1
      tmp |= self._list[i]
      pass
    return tmp
  
  @property
  def width(self):
    return (self._width + 1)
  
  def __xor__(self, val):
    val = bitarray(val)
    l = max([self.width, val.width])
    return bitarray([(self[i] ^ val[i]) for i in range(l)])
  
  def __iter__(self):
    self._index = 0
    return self
  
  def __next__(self):
    if (self._index <= self._width):
      result = self._list[self._index]
      self._index += 1
      return result
    else:
      raise StopIteration
  
  def __extend(self, key):
    _i = ((key.stop) if (type(key) is slice) else key)
    if (_i > self._width):
      self._list += [0] * (_i - self._width)
      self._width = _i
    pass
  
  def __getitem__(self, key):
    self.__extend(key)
    if (type(key) is slice):
      return bitarray(self._list[key.start:(key.stop + 1):key.step])
    else:
      return self._list[key]
  
  def __setitem__(self, key, val):
    self.__extend(key)
    if (type(key) is slice):
      self._list[key.start:(key.stop + 1):key.step] = \
            bitarray(val, ((key.stop + 1) - key.start))._list
    else:
      self._list[key] = val
  
  def __repr__(self):
    return "bitarray({0}, {1})".format(hex(self.value), self.width)