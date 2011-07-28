The GUID structure is actually a ULONG, USHORT (not another ULONG), USHORT,
and 8 bytes.  As a result, the structure is 16 bytes long.  This appears to be
a typo, and the correct information appears on [Wikipedia]
(http://en.wikipedia.org/wiki/UUID) and in the docs for
[Python's uuid module](http://docs.python.org/library/uuid.html).

Bit 4 of the ACSCHARACTERINFO flags ulong appears to specify whether voice
output is **DISABLED**, not *enabled*; i.e. set to 1 to **disable** voice
output.  Bit 5 *might* specify whether it's enabled, judging from the fact
that bits 8 and 9 correspond to word balloon enable/disable.
