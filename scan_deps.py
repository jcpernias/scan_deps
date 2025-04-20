#!/usr/bin/env python3

import re
import os

class GretlScanner:
    """Search a Gretl script for dependencies"""
    GRETL_PATTERN = re.compile(r'''
    ^\s*                        # Allow spaces
    (?:set\s+(workdir)|(open)|(outfile)|(gnuplot)) # Command
    \s+                         # Some spaces
    (?:(?(4).*--output=))       # gnuplot extras
    (?:"([^"\n]+)"|([^"\s]+)    # name without quotes
    (?:\s|$))                   # a space or end of line
    ''', re.X)

    def __init__(self, source):
        self.source = source
        self.workdir = ""
        self.datafiles = set()
        self.outfiles = set()
        self.figfiles = set()

    def lines(self):
        result = ''
        while True:
            try:
                line = next(self.source)
            except StopIteration:
                return

            # Remove line comments
            maybe_cont = True
            parts = line.split('#', maxsplit = 1)
            if len(parts) != 1:
                line = parts[0]  # Drop comments
                maybe_cont = False # No continuation if there are comments

            # Strip trailing spaces
            line = line.rstrip()

            # Check continuation line char
            if not maybe_cont or not len(line) or line[-1] != '\\':
                result += line
                yield result
                result = ''
            else:
                result += line[:-1]

    def parse_line(self, line):
        mobj = GretlScanner.GRETL_PATTERN.match(line)
        if mobj is None:
            return (None, None)
        return tuple(x for x in mobj.groups() if x is not None)

    def norm_path(self, path):
        return os.path.normpath(os.path.join(self.workdir, path))

    def parse(self):
        for line in self.lines():
            match self.parse_line(line):
                case ('workdir', path):
                    self.workdir = path
                case ('open', path):
                    self.datafiles.add(self.norm_path(path))
                case ('outfile', path):
                    self.outfiles.add(self.norm_path(path))
                case ('gnuplot', path):
                    self.figfiles.add(self.norm_path(path))
        return self


def main():
    print("Done.\n")

if __name__ == '__main__':
    main()

#  LocalWords:  workdir outfile gnuplot
