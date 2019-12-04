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
from typing import List, Optional, Tuple

import os

import WDL


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("wdl", metavar="WDL_FILE",
                        help="The WDL file that will be packaged.")
    parser.add_argument("-o", "--output", required=False,
                        help="The output zip file. By default uses the name "
                             "of the input.")
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
              unique = True) -> List[Tuple[Path, Path]]:
    """
    Return a list of all WDL files that are imported. The list contains
    tuples of absolute path on the filesystem and relative paths from the
    URI of the first WDL document.
    :param wdl: The WDL document
    :param start_path: relative path to start from.
    :param unique: Only return unique paths
    :return: A list of tuple(abspath, relpath)
    """
    path_list = []

    # Only file protocol is supported
    protocol = get_protocol(wdl.pos.uri)
    if protocol == "file":
        uri = wdl.pos.uri.lstrip("file://")
    elif protocol is None:
        uri = wdl.pos.uri
    else:
        raise NotImplementedError(f"{protocol} is not implemented yet")

    wdl_path = start_path / Path(uri)
    path_list.append((Path(wdl.pos.abspath), wdl_path))

    # Recursively use the function for imports as well.
    import_start_path = wdl_path.parent
    for wdl_import in wdl.imports:
        path_list.extend(
            # Uniqueness checking not done for each recursion
            wdl_paths(wdl_import.doc, import_start_path, unique=False))

    if not unique:
        return path_list

    # Make sure the list only contains unique entries. Some WDL files import
    # the same wdl file and this wdl file will end up in the list multiple
    # times because of that. This needs to be corrected.
    resolved_unique_paths = set()
    unique_path_list = []
    for abspath, relpath in path_list:
        # We need to resolve the path. Some paths have bla/../bla.wdl these
        # .. paths are removed by resolving. (The resolved path does not make
        # sense as it is resolved relative to pwd but that does not matter,
        # since we use it for uniqueness only.
        resolved_path = relpath.resolve()
        if resolved_path in resolved_unique_paths:
            continue
        else:
            resolved_unique_paths.add(resolved_path)
            unique_path_list.append((abspath, relpath))

    return unique_path_list


def main():
    args = argument_parser().parse_args()
    wdl_path = Path(args.wdl)

    # If we load the wdl path with WDL.load it will use the path as base URI
    # For example /home/user/workflows/workflow.wdl. All paths will be resolved
    # relative to that. So all paths in the zip will start with
    # /home/user/workflows. To work around this we go to the parent directory
    # /home/user/workflows and we load the WDL there. We go back to the
    # original cwd in the end, otherwise the output path does not make sense.
    cwd = os.getcwd()
    base_uri = wdl_path.name
    os.chdir(wdl_path.parent)
    wdl_doc = WDL.load(base_uri)
    os.chdir(cwd)

    # Create the by default package /bla/bla/my_workflow.wdl into
    # my_workflow.zip
    output_path = args.output or wdl_path.stem + "_imports.zip"

    with zipfile.ZipFile(output_path, "w") as archive:
        for abspath, relpath in wdl_paths(wdl_doc):
            archive.write(str(abspath), str(relpath))


if __name__ == "__main__":
    main()

