# -*- coding: utf-8 -*

import re
#   PID       Vss      Rss      Pss      Uss     Swap    PSwap    USwap    ZSwap  cmdline
# a = ' 1224  1229748K   85560K   47527K   41252K    6176K    2543K    2404K     732K  system_server'
a =  '4034  1360808K  160760K  111920K   97624K  com.android.incallui\r\n'

procrank = r'\s*(\d+)\s+(\d+)K\s+(\d+)K\s+(\d+)K\s+(\d+)K\s+(\d+)K\s+(\d+)K\s+(\d+)K\s+(\d+)K\s+(((/\w+)+)|(\w+)|((\w+.)+\w+))\s*.'

pattern = re.compile(procrank)

# info = pattern.match(a)
# if info:
#     print info.group(0)
#     print info.group(1)
#     print info.group(2)
#     print info.group(3)
#     print info.group(4)
#     print info.group(5)
#     print info.group(6)
# else:
#     print 'Not match'

