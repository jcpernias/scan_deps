import scan_deps

import io
from collections import deque


def test_simple():
    in_lines = '''
    set workdir ./build
    open ../data/data.csv
    outfile out.txt
      ols x 0 y
    end outfile
    gnuplot x y --output=fig.pdf
    set workdir "./test"
    open "../data/data2.csv"
    outfile "out.txt"
      ols x 0 y
    end outfile
    gnuplot x y --output="fig.pdf"
    '''
    test_in = io.StringIO(in_lines)
    scanner = scan_deps.GretlScanner(test_in).parse()

    assert scanner.datafiles == { 'data/data.csv', 'data/data2.csv' }
    assert scanner.outfiles == { 'build/out.txt', 'test/out.txt' }
    assert scanner.figfiles == { 'build/fig.pdf', 'test/fig.pdf' }


def test_cont_lines():
    in_lines = '''
    set \\
      workdir \\
      ./build
    open \\
      ../data/data.csv
    outfile out.txt
      ols x 0 y
    end outfile
    gnuplot x y \\
       --output=fig.pdf
    '''
    test_in = io.StringIO(in_lines)
    scanner = scan_deps.GretlScanner(test_in).parse()

    assert scanner.workdir == './build'
    assert scanner.datafiles == { 'data/data.csv' }
    assert scanner.outfiles == { 'build/out.txt' }
    assert scanner.figfiles == { 'build/fig.pdf' }

def test_line_comments():
    in_lines = '''
    set workdir ./build # Comment
    open ../data/data.csv # Another comment
    outfile out.txt
    # ols x 0 y
    end outfile # \\
    gnuplot x y --output=fig.pdf
    '''
    test_in = io.StringIO(in_lines)
    scanner = scan_deps.GretlScanner(test_in).parse()

    assert scanner.workdir == './build'
    assert scanner.datafiles == { 'data/data.csv' }
    assert scanner.outfiles == { 'build/out.txt' }
    assert scanner.figfiles == { 'build/fig.pdf' }


def test_comments():
    in_lines = '''
    set workdir "./#build"
    '''
    test_in = io.StringIO(in_lines)
    scanner = scan_deps.GretlScanner(test_in).parse()

    assert scanner.workdir == './#build'



# Local Variables:
# eval: (flyspell-mode -1)
# End:
