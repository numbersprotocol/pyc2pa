import re
import sys


img = sys.argv[1]

f = open(img, 'rb').read()

marker = b'\xff\xeb'

offsets = [m.start() for m in re.finditer(marker, f)]

final_lbox = 0
for offset in offsets:
    Le = int.from_bytes(f[offset + 2: offset + 4], byteorder='big')
    En = int.from_bytes(f[offset + 6: offset + 8], byteorder='big')
    Z = int.from_bytes(f[offset + 8: offset + 12], byteorder='big')
    LBox = int.from_bytes(f[offset + 12: offset + 16], byteorder='big')

    print('# Offset: {0}, Le: {1}, En: {2}, Z (seq): {3}, LBox: {4}'.format(
        offset, Le, En, Z, LBox))

    if Le > 10:
        final_lbox += Le - 18  # header (10) + LBox (4) + TBox (4)

final_lbox += 8  # final payload box = LBox (4) + TBox (4) + Payload
print('# Final LBox: {} (should be the same as LBox)'.format(final_lbox))
