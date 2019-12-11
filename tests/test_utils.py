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
from pathlib import Path
import pytest

from wdl_packager.utils import create_timestamped_temp_copy, \
    get_protocol, resolve_path_naive

PROTOCOL_TEST = [
    ("/bla/bla/bladiebla", None),
    ("http://github.com", "http"),
    ("file:///blabla/bla", "file"),
    ("sqlalchemy+psycopg2:///mydatabase?bla", "sqlalchemy+psycopg2")
]


@pytest.mark.parametrize(["uri", "result"], PROTOCOL_TEST)
def test_get_protocol(uri, result):
    assert get_protocol(uri) == result


DOTTED_URIS = [
    (Path("bla/../bla"), Path("bla")),
    (Path("/bla/../../../usr/lib"), Path("/usr/lib")),
    (Path("my_wdl/tasks/biopet/../common.wdl"),
     Path("my_wdl/tasks/common.wdl")),
    (Path("multiple/../dots/../detected"), Path("detected")),
]

UNRESOLVABLE_DOTTED_URIS = [
     Path("../my_import.wdl"),
     Path("tasks/../../my_import.wdl"),
     Path("seemingly/fine/../but/../too/many/dots/../../../../../indeed")
]


@pytest.mark.parametrize(["uri", "result"], DOTTED_URIS)
def test_resolve_path_naive(uri, result):
    assert resolve_path_naive(uri) == result


@pytest.mark.parametrize("uri", UNRESOLVABLE_DOTTED_URIS)
def test_resolve_path_naive_unsolvable(uri):
    with pytest.raises(ValueError) as e:
        resolve_path_naive(uri)
    assert e.match("unknown parent")


def test_create_timestamped_tempfile():
    timestamp=10
    temp_handle, temp_file = tempfile.mkstemp()
    timestamped_copy = create_timestamped_temp_copy(Path(temp_file), timestamp)
    assert timestamped_copy.stat().st_mtime == timestamp
    os.remove(temp_file)
    os.remove(str(timestamped_copy))
