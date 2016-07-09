import collections
import re
import sys

class Any():
  def __init__(self):
    pass
  def matches(self, v):
    return True

  def __str__(self):
    return "Any"

class Equals():
  def __init__(self, val):
    self.val = val

  def matches(self, v):
    return self.val == v

  def __str__(self):
    return "Equals(" + str(self.val) + ")"

class MatchesRegex():
  def __init__(self, regex):
    self.regex = regex

  def matches(self, v):
    return bool( re.match(self.regex, v) )

  def __str__(self):
    return "MatchesRegex(" + str(self.regex) + ")"

class IsMember():
  def __init__(self, member):
    self.needed = member

  def matches(self, v):
    return self.needed in v

  def __str__(self):
    return "IsMember(" + str(self.needed) + ")"

class BaseRule():
  def __init__(self):
    pass

  def check(self, error):
    return error.type in self.error_classes() and self.matches(error)

class LibRule(BaseRule):
  def __init__(self, lib):
    self.needed = lib

  def matches(self, error):
    return self.needed in error.libs

  def error_classes(self):
    return [ "MissingCLibrary" ]

  def __str__(self):
    return "LibRule(" + str(self.needed) + ")"

class ProgramRule(BaseRule):
  def __init__(self, pat):
    self.prog_pat = pat

  def matches(self, error):
    return self.prog_pat.matches(error.arg)

  def error_classes(self):
    return ["RequiredProgram"]

  def __str__(self):
    return "ProgramRule(" + str(self.prog_pat) + ")"

class ConfigureRule(BaseRule):
  def __init__(self, config_pat):
    self.config_pat = config_pat

  def matches(self, error):
    return self.config_pat.matches(error.arg)

  def error_classes(self):
    return ["ConfigureError"]

  def __str__(self):
    return "ConfigureRule(" + str(self.config_pat) + ")"

class PkgConfigRule(BaseRule):
  def __init__(self, pkg_pat, bounds_pat):
    self.pkg_pat = pkg_pat
    self.bounds_pat = bounds_pat

  def matches(self, error):
    return self.pkg_pat.matches(error.arg) and self.bounds_pat.matches(error.bounds)

  def error_classes(self):
    return ["PkgConfigError"]

  def __str__(self):
    return "PkgConfigRule(" + str(self.pkg_pat) + ")"

class NoSuchFileRule(BaseRule):
  def __init__(self, file_pat):
    self.file_pat = file_pat

  def matches(self, error):
    return self.file_pat.matches(error.arg)

  def error_classes(self):
    return ["NoSuchFile"]

  def __str__(self):
    return "NoSuchFileRule(" + str(self.file_pat) + ")"

# lib text
#  - package
#  - xenial: ...
#
# prog text
#  - ...
#  occurs in: ...
#
# configure (text | regex)
#  - ...
# pkgconfig ... (bounds)
#
# file ...

TOKEN_RE = r"(?:('(.*)')|(\"(.*)\")|(\S+))"

def extract_token(m, i):
  if not m:
    return None
  if m.group(i+0):
    return m.group(i+1)
  if m.group(i+2):
    return m.group(i+3)
  return m.group(i+4)

def parse_rule(s):
  m = re.match("lib\s+(\S+)", s)
  if m:
    return LibRule( m.group(1) )

  m = re.match("program\s+(?:('(.*)')|(\"(.*)\")|(\S+))", s)
  arg = extract_token(m, 1)
  if arg is not None:
    return ProgramRule( Equals( arg ) )

  m = re.match("configure\s+(?:('(.*)')|(\"(.*)\")|(\S+))", s)
  arg = extract_token(m, 1)
  if arg is not None:
    return ConfigureRule( Equals( arg ) )

  m = re.match("pkgconfig\s+(\S+)(\s+'(.*?)')?", s)
  if m:
    if m.group(2):
      bounds_pat = Equals(m.group(2))
    else:
      bounds_pat = Any()
    return PkgConfigRule( Equals(m.group(1)), bounds_pat)

  m = re.match("file\s+(\S+)", s)
  if m:
    return NoSuchFileRule( Equals(m.group(1)) )

  return None

PackageSpec = collections.namedtuple("PackageSpec", "suite pkgname")

def die(msg):
  sys.stderr.write(msg + "\n")
  sys.exit(1)

def parse_rules(lines):
  rs = []
  i = 0
  while i < len(lines):
    x = lines[i]
    i += 1
    if re.match("\s*(#.*)?\Z", x):
      continue
    r = parse_rule(x)
    if not r:
      die("syntax error on line", i)
    # collect the pkg specs
    specs = []
    while i < len(lines):
      x = lines[i]
      i += 1
      if re.match("\s*(#.*)?\Z", x): continue
      m = re.match("\s*-\s*((\S+):\s+)?(\S+)", x)
      if m:
        specs.append( PackageSpec(pkgname = m.group(3), suite = m.group(2)) )
      else:
        i -= 1
        break
    rs.append( (r, specs) )
  return rs

