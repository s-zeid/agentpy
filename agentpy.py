#!/usr/bin/env python

"""Agent Py

(a.k.a. Clippy for Linux)

'Cuz FUCK YOU, that's why.

"""

import os
import struct
import sys
import uuid

from collections import namedtuple

class AgentCharacter(object):
 def __init__(self, filename):
  with open(filename, "rb") as f:
   parser = ACSParser(f.read())
  self.data = parser.parse()

class ACSParser(object):
 acsheader = namedtuple("acsheader", ["signature", "acscharacterinfo",
              "acsanimationinfo", "acsimageinfo", "acsaudioinfo", "SIZE"])
 acslocator = namedtuple("acslocator", ["offset", "data_size", "SIZE"])
 acscharacterinfo = namedtuple("acscharacterinfo", ["minor_version",
                     "major_version", "localizedinfo", "guid", "width",
                     "height", "transparent_color_index", "flags",
                     "animation_set_major_version",
                     "animation_set_minior_version", "voiceinfo",
                     "ballooninfo", "color_table", "tray_icon_flag",
                     "tray_icon", "stateinfo", "SIZE"])
 charflags = namedtuple("charflags", ["voice_enabled", "balloon_enabled",
              "size_to_text", "auto_hide", "auto_pace", "std_anim_set",
              "flags", "SIZE"])
 localizedinfo_locale = namedtuple("localeizedinfo_locale", ["lang_id",
                         "name", "desc", "extra", "SIZE"])
 voiceinfo = namedtuple("voiceinfo", ["tts_engine_id", "tts_mode_id",
              "speed", "pitch", "extra_data_flag", "lang_id", "lang_dialect",
              "gender", "age", "style", "SIZE"])
 ballooninfo = namedtuple("ballooninfo", ["num_lines", "chars_per_line",
                "fgcolor", "bgcolor", "border_color", "font_name",
                "font_height", "font_weight", "italic_flag", "unknown",
                "SIZE"])
 rect = namedtuple("rect", ["upper_left", "lower_right", "SIZE"])
 rgbquad = namedtuple("rgbquad", ["red", "green", "blue", "reserved", "int",
            "hex", "SIZE"])
 rgndata = namedtuple("rgndata", ["header_size", "region_type", "num_rects",
            "buffer_size", "bounds", "rects", "SIZE"])
 trayicon = namedtuple("trayicon", ["mono_size", "mono_dib",
                       "color_size", "color_dib", "SIZE"])
 state = namedtuple("state", ["name", "animations", "SIZE"])
 
 acsanimationinfo = namedtuple("acsanimationinfo", ["name", "animation_data",
                     "SIZE"])
 acsanimationinfo_data = namedtuple("acsanimationinfo_data", ["name",
                          "transition_type", "return_animation", "frames",
                          "SIZE"])
 acsframeinfo = namedtuple("acsframeinfo", ["images", "audio_index",
                 "frame_duration_csecs", "exit_to_frame_index",
                 "frame_branches", "mouth_overlays", "SIZE"])
 acsframeimage = namedtuple("acsframeimage", ["image_index", "x_offset",
                  "y_offset", "SIZE"])
 branchinfo = namedtuple("branchinfo", ["jump_to_frame_index",
               "probability_percent", "SIZE"])
 acsoverlayinfo = namedtuple("acsoverlayinfo", ["overlay_type",
                   "replace_top_image_of_frame", "image_index", "unknown",
                   "region_data_flag", "x_offset", "y_offset", "width",
                   "height", "region_data", "SIZE"])
 # "Public" methods
 def __init__(self, data):
  self.data = data
  self.size = len(data)
 def parse(self):
  return self.parse_acsheader_test()
 # Helper methods
 def check(self, offset, size):
  if self.size < (offset + size):
   raise ValueError("data must be at least %d bytes long" % (offset + size))
 # ACS-specific types
 def parse_acsheader(self):
  sig = self.parse_ulong(0)
  if sig != 0xabcdabc3:
   raise ValueError("not a valid Agent character file")
  return self.acsheader(
   sig,
   self.parse_acscharacterinfo(*self.parse_acslocator(4)),
   self.parse_acsanimationinfo_list(*self.parse_acslocator(12)),
   self.parse_acsimageinfo_list(*self.parse_acslocator(20)),
   self.parse_acsaudioinfo_list(*self.parse_acslocator(28)),
  36)
 def parse_acsheader_test(self):
  sig = self.parse_ulong(0)
  if sig != 0xabcdabc3:
   raise ValueError("not a valid Agent character file")
  return self.acsheader(
   sig,
   self.parse_acscharacterinfo(*self.parse_acslocator(4)),
   self.parse_acsanimationinfo_list(*self.parse_acslocator(12)),
   None, None,
  36)
 def parse_acslocator(self, offset):
  return self.acslocator(
   *list(struct.unpack("<LL", self.data[offset:offset+8])) + [8]
  )
 # ACS Character Info (metadata)
 def parse_acscharacterinfo(self, offset, size, *_):
  self.check(offset, size)
  start = offset
  minor_version = self.parse_ushort(offset)
  major_version = self.parse_ushort(offset + 2)
  offset += 4
  localizedinfo_location = self.parse_acslocator(offset)
  localizedinfo = self.parse_localizedinfo(localizedinfo_location)
  offset += localizedinfo_location.SIZE
  guid = self.parse_guid(offset)
  offset += 16
  width = self.parse_ushort(offset)
  height = self.parse_ushort(offset + 2)
  offset += 4
  transparent_color_index = self.parse_byte(offset)
  offset += 1
  flags = self.parse_charflags(offset)
  offset += 4
  anim_set_major = self.parse_ushort(offset)
  anim_set_minor = self.parse_ushort(offset + 2)
  offset += 4
  if flags.voice_enabled:
   voiceinfo = self.parse_voiceinfo(offset)
   offset += voiceinfo.SIZE
  else:
   voiceinfo = None
  if flags.balloon_enabled:
   ballooninfo = self.parse_ballooninfo(offset)
   offset += ballooninfo.SIZE
  else:
   ballooninfo = None
  color_table = self.parse_color_table(offset)
  offset += color_table.SIZE
  tray_icon_flag = self.parse_byte(offset)
  offset += 1
  if tray_icon_flag:
   tray_icon = self.parse_trayicon(offset)
   offset += tray_icon.SIZE
  else:
   tray_icon = None
  stateinfo = self.parse_stateinfo(offset)
  offset += stateinfo.SIZE
  if offset - start != size:
   raise ValueError("malformed acscharacterinfo")
  return self.acscharacterinfo(
   minor_version, major_version, localizedinfo, guid, width, height,
   transparent_color_index, flags, anim_set_major, anim_set_minor, voiceinfo,
   ballooninfo, color_table, tray_icon_flag, tray_icon, stateinfo,
  offset - start)
 def parse_localizedinfo(self, acslocator):
  offset = acslocator.offset
  size = acslocator.data_size
  l = self.parse_list(offset, self.parse_ushort, 2,
       self.parse_localizedinfo_locale, lambda i: i.SIZE)
  if l.SIZE != size:
   raise ValueError("malformed locale at " + hex(offset))
  ret = ACSDict([(i.lang_id, i) for i in l], l.SIZE)
  return ret
 def parse_localizedinfo_locale(self, offset):
  start = offset
  lang_id = self.parse_langid(offset)
  offset += 2
  name = self.parse_string(offset)
  offset += name.SIZE
  desc = self.parse_string(offset)
  offset += desc.SIZE
  extra = self.parse_string(offset)
  offset += extra.SIZE
  return self.localizedinfo_locale(lang_id, name, desc, extra, offset - start)
 def parse_charflags(self, offset):
  flags = self.parse_ulong(offset)
  # Seriously, Microsoft, WTF?
  voice_disabled = bool(flags >> 4 & 1)
  voice_enabled = bool(flags >> 5 & 1)
  if voice_disabled == voice_enabled:
   raise ValueError("Voice Output is both enabled and disabled")
  balloon_disabled = bool(flags >> 8 & 1)
  balloon_enabled = bool(flags >> 9 & 1)
  if balloon_disabled == balloon_enabled:
   raise ValueError("Word Balloon is both enabled and disabled")
  size_to_text = bool(flags >> 16 & 1)
  auto_hide = not bool(flags >> 17 & 1)
  auto_pace = not bool(flags >> 18 & 1)
  std_anim_set = bool(flags >> 20 & 1)
  return self.charflags(
   voice_enabled, balloon_enabled, size_to_text, auto_hide, auto_pace,
   std_anim_set, flags,
  32)
 def parse_voiceinfo(self, offset):
  start = offset
  tts_engine_id = self.parse_guid(offset)
  tts_mode_id = self.parse_guid(offset + 16)
  offset += 32
  speed = self.parse_ulong(offset)
  pitch = self.parse_ushort(offset + 4)
  extra_data_flag = self.parse_byte(offset + 6)
  offset += 7
  if extra_data_flag & 1:
   lang_id = self.parse_langid(offset)
   lang_dialect = self.parse_string(offset + 2)
   offset += lang_dialect.SIZE + 2
   gender = self.parse_ushort(offset)
   age = self.parse_ushort(offset + 2)
   style = self.parse_string(offset + 4)
   offset += style.SIZE + 4
  else:
   lang_id = lang_dialect = gender = age = style = None
  return self.voiceinfo(
   tts_engine_id, tts_mode_id, speed, pitch, extra_data_flag,
   lang_id, lang_dialect, gender, age, style,
  offset - start)
 def parse_ballooninfo(self, offset):
  start = offset
  num_lines = self.parse_byte(offset)
  chars_per_line = self.parse_byte(offset + 1)
  offset += 2
  fgcolor = self.parse_rgbquad(offset)
  offset += 4
  bgcolor = self.parse_rgbquad(offset)
  offset += 4
  border_color = self.parse_rgbquad(offset)
  offset += 4
  font_name = self.parse_string(offset)
  offset += font_name.SIZE
  font_height = self.parse_long(offset)
  font_weight = self.parse_long(offset + 4)
  italic_flag = self.parse_byte(offset + 8)
  unknown = self.parse_byte(offset + 9)
  offset += 10
  return self.ballooninfo(
   num_lines, chars_per_line, fgcolor, bgcolor, border_color, font_name,
   font_height, font_weight, italic_flag, unknown,
  offset - start)
 def parse_color_table(self, offset):
  return self.parse_list(offset, self.parse_ulong, 4,
                         self.parse_rgbquad, 4)
 def parse_trayicon(self, offset):
  start = offset
  mono_size = self.parse_ulong(offset)
  offset += 4
  mono_dib = self.data[offset:offset+mono_size]
  offset += mono_size
  color_size = self.parse_ulong(offset)
  offset += 4
  color_dib = self.data[offset:offset+color_size]
  offset += color_size
  return self.trayicon(
   mono_size, mono_dib, color_size, color_dib,
  offset - start)
 def parse_stateinfo(self, offset):
  l = self.parse_list(offset, self.parse_ushort, 2, self.parse_state,
                      lambda i: i.SIZE)
  return ACSDict([(i.name, i) for i in l], l.SIZE)
 def parse_state(self, offset):
  start = offset
  name = self.parse_string(offset)
  offset += name.SIZE
  animations = self.parse_list(offset, self.parse_ushort, 2, self.parse_string,
                               lambda i: i.SIZE)
  offset += animations.SIZE
  return self.state(name, animations, offset - start)
 # ACS Animation Info
 def parse_acsanimationinfo_list(self, offset, size, *_):
  ret = self.parse_list(offset, self.parse_ulong, 4,
                        self.parse_acsanimationinfo, lambda i: i.SIZE)
  if ret.SIZE != size:
   raise ValueError("malformed acsanimationinfo list")
  return ret
 def parse_acsanimationinfo(self, offset):
  start = offset
  name = self.parse_string(offset)
  offset += name.SIZE
  animdata_location = self.parse_acslocator(offset)
  offset += animdata_location.SIZE
  animdata = self.parse_acsanimationinfo_data(*animdata_location)
  return self.acsanimationinfo(name, animdata, offset - start)
 def parse_acsanimationinfo_data(self, offset, size, *_):
  start = offset
  name = self.parse_string(offset)
  offset += name.SIZE
  transition_type = {0: "use_return_animation",
                     1: "use_exit_branches",
                     2: None}.get(self.parse_byte(offset), None)
  offset += 1
  return_animation = self.parse_string(offset)
  offset += return_animation.SIZE
  frames = self.parse_list(offset, self.parse_ushort, 2,
                           self.parse_acsframeinfo, lambda i: i.SIZE)
  offset += frames.SIZE
  if offset - start != size:
   raise ValueError("malformed animation data")
  return self.acsanimationinfo_data(
   name, transition_type, return_animation, frames,
  size)
 def parse_acsframeinfo(self, offset):
  start = offset
  images = self.parse_list(offset, self.parse_ushort, 2,
                           self.parse_acsframeimage, lambda i: i.SIZE)
  offset += images.SIZE
  audio_index = self.parse_ushort(offset)
  frame_duration_csecs = self.parse_ushort(offset + 2)
  exit_to_frame_index = self.parse_short(offset + 4)
  offset += 6
  frame_branches = self.parse_list(offset, self.parse_byte, 1,
                                   self.parse_branchinfo, lambda i: i.SIZE)
  offset += frame_branches.SIZE
  mouth_overlays = self.parse_list(offset, self.parse_byte, 1,
                                   self.parse_acsoverlayinfo,lambda i:i.SIZE)
  offset += mouth_overlays.SIZE
  return self.acsframeinfo(
   images, audio_index, frame_duration_csecs, exit_to_frame_index,
   frame_branches, mouth_overlays,
  offset - start)
 def parse_acsframeimage(self, offset):
  # TODO: image_index should eventually be the actual image data maybe?
  image_index = self.parse_ulong(offset)
  x_offset = self.parse_short(offset + 4)
  y_offset = self.parse_short(offset + 6)
  return self.acsframeimage(image_index, x_offset, y_offset, 8)
 def parse_branchinfo(self, offset):
  jump_to_frame_index = self.parse_ushort(offset)
  probability_percent = self.parse_ushort(offset + 2)
  return self.branchinfo(jump_to_frame_index, probability_percent, 4)
 def parse_acsoverlayinfo(self, offset):
  start = offset
  overlay_type = {0: "mouth_closed", 1: "mouth_wide_open_1",
                  2: "mouth_wide_open_2", 3: "mouth_wide_open_3",
                  4: "mouth_wide_open_4", 5: "mouth_medium",
                  6: "mouth_narrow"}.get(self.parse_byte(offset), None)
  replace_top_image_of_frame = bool(self.parse_byte(offset + 1))
  offset += 2
  image_index = self.parse_ushort(offset)
  offset += 2
  unknown = self.parse_byte(offset)
  region_data_flag = bool(self.parse_byte(offset + 1))
  offset += 2
  x_offset = self.parse_short(offset)
  y_offset = self.parse_short(offset + 2)
  width = self.parse_ushort(offset + 4) * 2
  height = self.parse_ushort(offset + 6) * 2
  offset += 8
  if region_data_flag:
   region_data_size = self.parse_ulong(offset)
   offset += 4
   region_data = self.parse_rgndata(offset, region_data_size)
   offset += region_data.SIZE
  else:
   region_data = None
  return self.acsoverlayinfo(
   overlay_type, replace_top_image_of_frame, image_index, unknown,
   region_data_flag, x_offset, y_offset, width, height, region_data,
  offset - start)
 def parse_rgndata(self, offset, size):
  print "region data yay"
  start = offset
  header_size = self.parse_ulong(offset)
  region_type = self.parse_ulong(offset + 4)
  num_rects = self.parse_ulong(offset + 8)
  buffer_size = self.parse_ulong(offset + 12)
  bounds = self.parse_rect(offset + 16)
  offset += 32
  rects = self.parse_list(offset, lambda x: (size-32)/16, 0, self.parse_rect,
                          lambda i: i.SIZE)
  offset += rects.SIZE
  if offset - start != size:
   raise ValueError("malformed rect array")
  return self.rgndata(
   header_size, region_type, num_rects, buffer_size, bounds, rects, size
  )
 # ACS Image Info List
 def parse_acsimageinfo_list(self, offset, size, *_):
  ret = self.parse_list(offset, self.parse_ulong, 4,
                        self.parse_acsimageinfo, lambda i: i.SIZE)
  if ret.SIZE != size:
   raise ValueError("malformed acsimageinfo list")
  return ret
 def parse_acsimageinfo(self, offset):
  start = offset
  location = self.parse_acslocator(offset)
  offset += location.SIZE
  checksum_maybe = self.parse_ulong(offset)
  offset += 4
  imagedata = self.parse_acsimageinfo_data(*location)
  return self.acsimageinfo(...)
 def parse_acsimageinfo_data(self, offset, size, *_):
  start = offset
  unknown = self.parse_byte(offset)
  offset += 1
  width = self.parse_ushort(offset)
  height = self.parse_ushort(offset + 2)
  offset += 4
  compressed = bool(self.parse_byte(offset))
  offset += 1
  image_data = self.parse_datablock(offset)
  offset += image_data.SIZE
  if compressed:
   image_data = self.decompress(image_data)
  rgndata_size_compressed = self.parse_ulong(offset)
  rgndata_size_uncompressed = self.parse_ulong(offset + 4)
  offset += 8
  rgndata_compressed = bool(rgndata_size_compressed)
  rgndata_size = rgndata_size_compressed or rgndata_size_uncompressed
  rgndata = self.data[offset:offset+rgndata_size]
  if rgndata_compressed:
   rgndata = self.decompress(rgndata)
   rgndata_size = rgndata_size_uncompressed
  rgndata = ACSParser(rgndata).parse_rgndata(0, rgndata_size)
  if offset - start != size:
   raise ValueError("malformed acsimageinfo_data")
  return self.acsimageinfo_data(
   unknown, width, height, compressed, image_data, rgndata_size_compressed,
   rgndata_size_uncompressed, rgndata_size, rgndata,
  size)
 # Primitives
 def parse_byte(self, offset):
  return struct.unpack("<B", self.data[offset:offset+1])[0]
 def parse_long(self, offset):
  return struct.unpack("<l", self.data[offset:offset+4])[0]
 def parse_ulong(self, offset):
  return struct.unpack("<L", self.data[offset:offset+4])[0]
 def parse_short(self, offset):
  return struct.unpack("<h", self.data[offset:offset+2])[0]
 def parse_ushort(self, offset):
  return struct.unpack("<H", self.data[offset:offset+2])[0]
 def parse_wchar(self, offset):
  return struct.unpack("<h", self.data[offset:offset+2])[0]
 # Other common types
 def parse_datablock(self, offset):
  # (header--size in bytes) + 4 bytes in header
  size = self.parse_ulong(offset) + 4
  offset += 4
  return ACSDataBlock(self.data[offset:offset+size-4], size)
 def parse_guid(self, offset):
  return uuid.UUID(bytes_le=self.data[offset:offset+16])
 def parse_langid(self, offset):
  return self.parse_ushort(offset)
 def parse_rect(self, offset):
  top_left_x = self.parse_long(offset)
  top_left_y = self.parse_long(offset + 4)
  bottom_right_x = self.parse_long(offset + 8)
  bottom_right_y = self.parse_long(offset + 12)
  return self.rect(
   (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 16
  )
 def parse_rgbquad(self, offset):
  red = self.parse_byte(offset)
  green = self.parse_byte(offset + 1)
  blue = self.parse_byte(offset + 2)
  reserved = self.parse_byte(offset + 3)
  int_ = (red * 0x10000) + (green * 0x100) + blue
  hex_ = hex(red)[2:].zfill(2)+hex(green)[2:].zfill(2)+hex(blue)[2:].zfill(2)
  return self.rgbquad(red, green, blue, reserved, int_, hex_, 4)
 def parse_list(self, offset, count_parser, count_size,
                struct_parser, struct_size):
  start = offset
  size = count_parser(offset)
  if callable(count_size): count_size = count_size(size)
  offset += count_size
  ret = []
  if not callable(struct_size):
   self.check(offset, struct_size * size)
   struct_size_ = struct_size
   struct_size = lambda s: struct_size_
  n = 0
  while n < size:
   st = struct_parser(offset)
   ret.append(st)
   offset += struct_size(st)
   n += 1
  return ACSList(ret, offset - start)
 def parse_string(self, offset):
  num_chars = self.parse_ulong(offset)
  terminator_len = 2 if num_chars else 0
  offset += 4
  size = (num_chars * 2) + terminator_len + 4
  return ACSString(self.data[offset:offset+size-terminator_len-4], size)

class ACSDataBlock(bytes):
 def __new__(cls, data, size):
  return super(ACSDataBlock, cls).__new__(cls, data)
 def __init__(self, data, size):
  self.SIZE = size

class ACSDict(dict):
 def __new__(cls, iterable, size):
  return super(ACSDict, cls).__new__(cls, iterable)
 def __init__(self, iterable, size):
  self.update(iterable)
  self.SIZE = size

class ACSList(list):
 def __new__(cls, iterable, size):
  return super(ACSList, cls).__new__(cls, iterable)
 def __init__(self, iterable, size):
  self += iterable
  self.SIZE = size

class ACSString(unicode):
 def __new__(cls, data, size):
  return super(ACSString, cls).__new__(cls, data, "utf_16_le", "strict")
 def __init__(self, data, size):
  self.SIZE = size

def test(character="clippit"):
 return AgentCharacter(character + ".acs")

def testd(character="clippit"):
 with open(character + ".acs", "rb") as f:
  return f.read()
