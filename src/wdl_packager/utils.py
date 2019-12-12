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

import os
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

from .git import get_file_last_commit_timestamp


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


def create_timestamped_temp_copy(original_file: Path, timestamp: int) -> Path:
    temp_handle, temp_path = tempfile.mkstemp()
    Path(temp_path).write_bytes(original_file.read_bytes())
    os.utime(temp_path, (timestamp, timestamp))
    return Path(temp_path)


def create_zip_file(src_dest_list: List[Tuple[Path, Path]],
                    output_path: str,
                    use_git_timestamps: bool = False):
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
