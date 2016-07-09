
from builderrors import *

import re

def parse_errors(inp, errors):
  for x in inp:

    m = re.match("\* Missing C library:\s*(\S+)", x)
    if m:
      errors.append( mkMissingCLibrary(m.group(1)) )
      continue

    m = re.match("\* Missing C libraries:\s*(.*)", x)
    if m:
      errors.append( mkMissingCLibrary( m.group(1) ) )
      continue
 
    m = re.match("\* Missing .or bad. header file:\s*(\S+)", x)
    if m:
      errors.append( mkMissingCHeader(m.group(1)) )
      continue

    m = re.match("setup: The program '(.*?)' is required but", x)
    if m:
      errors.append( mkRequiredProgram( m.group(1) ) )
      continue

    m = re.match("configure: error:\s*(\S.*?), so this package cannot be built", x)
    if m:
      errors.append( mkConfigureError( m.group(1) ) )
      continue

    m = re.match("configure: error:\s*(\S.*?) is required", x)
    if m:
      errors.append( mkConfigureError( m.group(1) ) )
      continue

    m = re.match(".*?: fatal error: (.*): No such file or directory", x)
    if m:
      errors.append( mkNoSuchFile( m.group(1) ) )
      continue

# configure: error: readline not found, so this package cannot be built

# qDM57kQSPo1mKx/include/HsUnix.h:79:25: fatal error: bsd/libutil.h: No such file or d

def parse_multiline_errors(content, errors):

  for m in re.finditer("^setup.*?: The pkg-config package '(.*?)'\s+is\s+required\s+but\s+it\s+could\s+not\s+be\s+found", content, re.M):
    errors.append( mkPkgConfigMissing( m.group(1) ) )

  for m in re.finditer("^setup.*?: The pkg-config package '(.*?)'\s+version\s+(.*?)\s+is\s+required\s+but\s+it\s+could\s+not\s+be\s+found", content, re.M):
    errors.append( mkPkgConfigMissing( m.group(1), bounds= m.group(2) ) )

"""
setup-Simple-Cabal-1.22.5.0-ghc-7.10.3: The pkg-config package 'fftw3f'
version >=3.3 && <4 is required but it could not be found.
"""
