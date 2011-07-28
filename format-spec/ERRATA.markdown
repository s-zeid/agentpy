The GUID structure is actually a ULONG, **USHORT (not another ULONG)**, USHORT,
and 8 BYTEs.  As a result, the structure is 16 bytes long, and not 18.  This
problem appears to be a typo, and the correct information appears on
[Wikipedia](http://en.wikipedia.org/wiki/GUID) and in the docs for
[Python's uuid module](http://docs.python.org/library/uuid.html).

Bit 4 of the ACSCHARACTERINFO Flags ULONG appears to specify whether voice
output is **DISABLED**, rather than *enabled*; i.e. set to 1 to **disable**
voice output.  Bit 5 *might* specify whether it's enabled, judging from the
fact that bits 8 and 9 correspond to word balloon disable/enable, but this is
pure speculation.
