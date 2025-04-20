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
    (?:"([^"]+)"|([^"\s]+)      # name without quotes
    (?:\s|$))                   # a space or end of line
    ''', re.X)

    COMMENT_PATTERN = re.compile(r'''
    ("[^"]*")|                  # String
    (/\*(?:[^*]|\*(?!/))*\*/)|  # Delimited comment
    (\#.*$)                     # Line comment
    ''', re.X)
    def __init__(self, source):
        self.source = source
        self.workdir = ""
        self.datafiles = set()
        self.outfiles = set()
        self.figfiles = set()

    def delete_comments(self, line):
        start = 0
        end = 0
        parts = []
        while True:
            mobj = GretlScanner.COMMENT_PATTERN.search(line, start)
            if not mobj:
                parts.append(line[start:])
                break
            if mobj[1]:
                end = mobj.end()
                parts.append(line[start:end])
                start = end
            elif mobj[2]:
                end = mobj.start()
                parts.append(line[start:end])
                start = mobj.end()
            elif mobj[3]:
                end = mobj.start()
                parts.append(line[start:end])
                return (' '.join(parts), False)

        line = ' '.join(parts).rstrip()
        line_cont = len(line) and line[-1] == '\\'
        if line_cont:
            line = line[:-1] + ' '
        return (line, line_cont)

    def lines(self):
        result = ''
        while True:
            try:
                line = next(self.source)
            except StopIteration:
                return

            # Remove line comments
            line, line_cont = self.delete_comments(line)
            result += line

            # Check continuation line char
            if not line_cont:
                yield result
                result = ''

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
