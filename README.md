
### Synopsis

```sh
$ stack build > out 2>&1 
$ ./analyze-log out
```

### Overview

`analyze-log` will parse the output produced by `stack build`
or `cabal build` looking for error messages referring to missing
libraries and return a list of packages which should resolve
those errors.

The file `all-rules` contains the knowledge base of errors and
which libraries they are associated with.

Currently it only knows about Ubuntu packages, but the capability
exists to add information about other packaging systems including
brew, macports and rpm-pbased systems.

Without any arguments `analyze-log` will read from stdin.
Otherwise it will process each file on the command line.

Note that if you run `stack install ...` outside of a stack work directory,
stack will save the build log files in the directory
`~/.stack/global-project/.stack-work/logs`, so this invocation
of `analyze-log` can be useful:

    analyze-log ~/.stack/global-project/.stack-work/logs/*

