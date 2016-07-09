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
PkgConfigError.type = "PkgConfigError"

MissingCLibrary = namedtuple('MissingCLibrary', "libs")
MissingCLibrary.type = "MissingCLibrary"

MissingCHeader  = namedtuple("MissingCHeader", "arg")
MissingCHeader.type = "MissingCHeader"

NoSuchFile      = namedtuple("NoSuchFile", "arg")
NoSuchFile.type = "NoSuchFile"

RequiredProgram = namedtuple("RequiredProgram", "arg")
RequiredProgram.type = "RequiredProgram"

ConfigureError  = namedtuple("ConfigureError", "arg")
ConfigureError.type = "ConfigureError"

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

