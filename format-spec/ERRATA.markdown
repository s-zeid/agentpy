MS Agent Character Data Specification 1.3 Errata
================================================
by [Scott Zeid](http://srwz.us/)

[Original spec](http://www.lebeausoftware.org/download.aspx?ID=25001fc7-18e9-49a4-90dc-21e8ff46aa1d),
[mirror](http://uploads.srwz.us/ms-agent-format-spec.html)

[GUID](http://uploads.srwz.us/ms-agent-format-spec.html#GUID)
-------------------------------------------------------------
The GUID structure is actually a ULONG, **USHORT (not another ULONG)**, USHORT,
and 8 BYTEs.  As a result, the structure is 16 bytes long, and not 18.  This
problem appears to be a typo, and the correct information appears on
[Wikipedia](http://en.wikipedia.org/wiki/GUID) and in the docs for
[Python's uuid module](http://docs.python.org/library/uuid.html).

[Compression Algorithim](http://uploads.srwz.us/ms-agent-format-spec.html#Compression)
--------------------------------------------------------------------------------------
In the compression algorithim, where it says:

    If the value bit count is 20 bits and the numeric value is 0x000FFFFF
    before adding 4673, the end of the bit stream has been reached. Otherwise,
    increment the count of BYTEs to be decoded by 1 and continue with the next
    steps:

**ONLY** add 1 to the decoded byte count if the bit count is 20 bits.

The first byte (that's "always 0x00") is not to be included when reading the
compressed data.  It seems to not matter if you include the last six bytes
("\xFF\xFF\xFF") because part of the algorithim detects these bytes.

[ACSCHARACTERINFO](http://uploads.srwz.us/ms-agent-format-spec.html#ACSCHARACTERINFO)
-------------------------------------------------------------------------------------
Bit 4 of the Flags ULONG in ACSCHARACTERINFO appears to specify whether voice
output is **DISABLED**, rather than *enabled*; i.e. set to 1 to **disable**
voice output.  Bit 5 *might* specify whether it's enabled, judging from the
fact that bits 8 and 9 correspond to word balloon disable/enable, but this is
pure speculation.
