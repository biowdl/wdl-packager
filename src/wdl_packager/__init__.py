# Copyright (c) 2019 Leiden University Medical Center
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import zipfile
from pathlib import Path
from typing import Generator, Optional, Tuple

import WDL


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("wdl", metavar="WDL_FILE",
                        help="The WDL file that will be packaged.")
    parser.add_argument("-o", "--output", required=False,
                        help="The output zip file. By default uses the name "
                             "of the input")
    return parser


def get_protocol(uri: str) -> Optional[str]:
    if "://" in uri:
        return uri.split("://")[0]
    else:
        return None


def wdl_paths(wdl: WDL.Tree.Document, start_path= Path()) -> Generator[Tuple[Path, Path], None, None]:
    protocol = get_protocol(wdl.pos.uri)
    if protocol == "file":
        uri = wdl.pos.uri.lstrip("file://")
    elif protocol is None:
        uri = wdl.pos.uri
    else:
        raise NotImplementedError(f"{protocol} is not implemented yet")
    rel_path = start_path / Path(uri).name
def main():
    args = argument_parser().parse_args()
    wdl = WDL.load(args.wdl)
    print(wdl)

if __name__ == "__main__":
    main()

