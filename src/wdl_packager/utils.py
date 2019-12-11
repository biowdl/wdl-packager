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

from pathlib import Path
from typing import Optional


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