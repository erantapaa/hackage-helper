import collections

BuildError = collections.namedtuple("BuildError", "kind args")

MissingCLibrary = "MissingCLibrary"
MissingCHeader = "MissingCHeader"
NoSuchFile = "NoSuchFile"
CheckingFor = "CheckingFor"
RequiredProgram = "RequiredProgram"
ConfigureError = "ConfigureError"
PkgConfigMissing = "PkgConfigMissing"

PkgConfigError = collections.namedtuple("PkgConfigError", "kind args bounds")

def mkMissingCLibrary(args):
  return BuildError(kind = MissingCLibrary, args = args)

def mkMissingCHeader(args):
  return BuildError(kind = MissingCHeader, args = args)

def mkNoSuchFile(args):
  return BuildError(kind = NoSuchFile, args = args)

def mkCheckinFor(args):
  return BuildError(kind = CheckingFor, args = args)

def mkRequiredProgram(args):
  return BuildError(kind = RequiredProgram, args = args)

def mkConfigureError(args):
  return BuildError(kind = ConfigureError, args = args)

def mkPkgConfigMissing(args, bounds = None):
  return PkgConfigError(kind = PkgConfigMissing, args = args, bounds = bounds)

