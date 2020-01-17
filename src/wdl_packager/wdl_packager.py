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
import os
import time
import warnings
import zipfile
from pathlib import Path
from typing import List, Optional, Set, Tuple

import WDL

from .git import get_commit_version, get_file_last_commit_timestamp
from .utils import create_timestamped_temp_copy, get_protocol, \
    resolve_path_naive
from .version import get_version


def _wdl_all_paths(wdl: WDL.Tree.Document,
                   start_path: Path = Path()) -> List[Tuple[Path, Path]]:
    """
    Return a list of all WDL files that are imported. The list contains
    tuples of absolute path on the filesystem and relative paths from the
    URI of the first WDL document.
    :param wdl: The WDL document
    :param start_path: relative path to start from.
    :return: A list of tuple(abspath, relpath)
    """
    path_list = []

    # Only file protocol is supported
    protocol = get_protocol(wdl.pos.uri)
    if protocol == "file":
        raise NotImplementedError("The 'file://' protocol is not usable for "
                                  "building portable WDLs. It can not be used "
                                  "in zips because zip paths are relative. "
                                  "See: "
                                  "https://github.com/openwdl/wdl/pull/349 "
                                  "for more information.")
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
            _wdl_all_paths(wdl_import.doc, import_start_path))
    return path_list


def wdl_paths(wdl_uri: str) -> List[Tuple[Path, Path]]:
    wdl_doc = WDL.load(wdl_uri)
    wdl_path = Path(wdl_uri)

    # Make sure the list only contains unique entries. Some WDL files import
    # the same wdl file and this wdl file will end up in the list multiple
    # times because of that. This needs to be corrected.
    unique_paths = set()  # type: Set[Path]
    unique_path_list = []
    for source, raw_destination in _wdl_all_paths(wdl_doc):  # type: Path, Path
        try:
            # If we load the wdl path with WDL.load it will use the path as
            # base URI. For example /home/user/workflows/workflow.wdl. All
            # paths will be resolved relative to that. So all paths in the zip
            # will start with /home/user/workflows. We can resolve this by
            # using relative_to.
            destination = raw_destination.relative_to(wdl_path.parent)
        except ValueError:  # Raised when path is not relative
            raise ValueError("Could not create import zip with sensible "
                             "paths. Are there parent file ('..') type "
                             "imports in the wdl?")
        if destination in unique_paths:
            continue
        else:
            unique_paths.add(destination)
            unique_path_list.append((source, destination))

    return unique_path_list


def create_zip_file(src_dest_list: List[Tuple[Path, Path]],
                    output_path: str,
                    use_git_timestamps: bool = False):
    if use_git_timestamps:
        if time.tzname[0] != "UTC":
            warnings.warn(f"Timezone '{time.tzname[0]}' is not 'UTC'. "
                          f"Setting this process's timezone to 'UTC' for "
                          f"reproducibility.")
            os.environ["TZ"] = "UTC"
            time.tzset()

    tempfiles = []
    with zipfile.ZipFile(output_path, "w") as archive:
        for src, dest in src_dest_list:
            if use_git_timestamps:
                timestamp = get_file_last_commit_timestamp(src)
                src_path = create_timestamped_temp_copy(src, timestamp)
                tempfiles.append(src_path)
            else:
                src_path = src
            archive.write(str(src_path), str(dest))
    for temp in tempfiles:
        os.remove(str(temp))


def package_wdl(wdl_path: Path, output_zip: str,
                use_git_timestamps: bool = False,
                additional_files: Optional[List[Path]] = None):

    zipfiles = wdl_paths(str(wdl_path))

    if additional_files is not None:
        for add_file in additional_files:
            add_file_path = Path(add_file)
            src = add_file_path.resolve()
            try:
                dest = src.relative_to(wdl_path.parent)
            except ValueError:
                # If not relative to the wdl we add it in the root of the zip
                dest = Path(add_file_path.name)
            zipfiles.append((src, dest))

    # Sort on the zip paths for reproducibility
    zipfiles.sort(key=lambda x: str(x[1]))
    create_zip_file(zipfiles, output_path=output_zip,
                    use_git_timestamps=use_git_timestamps)


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("wdl", metavar="WDL_FILE",
                        help="The WDL file that will be packaged.")
    parser.add_argument("-o", "--output", required=False,
                        help="The output zip file. By default uses the name "
                             "of the input. This overrides the git name "
                             "option.")
    parser.add_argument("--add", "--additional-file", required=False,
                        type=Path,
                        action="append", dest="additional_files")
    parser.add_argument("--use-git-version-name", action="store_true",
                        dest="use_git_name",
                        help="Use git describe to determine the name of the "
                             "zip.")
    parser.add_argument("--use-git-commit-timestamp", action="store_true",
                        dest="use_timestamp",
                        help="Use the git commit timestamp to timestamp all "
                             "the files in the zip.")
    parser.add_argument("--reproducible", action="store_true",
                        help="shorthand for --use-git-version-name and "
                             "--use-git-commit-timestamp")
    parser.add_argument("--version", action="version", version=get_version())
    return parser


def main():
    args = argument_parser().parse_args()

    # Make sure path to the wdl is resolved
    wdl_path = Path(args.wdl).resolve()

    if args.output is not None:
        output_path = args.output
    elif args.use_git_name or args.reproducible:
        output_path = (wdl_path.stem + "_" +
                       get_commit_version(wdl_path.parent) +
                       ".zip")
    else:
        # Create the by default package /bla/bla/my_workflow.wdl into
        # my_workflow.zip
        output_path = wdl_path.stem + ".zip"

    package_wdl(wdl_path,
                output_path,
                use_git_timestamps=(args.use_timestamp or args.reproducible),
                additional_files=args.additional_files)


if __name__ == "__main__":
    main()
