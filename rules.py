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

class OrClause():
  def __init__(self, children):
    self.children = children

  def check(self, error):
    for c in self.children:
      if c.check(error): return True
    return False

  def __str__(self):
    return "OrClause(" + ', '.join([ str(c) for c in self.children ]) + ")"

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

class CHeaderRule(BaseRule):
  def __init__(self, doth):
    self.doth = doth

  def matches(self, error):
    return self.doth.matches( error.arg )

  def error_classes(self):
    return [ "MissingCHeader" ]

  def __str__(self):
    return "CHeaderRule(" + str(self.doth) + ")"

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

  m = re.match("dot-h\s+(\S+)", s)
  if m:
    return CHeaderRule( Equals(m.group(1)) )

  return None

PackageSpec = collections.namedtuple("PackageSpec", "suite pkgname")

def die(msg):
  sys.stderr.write(msg + "\n")
  sys.exit(1)

def syntax_error(msg, t):
  die( "syntax error line {}: {}\n{}".format(t.pos, msg, t.content) )

def parse_clauses(it, t):
  r = parse_rule(t.content)
  if not r:
    syntax_error("rule expected", t)
  rs = [ r ]
  while True:
    t = next(it, None)
    if t is None: break
    r = parse_rule(t.content)
    if not r: break
    rs.append(r)
  return (rs, t)

def parse_spec(x):
  m = re.match("\s*-\s+(?:(\S+):\s*)?(\S+)", x)
  if m:
    if m.group(1):
      suite = m.group(1)
    else:
      suite = None
    return PackageSpec( suite = suite, pkgname = m.group(2) )

def parse_pkgspecs(it, t):
  specs = []
  while t != None:
    s = parse_spec(t.content)
    if s is None: break
    specs.append(s)
    t = next(it, None)
  return (specs, t)

SourceLine = collections.namedtuple("SourceLine", "content pos")

Stanza = collections.namedtuple("Stanza", "clauses pkgspecs")

def remove_comments(lines):
  for i, x in enumerate(lines):
    if re.match("\s*(#.*)?\Z", x, re.S):
      continue
    yield SourceLine(content = x, pos = i)
  yield None

def parse_rules(lines):
  it = remove_comments(lines)
  t = next(it, None)

  stanzas = []

  while t:
    clauses, t = parse_clauses(it, t)
    specs, t = parse_pkgspecs(it, t)
    if len(clauses) > 1:
      stanza = Stanza( clauses=OrClause(clauses), pkgspecs=specs )
    else:
      stanza = Stanza( clauses=clauses[0], pkgspecs=specs )
    stanzas.append(stanza)
  return stanzas

def test_comments():
  lines = """

# foo
  a

        
b
   #   
   c
""".split("\n")
  it = remove_comments(lines)
  for t in it:
    print t

