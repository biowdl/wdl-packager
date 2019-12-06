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
from typing import List, Optional, Set, Tuple

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


def resolve_path_naive(path: Path):
    """
    Path.resolve() uses CWD on relative paths. But this is not always
    desirable. This function solves "my_path/my_dir/../my_file" naively
    as "my_path/my_file". This is not correct if symlinks are involved so
    this function should be used when a naive implementation is desirable.
    :param path: The path to resolve
    :return: A resolved path
    """
    if path.is_absolute():  # resolve works fine in this case.
        return path.resolve()
    if ".." in path.parts:
        index = path.parts.index("..")
        if index == 0:
            raise ValueError(f"unknown parent for {path}")
        else:
            # Slice out the double dot and its parent.
            new_parts = path.parts[:index - 1] + path.parts[index + 1:]
            # Recursion which allows for checking multiple ".." parts.
            return resolve_path_naive(Path(*new_parts))
    else:
        return path


def wdl_paths(wdl: WDL.Tree.Document,
              start_path: Path = Path(),
              unique: bool = True) -> List[Tuple[Path, Path]]:
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
        # Assume for now there is now host in the protocol string.
        # https://en.wikipedia.org/wiki/File_URI_scheme
        uri = wdl.pos.uri.lstrip("file:///")
    elif protocol is None:
        uri = wdl.pos.uri
    else:
        raise NotImplementedError(f"{protocol} is not implemented yet")

    try:
        # If .. is in the path we have a problem. This can be fixed by
        # resolving it.
        wdl_path = resolve_path_naive(start_path / Path(uri))
    except ValueError:
        raise ValueError(f"'..' was found in the import path "
                         f"'{uri}' and could not be resolved.")
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
    unique_paths = set()  # type: Set[Path]
    unique_path_list = []
    for abspath, relpath in path_list:  # type: Path, Path
        if relpath in unique_paths:
            continue
        else:
            unique_paths.add(relpath)
            unique_path_list.append((abspath, relpath))

    return unique_path_list


def package_wdl(wdl_uri: str, output_zip: str):
    wdl_doc = WDL.load(wdl_uri)
    wdl_path = Path(wdl_uri)
    with zipfile.ZipFile(output_zip, "w") as archive:
        for abspath, relpath in wdl_paths(wdl_doc):
            # If we load the wdl path with WDL.load it will use the path as
            # base URI. For example /home/user/workflows/workflow.wdl. All
            # paths will be resolved relative to that. So all paths in the zip
            # will start with /home/user/workflows. We can resolve this by
            # using relative_to.
            try:
                zip_path = relpath.relative_to(wdl_path.parent)
            except ValueError:
                raise ValueError("Could not create import zip with sensible "
                                 "paths. Are there parent file ('..') type "
                                 "imports in the wdl?")
            archive.write(str(abspath), str(zip_path))


def main():
    args = argument_parser().parse_args()

    # Create the by default package /bla/bla/my_workflow.wdl into
    # my_workflow.zip
    output_path = args.output or Path(args.wdl).stem + ".zip"
    package_wdl(args.wdl, output_path)


if __name__ == "__main__":
    main()
