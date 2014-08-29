#!/usr/bin/env python
import sys
import wave
import struct
import time
import itertools

def unpack_pcm(packed_values, sampwidth):
    if sampwidth == 2:
        return struct.unpack(str(len(packed_values)/sampwidth) + 'h', packed_values)
    elif sampwidth == 3:
        tmp = struct.unpack(str(len(packed_values)) + 'B', packed_values)
        tmp = [x + (y<<8) + (z<<16) for x,y,z in itertools.izip(*[iter(tmp)]*3)]
        return [x if (x & 0x800000) == 0 else x - (1<<24) for x in tmp]

def pack_pcm(values, sampwidth):
    if sampwidth == 2:
        return struct.pack(str(len(values)) + 'h', *values)
    elif sampwidth == 3:
        tmp = [k for j in itertools.imap(lambda i: (i & 0xff, (i>>8) & 0xff, (i>>16) & 0xff), values) for k in j]
        return struct.pack(str(len(values)*sampwidth) + 'B', *tmp)

def main(argv):
    if len(argv) < 4:
        print("Incorrect arguments")
        return 1

    inname1 = argv[1]
    inname2 = argv[2]
    outname = argv[3]

    in1 = wave.open(inname1, 'r')
    in2 = wave.open(inname2, 'r')

    param1 = in1.getparams()
    param2 = in2.getparams()

    if param1 != param2:
        print("Input files' parameters differ.")
        return 2

    print(time.time())

    packed_values1 = in1.readframes(param1[3])
    packed_values2 = in2.readframes(param1[3])

    values1 = unpack_pcm(packed_values1, param1[1])
    values2 = unpack_pcm(packed_values2, param2[1])
    outvalues = list(itertools.imap(lambda x,y: x - y, values1, values2))
    packed_outvalues = pack_pcm(outvalues, param1[1])

    out = wave.open(outname, 'w')
    out.setparams(param1)
    out.writeframesraw(packed_outvalues)
    out.close()

    print(time.time())

    in1.close()
    in2.close()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
