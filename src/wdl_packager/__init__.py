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
    """
    Get protocol from a uri by splitting on the :// part.
    :param uri: The uri
    :return: The protocol (if any) else None
    """
    if "://" in uri:
        return uri.split("://")[0]
    else:
        return None


def wdl_paths(wdl: WDL.Tree.Document,
              start_path: Path = Path(),
              relative_to_path: Path = Path()
              ) -> Generator[Tuple[Path, Path], None, None]:
    """
    A generator that yields tuples with an absolute file path and the
    relative imports path.
    :param wdl: The WDL document
    :param start_path: relative path to start from.
    :param relative_to_path:
    :returns
    """
    protocol = get_protocol(wdl.pos.uri)
    if protocol == "file":
        uri = wdl.pos.uri.lstrip("file://")
    elif protocol is None:
        uri = wdl.pos.uri
    else:
        raise NotImplementedError(f"{protocol} is not implemented yet")

    wdl_path = (start_path / (Path(uri))).relative_to(relative_to_path)
    yield Path(wdl.pos.abspath), wdl_path

    import_start_path = wdl_path.parent
    for wdl_import in wdl.imports:  # type: WDL.Tree.DocImport
        wdl_doc = wdl_import.doc  # type: WDL.Tree.Document
        for file_path, rel_path in wdl_paths(wdl_doc, import_start_path):
            yield file_path, rel_path


def main():
    args = argument_parser().parse_args()
    wdl = WDL.load(args.wdl)
    print(wdl)

if __name__ == "__main__":
    main()

