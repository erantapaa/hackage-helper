import collections
from collections import namedtuple
import re

BuildError = namedtuple("BuildError", "kind args")

# MissingCLibrary = "MissingCLibrary"
# MissingCHeader = "MissingCHeader"

# NoSuchFile = "NoSuchFile"
# RequiredProgram = "RequiredProgram"
# ConfigureError = "ConfigureError"
# PkgConfigMissing = "PkgConfigMissing"

PkgConfigError  = namedtuple("PkgConfigError", "arg bounds")
MissingCLibrary = namedtuple('MissingCLibrary', "libs")
MissingCHeader  = namedtuple("MissingCHeader", "arg")
NoSuchFile      = namedtuple("NoSuchFile", "arg")
RequiredProgram = namedtuple("RequiredProgram", "arg")
ConfigureError  = namedtuple("ConfigureError", "arg")

def mkMissingCLibrary(args):
  libs = re.split(" *, *", args)
  return MissingCLibrary(libs = libs)

def mkMissingCHeader(arg):
  return MissingCHeader(arg)

def mkNoSuchFile(arg):
  return NoSuchFile(arg)

def mkRequiredProgram(arg):
  return RequiredProgram(arg)

def mkConfigureError(arg):
  return ConfigureError(arg)

def mkPkgConfigMissing(arg, bounds = None):
  return PkgConfigError(arg = arg, bounds = bounds)

